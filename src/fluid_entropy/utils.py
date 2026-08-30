"""Shared utilities for fluid entropy extraction."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2

ROI = tuple[int, int, int, int]


@dataclass(frozen=True, slots=True)
class VideoMetadata:
    """Basic metadata read from a video stream."""

    fps: float
    frame_count: int
    width: int
    height: int


def ensure_video_path(video_path: str | Path) -> Path:
    path = Path(video_path).expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError(f"Video file not found: {path}")
    return path


def parse_roi(value: str | None) -> ROI | None:
    if value is None:
        return None
    try:
        x_str, y_str, w_str, h_str = value.split(",")
        roi = (int(x_str), int(y_str), int(w_str), int(h_str))
    except ValueError as exc:
        raise ValueError("ROI must be formatted as x,y,w,h") from exc
    validate_roi(roi)
    return roi


def validate_roi(roi: ROI) -> ROI:
    x, y, w, h = roi
    if min(x, y) < 0 or min(w, h) <= 0:
        raise ValueError("ROI coordinates must be non-negative and ROI size must be positive")
    return roi


def capture_metadata(capture: cv2.VideoCapture) -> VideoMetadata:
    fps = float(capture.get(cv2.CAP_PROP_FPS) or 0.0)
    frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
    return VideoMetadata(fps=fps, frame_count=frame_count, width=width, height=height)


def seconds_to_frame(seconds: float | None, fps: float) -> int | None:
    if seconds is None:
        return None
    if seconds < 0:
        raise ValueError("Time bounds must be non-negative")
    if fps <= 0:
        raise ValueError("Video FPS metadata is required when using time bounds")
    return int(seconds * fps)
