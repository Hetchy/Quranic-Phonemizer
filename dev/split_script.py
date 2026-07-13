import json
import sys
import argparse


def main():
    parser = argparse.ArgumentParser(
        description="Split text fields into individual words, keyed by surah:ayah:word location."
    )
    parser.add_argument("input_file", help="Path to input JSON file")
    parser.add_argument("field", help="Name of the JSON field containing the text to split (e.g. aya_text)")
    parser.add_argument("output_file", help="Path to output JSON file")
    args = parser.parse_args()

    try:
        with open(args.input_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: input file not found: {args.input_file}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: invalid JSON in {args.input_file}: {e}")
        sys.exit(1)

    words_output = {}
    running_id = 1

    for record in data:
        text = record.get(args.field, "")
        if not text:
            continue

        surah = str(record.get("sura_no"))
        ayah = str(record.get("aya_no"))
        words = text.split()  # split on whitespace

        for word_position, word in enumerate(words, start=1):
            word_str = str(word_position)
            location = f"{surah}:{ayah}:{word_str}"

            words_output[location] = {
                "id": running_id,
                "surah": surah,
                "ayah": ayah,
                "word": word_str,
                "location": location,
                "text": word
            }
            running_id += 1

    with open(args.output_file, "w", encoding="utf-8") as f:
        json.dump(words_output, f, ensure_ascii=False, indent=2)

    print(f"Done. Wrote {len(words_output)} words to {args.output_file}")


if __name__ == "__main__":
    main()