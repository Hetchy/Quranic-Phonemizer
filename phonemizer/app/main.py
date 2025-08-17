from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

import json
import yaml
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from core.phonemizer import Phonemizer


APP_DIR = Path(__file__).resolve().parent

def _find_resources_dir(start: Path) -> Path:
    """Find the project's resources directory by walking up parents.

    This is resilient to the app living under different nesting levels.
    """
    for up in [start, start.parent, start.parent.parent, start.parent.parent.parent]:
        candidate = up.parent / "resources" if (up / "app").exists() else up / "resources"
        if (candidate / "surah_info.json").exists():
            return candidate
    # Fallback to original expectation
    return (start.parents[1] / "resources")

RESOURCES_DIR = _find_resources_dir(APP_DIR)


class PhonemizeRequest(BaseModel):
    ref: str
    stops: List[str] = []
    newline_mode: str = "verse"  # "verse" | "word"

class ExportRequest(BaseModel):
    ref: str
    stops: List[str] = []
    fmt: str  # "json" | "csv"
    split: str = "word"  # "word" | "verse" | "both"


def _load_surah_info() -> Dict[str, Any]:
    with (RESOURCES_DIR / "surah_info.json").open(encoding="utf-8") as fh:
        return json.load(fh)


def _load_stop_signs() -> Dict[str, Dict[str, str]]:
    """Return mapping of lowercase stop keys to their symbol char and label.

    Only include the stop types that are usable as boundaries in Phonemizer,
    excluding the prohibited stop from the selectable list.
    """
    with (RESOURCES_DIR / "base_phonemes.yaml").open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh)

    out: Dict[str, Dict[str, str]] = {}
    stop_signs: Dict[str, Dict[str, str]] = data.get("stop_signs", {})
    for upper_key, info in stop_signs.items():
        lower = upper_key.lower()
        # Only consider those supported by the phonemizer as boundaries
        if lower in {"preferred_continue", "preferred_stop", "optional_stop", "compulsory_stop", "prohibited_stop"}:
            out[lower] = {
                "symbol": info.get("char", ""),
                "label": lower.replace("_", " ").capitalize(),
            }
    return out


pm = Phonemizer()
SURAH_INFO = _load_surah_info()
STOP_SIGNS = _load_stop_signs()

app = FastAPI(title="Qurʾānic Phonemizer App", version="1.0")


# Static files (frontend)
app.mount("/static", StaticFiles(directory=str(APP_DIR / "static")), name="static")


@app.get("/")
def index() -> FileResponse:
    return FileResponse(str(APP_DIR / "static" / "index.html"))


# Favicon endpoints (serve PNG as favicon)
@app.get("/favicon.ico")
def favicon_ico() -> FileResponse:
    # Many browsers request /favicon.ico; serve the PNG icon
    alt = APP_DIR / "static" / "icon.png"
    path = alt if alt.exists() else (APP_DIR / "static" / "icon.png")
    return FileResponse(str(path), media_type="image/png")


@app.get("/icon.png")
def icon_png() -> FileResponse:
    alt = APP_DIR / "static" / "icon.png"
    path = alt if alt.exists() else (APP_DIR / "static" / "icon.png")
    return FileResponse(str(path), media_type="image/png")


@app.get("/api/meta")
def get_meta() -> Dict[str, Any]:
    # Build surah list with id and names
    surahs: List[Dict[str, Any]] = []
    for sid_str, sdata in SURAH_INFO.items():
        surahs.append({
            "id": int(sid_str),
            "name_en": sdata.get("name_en", str(sid_str)),
            "name_ar": sdata.get("name_ar", ""),
            "num_verses": sdata.get("num_verses", 0),
            "verses": sdata.get("verses", []),  # each has verse + num_words
        })
    surahs.sort(key=lambda x: x["id"])

    # Build stops list excluding prohibited for selection
    stops: List[Dict[str, Any]] = []
    for key in ["preferred_continue", "preferred_stop", "optional_stop", "compulsory_stop"]:
        if key in STOP_SIGNS:
            stops.append({
                "key": key,
                "label": STOP_SIGNS[key]["label"],
                "symbol": STOP_SIGNS[key]["symbol"],
                "default": True if key == "compulsory_stop" else False,
            })

    return {
        "surahs": surahs,
        "stops": stops,
        # Expose what the backend accepts for validation in the UI if needed
        "valid_stop_keys": sorted(pm.valid_stops),
        # Default selection state
        "defaults": {
            "stops": ["verse", "compulsory_stop"],
            "newline_mode": "verse",
        },
    }


@app.post("/api/phonemize")
def api_phonemize(body: PhonemizeRequest, request: Request) -> Dict[str, Any]:
    # Require explicit user action header to avoid accidental auto-requests from preloaders
    if request.headers.get("x-phonemize-intent") != "1":
        raise HTTPException(status_code=400, detail="Phonemize requires user action")
    # Validate newline mode
    if body.newline_mode not in {"verse", "word"}:
        raise HTTPException(status_code=400, detail="newline_mode must be 'verse' or 'word'")

    # Validate stops
    invalid = set(body.stops) - pm.valid_stops
    if invalid:
        raise HTTPException(status_code=400, detail=f"Invalid stops: {sorted(invalid)}")

    try:
        result = pm.phonemize(body.ref, stops=body.stops)
    except Exception as exc:  # pragma: no cover (thin API surface)
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    # Choose separators (still returned for convenience), but also include a
    # nested structure so the UI can reformat instantly without another call.
    if body.newline_mode == "verse":
        phonemes_text = result.phonemes_str(phoneme_sep=" ", word_sep=" ", verse_sep="\n")
    else:  # word
        phonemes_text = result.phonemes_str(phoneme_sep=" ", word_sep="\n", verse_sep="\n")

    return {
        "ref": result.ref,
        "text": result.text(),
        "phonemes": phonemes_text,
        # verses → words → phonemes
        "verses_words": result.phonemes_list("both"),
    }


def _sanitize_filename(name: str) -> str:
    return (
        name.replace(":", "-")
            .replace("/", "-")
            .replace(" ", "")
    )


def _delete_file(path: Path) -> None:
    try:
        path.unlink(missing_ok=True)
    except Exception:
        pass


@app.post("/api/export")
def api_export(body: ExportRequest, request: Request, background_tasks: BackgroundTasks) -> Any:
    if request.headers.get("x-phonemize-intent") != "1":
        raise HTTPException(status_code=400, detail="Export requires user action")

    if body.fmt not in {"json", "csv"}:
        raise HTTPException(status_code=400, detail="fmt must be 'json' or 'csv'")
    if body.split not in {"word", "verse", "both"}:
        raise HTTPException(status_code=400, detail="split must be 'word', 'verse', or 'both'")
    if body.fmt == "csv" and body.split == "both":
        raise HTTPException(status_code=400, detail="CSV does not support split='both'")

    invalid = set(body.stops) - pm.valid_stops
    if invalid:
        raise HTTPException(status_code=400, detail=f"Invalid stops: {sorted(invalid)}")

    try:
        result = pm.phonemize(body.ref, stops=body.stops)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    tmp_dir = APP_DIR / "tmp"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    filename_base = f"phonemized_{_sanitize_filename(body.ref)}_{body.split}.{body.fmt}"
    out_path = tmp_dir / filename_base

    try:
        result.save(out_path, fmt=body.fmt, split=body.split)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to export: {exc}") from exc

    background_tasks.add_task(_delete_file, out_path)
    media = "application/json" if body.fmt == "json" else "text/csv"
    return FileResponse(str(out_path), media_type=media, filename=filename_base)


# If running directly: `python3 -m uvicorn phonemizer.app.main:app --reload`
