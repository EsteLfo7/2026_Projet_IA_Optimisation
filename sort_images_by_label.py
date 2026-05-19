#!/usr/bin/env python3
"""Sort images into label folders using train.csv."""

from __future__ import annotations

import argparse
import csv
import os
import shutil
from pathlib import Path

SUPPORTED_EXTS = (".png", ".jpg", ".jpeg")


def find_image_file(image_id: str, src_dir: Path) -> Path | None:
    for ext in SUPPORTED_EXTS:
        candidate = src_dir / f"{image_id}{ext}"
        if candidate.exists():
            return candidate
    return None


def load_labels(csv_path: Path) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    with csv_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if "Image" not in reader.fieldnames or "Label" not in reader.fieldnames:
            raise ValueError("CSV must contain 'Image' and 'Label' headers.")
        for row in reader:
            image_id = (row.get("Image") or "").strip()
            label = (row.get("Label") or "").strip()
            if image_id and label:
                rows.append((image_id, label))
    return rows


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def sort_images(
    csv_path: Path,
    src_dir: Path,
    out_dir: Path,
    move_files: bool,
) -> dict[str, int]:
    labels = load_labels(csv_path)
    counts: dict[str, int] = {}

    for image_id, label in labels:
        source = find_image_file(image_id, src_dir)
        if source is None:
            print(f"[WARN] Missing image for id {image_id}")
            continue

        label_dir = out_dir / label
        ensure_dir(label_dir)
        dest = label_dir / source.name

        if move_files:
            shutil.move(str(source), str(dest))
        else:
            shutil.copy2(str(source), str(dest))

        counts[label] = counts.get(label, 0) + 1

    return counts


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Sort images into label folders using train.csv",
    )
    parser.add_argument(
        "--csv",
        default="train.csv",
        help="Path to train.csv (default: train.csv)",
    )
    parser.add_argument(
        "--src",
        default="DATASET_images/Training dataset - images-20260519",
        help="Source images directory",
    )
    parser.add_argument(
        "--out",
        default="DATASET_images/Training_sorted",
        help="Output directory for sorted images",
    )
    parser.add_argument(
        "--move",
        action="store_true",
        help="Move files instead of copying",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    csv_path = Path(args.csv)
    src_dir = Path(args.src)
    out_dir = Path(args.out)

    if not csv_path.exists():
        raise SystemExit(f"CSV not found: {csv_path}")
    if not src_dir.exists():
        raise SystemExit(f"Source directory not found: {src_dir}")

    counts = sort_images(csv_path, src_dir, out_dir, args.move)

    total = sum(counts.values())
    print("Done. Copied" if not args.move else "Done. Moved", total, "images.")
    for label, count in sorted(counts.items()):
        print(f"- {label}: {count}")


if __name__ == "__main__":
    main()
