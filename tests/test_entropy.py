from pathlib import Path

import cv2
import numpy as np

from fluid_entropy.extractor import extract_entropy
from fluid_entropy.validation import validate_extraction


def _write_static_video(path: Path, *, frames: int = 12, fps: int = 6) -> None:
    writer = cv2.VideoWriter(
        str(path),
        cv2.VideoWriter_fourcc(*"MJPG"),
        fps,
        (64, 64),
    )
    assert writer.isOpened()
    frame = np.zeros((64, 64, 3), dtype=np.uint8)
    for _ in range(frames):
        writer.write(frame)
    writer.release()


def test_static_video_fails_entropy_audit(tmp_path: Path):
    video_path = tmp_path / "static.avi"
    _write_static_video(video_path)

    extraction = extract_entropy(video_path)
    report = validate_extraction(extraction)

    assert not report.passed
    assert report.min_entropy_per_byte == 0.0
    assert any("static" in warning for warning in report.warnings)
