"""
generate_dataset.py
Run once before the quiz:  python generate_dataset.py
"""

import os
import json
import shutil
import glob

from icrawler.builtin import BingImageCrawler

IMAGES_DIR   = "dataset/images"
ANSWERS_PATH = "dataset/answers.json"
TEMP_DIR     = "temp"

CELEBRITIES = [
    ("Virat Kohli cricketer face portrait",  "Virat Kohli"),
    ("Elon Musk face portrait",              "Elon Musk"),
    ("Cristiano Ronaldo face portrait",      "Cristiano Ronaldo"),
    ("Taylor Swift face portrait",           "Taylor Swift"),
    ("Barack Obama face portrait",           "Barack Obama"),
    ("Lionel Messi face portrait",           "Lionel Messi"),
    ("Priyanka Chopra face portrait",        "Priyanka Chopra"),
]

IMAGES_PER_PERSON = 1


def clean_dir(path: str):
    if os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(path, exist_ok=True)


def download_images() -> dict:
    clean_dir(IMAGES_DIR)
    clean_dir(TEMP_DIR)

    answers: dict[str, str] = {}
    counter = 1

    for query, name in CELEBRITIES:
        scratch = os.path.join(TEMP_DIR, f"person_{counter}")
        os.makedirs(scratch, exist_ok=True)

        print(f"[{counter}/{len(CELEBRITIES)}] Downloading: {name}")
        try:
            crawler = BingImageCrawler(storage={"root_dir": scratch})
            crawler.crawl(
                keyword=query,
                max_num=IMAGES_PER_PERSON,
                filters={"type": "photo", "size": "medium"},
                file_idx_offset=0,
            )
        except Exception as exc:
            print(f"  ⚠  Crawler error for {name}: {exc}")

        found = sorted(
            glob.glob(os.path.join(scratch, "*.jpg"))
            + glob.glob(os.path.join(scratch, "*.jpeg"))
            + glob.glob(os.path.join(scratch, "*.png"))
            + glob.glob(os.path.join(scratch, "*.webp"))
        )

        if not found:
            print(f"  ✗  No image found for {name}, skipping.")
            continue

        src           = found[0]
        dest_filename = f"{counter}.jpg"
        dest_path     = os.path.join(IMAGES_DIR, dest_filename)

        try:
            from PIL import Image
            img = Image.open(src).convert("RGB")
            img.save(dest_path, "JPEG", quality=90)
        except Exception:
            shutil.copy(src, dest_path)

        answers[dest_filename] = name
        print(f"  ✓  Saved as {dest_filename}")
        counter += 1

    return answers


def save_answers(answers: dict):
    os.makedirs("dataset", exist_ok=True)
    with open(ANSWERS_PATH, "w") as f:
        json.dump(answers, f, indent=4)
    print(f"\n✓ answers.json saved → {ANSWERS_PATH}")


def main():
    print("=" * 50)
    print("  Quiz Dataset Generator")
    print("=" * 50)

    answers = download_images()

    if not answers:
        print("\n✗ No images downloaded. Check your internet connection.")
        return

    save_answers(answers)

    # clean temp
    shutil.rmtree(TEMP_DIR, ignore_errors=True)
    os.makedirs(TEMP_DIR, exist_ok=True)

    print(f"\n✓ Dataset ready: {len(answers)} image(s) in {IMAGES_DIR}")
    for fname, name in answers.items():
        print(f"  {fname}  →  {name}")

    print("\nRun:  streamlit run app.py")


if __name__ == "__main__":
    main()
