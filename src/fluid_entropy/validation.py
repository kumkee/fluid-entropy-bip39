"""Entropy validation and audit helpers."""

from __future__ import annotations

from dataclasses import dataclass
import math

from fluid_entropy.extractor import ExtractionResult


@dataclass(frozen=True, slots=True)
class ValidationReport:
    """Statistical summary of extracted frame-delta bytes."""

    max_probability: float
    min_entropy_per_byte: float
    chi_square: float
    sample_size: int
    warnings: tuple[str, ...]
    passed: bool


def validate_extraction(
    extraction: ExtractionResult,
    *,
    min_entropy_threshold: float = 4.0,
) -> ValidationReport:
    histogram = extraction.byte_histogram
    sample_size = extraction.bytes_processed
    warnings: list[str] = []

    if sample_size <= 0:
        warnings.append("No frame-delta bytes were captured from the selected video window.")
        return ValidationReport(
            max_probability=1.0,
            min_entropy_per_byte=0.0,
            chi_square=float("inf"),
            sample_size=sample_size,
            warnings=tuple(warnings),
            passed=False,
        )

    max_count = max(histogram)
    max_probability = max_count / sample_size
    min_entropy = -math.log2(max_probability) if max_probability > 0 else 0.0
    expected = sample_size / len(histogram)
    chi_square = sum(((count - expected) ** 2) / expected for count in histogram) if expected else float("inf")

    if min_entropy < min_entropy_threshold:
        warnings.append(
            "Min-entropy estimate is below the default 4.0 bits/byte safety threshold; the video may be too static."
        )
    if extraction.deltas_processed < 8:
        warnings.append("Very short video window detected; collect more frames for stronger entropy confidence.")

    return ValidationReport(
        max_probability=max_probability,
        min_entropy_per_byte=min_entropy,
        chi_square=chi_square,
        sample_size=sample_size,
        warnings=tuple(warnings),
        passed=not warnings,
    )
