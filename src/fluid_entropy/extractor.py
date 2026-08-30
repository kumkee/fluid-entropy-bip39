"""Video entropy extraction pipeline."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path

import cv2
import numpy as np

from fluid_entropy.utils import ROI, VideoMetadata, capture_metadata, ensure_video_path, seconds_to_frame, validate_roi


@dataclass(frozen=True, slots=True)
class ExtractionConfig:
    """Immutable extraction settings."""

    video_path: Path
    start_sec: float | None = None
    end_sec: float | None = None
    roi: ROI | None = None


@dataclass(frozen=True, slots=True)
class ExtractionResult:
    """Hashed frame-delta extraction result."""

    config: ExtractionConfig
    metadata: VideoMetadata
    digest: bytes
    byte_histogram: tuple[int, ...]
    bytes_processed: int
    deltas_processed: int
    start_frame: int
    end_frame: int

    @property
    def digest_hex(self) -> str:
        return self.digest.hex()


def _apply_roi(frame, roi: ROI | None):
    if roi is None:
        return frame
    x, y, w, h = validate_roi(roi)
    frame_height, frame_width = frame.shape[:2]
    if x + w > frame_width or y + h > frame_height:
        raise ValueError(
            f"ROI {roi} exceeds frame bounds {(frame_width, frame_height)}"
        )
    return frame[y : y + h, x : x + w]


def _build_config(
    video_path: str | Path,
    start_sec: float | None,
    end_sec: float | None,
    roi: ROI | None,
) -> ExtractionConfig:
    path = ensure_video_path(video_path)
    effective_start = 0.0 if start_sec is None else start_sec
    if end_sec is not None and end_sec <= effective_start:
        raise ValueError("end_sec must be greater than start_sec")
    if roi is not None:
        validate_roi(roi)
    return ExtractionConfig(video_path=path, start_sec=start_sec, end_sec=end_sec, roi=roi)


def extract_entropy(
    video_path: str | Path,
    *,
    start_sec: float | None = None,
    end_sec: float | None = None,
    roi: ROI | None = None,
) -> ExtractionResult:
    """Stream frame deltas into a SHA-256 accumulator."""

    config = _build_config(video_path, start_sec, end_sec, roi)
    capture = cv2.VideoCapture(str(config.video_path))
    if not capture.isOpened():
        raise ValueError(f"Unable to open video file: {config.video_path}")

    try:
        metadata = capture_metadata(capture)
        start_frame = seconds_to_frame(config.start_sec, metadata.fps)
        end_frame = seconds_to_frame(config.end_sec, metadata.fps)
        start_frame = 0 if start_frame is None else start_frame
        if end_frame is None and metadata.frame_count:
            end_frame = metadata.frame_count
        if metadata.frame_count and start_frame >= metadata.frame_count:
            raise ValueError("start_sec is beyond the end of the video")
        if metadata.frame_count and end_frame is not None and end_frame > metadata.frame_count:
            end_frame = metadata.frame_count
        if end_frame is not None and end_frame - start_frame < 2:
            raise ValueError("Video window must contain at least two frames")

        if start_frame:
            capture.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

        ok, previous = capture.read()
        if not ok:
            raise ValueError("Unable to read the first frame from the selected window")
        previous = _apply_roi(previous, config.roi)

        hasher = hashlib.sha256()
        histogram = np.zeros(256, dtype=np.int64)
        bytes_processed = 0
        deltas_processed = 0
        frame_index = start_frame + 1

        while True:
            if end_frame is not None and frame_index >= end_frame:
                break
            ok, current = capture.read()
            if not ok:
                break
            current = _apply_roi(current, config.roi)
            delta = cv2.absdiff(previous, current)
            delta_bytes = delta.tobytes()
            hasher.update(delta_bytes)
            histogram += np.bincount(delta.ravel(), minlength=256)
            bytes_processed += len(delta_bytes)
            deltas_processed += 1
            previous = current
            frame_index += 1

        if deltas_processed == 0:
            raise ValueError("Video window must contain at least two decodable frames")

        return ExtractionResult(
            config=config,
            metadata=metadata,
            digest=hasher.digest(),
            byte_histogram=tuple(int(count) for count in histogram),
            bytes_processed=bytes_processed,
            deltas_processed=deltas_processed,
            start_frame=start_frame,
            end_frame=frame_index,
        )
    finally:
        capture.release()
