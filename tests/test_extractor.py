from pathlib import Path

import cv2
import numpy as np
import pytest

from fluid_entropy.extractor import extract_entropy


def _write_synthetic_video(path: Path, *, seed: int = 7, frames: int = 24, fps: int = 12) -> None:
    rng = np.random.default_rng(seed)
    writer = cv2.VideoWriter(
        str(path),
        cv2.VideoWriter_fourcc(*"MJPG"),
        fps,
        (96, 96),
    )
    assert writer.isOpened()
    for index in range(frames):
        frame = rng.integers(0, 256, size=(96, 96, 3), dtype=np.uint8)
        center = (int((index * 7) % 96), int((index * 11) % 96))
        cv2.circle(frame, center, 12, (255, 255, 255), thickness=-1)
        writer.write(frame)
    writer.release()


def test_extractor_produces_digest_and_statistics(tmp_path: Path):
    video_path = tmp_path / "synthetic.avi"
    _write_synthetic_video(video_path)

    result = extract_entropy(video_path)

    assert len(result.digest) == 32
    assert result.bytes_processed > 0
    assert result.deltas_processed == 23


def test_extractor_supports_temporal_window_and_roi(tmp_path: Path):
    video_path = tmp_path / "windowed.avi"
    _write_synthetic_video(video_path, seed=11, frames=30, fps=10)

    full_result = extract_entropy(video_path)
    partial_result = extract_entropy(video_path, start_sec=0.5, end_sec=2.0, roi=(16, 16, 48, 48))

    assert partial_result.deltas_processed < full_result.deltas_processed
    assert partial_result.bytes_processed < full_result.bytes_processed
    assert partial_result.digest != full_result.digest


def test_extractor_rejects_zero_length_window(tmp_path: Path):
    video_path = tmp_path / "invalid-window.avi"
    _write_synthetic_video(video_path, frames=10, fps=10)

    with pytest.raises(ValueError, match="end_sec must be greater than start_sec"):
        extract_entropy(video_path, start_sec=0.0, end_sec=0.0)
