let META = null;
let CACHE = { ref: null, verses_words: null, text: null };
let ALLOW_PHONEMIZE = false;

async function loadMeta() {
  const res = await fetch('/api/meta');
  if (!res.ok) throw new Error('Failed to load metadata');
  META = await res.json();
}

function option(value, label) {
  const o = document.createElement('option');
  o.value = value; o.textContent = label; return o;
}

function fillSurahSelect(sel) {
  sel.innerHTML = '';
  META.surahs.forEach(s => sel.appendChild(option(String(s.id), `${s.id}. ${s.name_en} (${s.name_ar})`)));
}

function fillVerseSelect(sel, surahId) {
  sel.innerHTML = '';
  const s = META.surahs.find(x => x.id === Number(surahId));
  if (!s) return;
  s.verses.forEach(v => sel.appendChild(option(String(v.verse), `Verse ${v.verse}`)));
}

function fillWordSelect(sel, surahId, verseNo) {
  sel.innerHTML = '';
  const s = META.surahs.find(x => x.id === Number(surahId));
  if (!s) return;
  const v = s.verses.find(v => v.verse === Number(verseNo));
  if (!v) return;
  for (let i = 1; i <= v.num_words; i++) sel.appendChild(option(String(i), `Word ${i}`));
}

function show(el, on) {
  el.classList.toggle('hide', !on);
}

function setupModeVisibility() {
  const mode = document.querySelector('input[name="mode"]:checked').value;
  show(document.getElementById('single-selectors'), mode === 'single');
  show(document.getElementById('range-selectors'), mode === 'range');
}

function buildRefFromSingle() {
  const kind = document.querySelector('input[name="singleType"]:checked').value;
  const s = document.getElementById('single-surah').value;
  if (kind === 'surah') return s;
  const v = document.getElementById('single-verse').value;
  if (kind === 'verse') return `${s}:${v}`;
  const w = document.getElementById('single-word').value;
  return `${s}:${v}:${w}`;
}

function buildRefFromRange() {
  const ks = document.getElementById('range-start-kind').value;
  const ke = document.getElementById('range-end-kind').value;
  const ss = document.getElementById('range-start-surah').value;
  const se = document.getElementById('range-end-surah').value;

  let left = ss;
  if (ks !== 'surah') {
    const vs = document.getElementById('range-start-verse').value;
    left = `${left}:${vs}`;
    if (ks === 'word') {
      const ws = document.getElementById('range-start-word').value;
      left = `${left}:${ws}`;
    }
  }

  let right = se;
  if (ke !== 'surah') {
    const ve = document.getElementById('range-end-verse').value;
    right = `${right}:${ve}`;
    if (ke === 'word') {
      const we = document.getElementById('range-end-word').value;
      right = `${right}:${we}`;
    }
  }
  return `${left} - ${right}`;
}

function currentRef() {
  const mode = document.querySelector('input[name="mode"]:checked').value;
  return mode === 'single' ? buildRefFromSingle() : buildRefFromRange();
}

function currentStops() {
  const out = [];
  // Verse boundary
  if (document.getElementById('stop-verse').checked) out.push('verse');
  // YAML-driven stops
  (META.stops || []).forEach(s => {
    if (document.getElementById(`stop-${s.key}`).checked) out.push(s.key);
  });
  return out;
}

async function phonemize() {
  if (!ALLOW_PHONEMIZE) return; // prevent any accidental auto-run
  const newlineMode = document.querySelector('input[name="newlineMode"]:checked').value;
  const payload = {
    ref: currentRef(),
    stops: currentStops(),
    newline_mode: newlineMode,
  };
  setLoading(true);
  try {
    const res = await fetch('/api/phonemize', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'x-phonemize-intent': '1' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      alert(err.detail || 'Request failed');
      return;
    }
    const data = await res.json();
    CACHE.ref = data.ref;
    CACHE.text = data.text;
    CACHE.verses_words = data.verses_words;
    renderFromCache();
  } finally {
    setLoading(false);
  }
}

function setupSingleVisibility() {
  const kind = document.querySelector('input[name="singleType"]:checked').value;
  show(document.querySelector('.single-verse'), kind !== 'surah');
  show(document.querySelector('.single-word'), kind === 'word');
}

function setupRangeVisibility() {
  const ks = document.getElementById('range-start-kind').value;
  const ke = document.getElementById('range-end-kind').value;
  // Start
  document.getElementById('range-start-verse').disabled = (ks === 'surah');
  document.getElementById('range-start-word').disabled = (ks !== 'word');
  // End
  document.getElementById('range-end-verse').disabled = (ke === 'surah');
  document.getElementById('range-end-word').disabled = (ke !== 'word');
}

function renderStops() {
  const box = document.getElementById('stops-box');
  box.innerHTML = '';
  // Verse boundary
  const verse = document.createElement('label');
  verse.innerHTML = `<input id="stop-verse" type="checkbox" checked /> Verse (boundary)`;
  box.appendChild(verse);
  // Other stops
  (META.stops || []).forEach(s => {
    const lab = document.createElement('label');
    lab.innerHTML = `<input id="stop-${s.key}" type="checkbox" ${s.default ? 'checked' : ''} /> ${s.label} <span class="symbol">${s.symbol}</span>`;
    box.appendChild(lab);
  });
}

async function init() {
  // Ensure loading overlay is hidden on entry regardless of CSS cache
  setLoading(false);

  await loadMeta();

  // Populate base selects
  const singleSurah = document.getElementById('single-surah');
  const singleVerse = document.getElementById('single-verse');
  const singleWord = document.getElementById('single-word');
  fillSurahSelect(singleSurah);
  fillVerseSelect(singleVerse, singleSurah.value);
  fillWordSelect(singleWord, singleSurah.value, singleVerse.value);

  const rsSurah = document.getElementById('range-start-surah');
  const rsVerse = document.getElementById('range-start-verse');
  const rsWord = document.getElementById('range-start-word');
  const reSurah = document.getElementById('range-end-surah');
  const reVerse = document.getElementById('range-end-verse');
  const reWord = document.getElementById('range-end-word');
  [rsSurah, reSurah].forEach(fillSurahSelect);
  fillVerseSelect(rsVerse, rsSurah.value);
  fillVerseSelect(reVerse, reSurah.value);
  fillWordSelect(rsWord, rsSurah.value, rsVerse.value);
  fillWordSelect(reWord, reSurah.value, reVerse.value);

  // Listeners
  document.querySelectorAll('input[name="singleType"]').forEach(el => el.addEventListener('change', setupSingleVisibility));
  singleSurah.addEventListener('change', () => { fillVerseSelect(singleVerse, singleSurah.value); fillWordSelect(singleWord, singleSurah.value, singleVerse.value); });
  singleVerse.addEventListener('change', () => fillWordSelect(singleWord, singleSurah.value, singleVerse.value));

  document.getElementById('range-start-kind').addEventListener('change', setupRangeVisibility);
  document.getElementById('range-end-kind').addEventListener('change', setupRangeVisibility);

  rsSurah.addEventListener('change', () => { fillVerseSelect(rsVerse, rsSurah.value); fillWordSelect(rsWord, rsSurah.value, rsVerse.value); });
  reSurah.addEventListener('change', () => { fillVerseSelect(reVerse, reSurah.value); fillWordSelect(reWord, reSurah.value, reVerse.value); });
  rsVerse.addEventListener('change', () => fillWordSelect(rsWord, rsSurah.value, rsVerse.value));
  reVerse.addEventListener('change', () => fillWordSelect(reWord, reSurah.value, reVerse.value));

  renderStops();
  setupSingleVisibility();
  setupRangeVisibility();
  setupModeVisibility();

  document.getElementById('go').addEventListener('click', () => { ALLOW_PHONEMIZE = true; phonemize(); });
  document.querySelectorAll('input[name="mode"]').forEach(el => el.addEventListener('change', setupModeVisibility));
  document.querySelectorAll('input[name="newlineMode"]').forEach(el => el.addEventListener('change', () => CACHE.verses_words && renderFromCache()));

  // Export
  document.getElementById('export').addEventListener('click', exportData);
}

function setLoading(on) {
  const el = document.getElementById('loading');
  // force style toggling to avoid any cached CSS/DOM race
  if (on) {
    el.style.display = 'flex';
    el.classList.add('on');
    el.classList.remove('hide');
    el.removeAttribute('hidden');
  } else {
    el.style.display = 'none';
    el.classList.remove('on');
    el.classList.add('hide');
    el.setAttribute('hidden', '');
  }
}

async function exportData() {
  const fmt = document.getElementById('export-format').value;
  const split = document.getElementById('export-split').value;
  if (fmt === 'csv' && split === 'both') {
    alert("CSV doesn't support 'both' split. Choose JSON or a different split.");
    return;
  }
  const payload = {
    ref: currentRef(),
    stops: currentStops(),
    fmt,
    split,
  };
  setLoading(true);
  try {
    const res = await fetch('/api/export', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'x-phonemize-intent': '1' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      alert(err.detail || 'Export failed');
      return;
    }
    // Trigger download
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    // Derive filename from content-disposition if present
    const cd = res.headers.get('content-disposition') || '';
    const m = cd.match(/filename="?([^";]+)"?/i);
    a.download = m ? m[1] : `phonemized.${fmt}`;
    a.href = url;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  } finally {
    setLoading(false);
  }
}

function renderFromCache() {
  const newlineMode = document.querySelector('input[name="newlineMode"]:checked').value;
  const textEl = document.getElementById('text');
  const phEl = document.getElementById('phonemes');

  textEl.textContent = CACHE.text || '';
  const v = CACHE.verses_words || [];

  if (newlineMode === 'verse') {
    const lines = v.map(words => words.flat().join(' '));
    phEl.textContent = lines.join('\n');
  } else {
    const lines = [];
    v.forEach(words => {
      words.forEach(word => lines.push(word.join(' ')));
    });
    phEl.textContent = lines.join('\n');
  }
}

init().catch(err => {
  console.error(err);
  alert('Failed to initialize app');
});

