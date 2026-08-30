"""Generate a deterministic synthetic chaotic video fixture."""

from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import numpy as np


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--frames", type=int, default=120)
    parser.add_argument("--fps", type=int, default=30)
    parser.add_argument("--width", type=int, default=160)
    parser.add_argument("--height", type=int, default=120)
    parser.add_argument("--seed", type=int, default=7)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    writer = cv2.VideoWriter(
        str(args.output),
        cv2.VideoWriter_fourcc(*"MJPG"),
        args.fps,
        (args.width, args.height),
    )
    if not writer.isOpened():
        raise SystemExit("Unable to open output video writer")

    rng = np.random.default_rng(args.seed)
    for index in range(args.frames):
        frame = rng.integers(0, 256, size=(args.height, args.width, 3), dtype=np.uint8)
        center = (int((index * 13) % args.width), int((index * 9) % args.height))
        radius = max(6, min(args.width, args.height) // 10)
        cv2.circle(frame, center, radius, (255, 255, 255), thickness=-1)
        cv2.GaussianBlur(frame, (5, 5), sigmaX=0, dst=frame)
        writer.write(frame)
    writer.release()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
