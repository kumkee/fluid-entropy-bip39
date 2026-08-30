"""Command-line interface for fluid entropy BIP-39 generation."""

from __future__ import annotations

import argparse
import sys

from fluid_entropy.bip39 import entropy_to_mnemonic, format_mnemonic
from fluid_entropy.extractor import extract_entropy
from fluid_entropy.utils import parse_roi
from fluid_entropy.validation import validate_extraction

OFFLINE_REMINDER = (
    "Security reminder: run this tool on an air-gapped/offline machine and never upload source video or mnemonic data."
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="fluid-entropy")
    subparsers = parser.add_subparsers(dest="command", required=True)

    for command in ("generate", "audit"):
        subparser = subparsers.add_parser(command)
        subparser.add_argument("video_path")
        subparser.add_argument("--start", type=float, default=None, dest="start_sec")
        subparser.add_argument("--end", type=float, default=None, dest="end_sec")
        subparser.add_argument("--roi", type=str, default=None)
        if command == "generate":
            subparser.add_argument("--quiet", action="store_true")
            subparser.add_argument("--mask", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        extraction = extract_entropy(
            args.video_path,
            start_sec=args.start_sec,
            end_sec=args.end_sec,
            roi=parse_roi(args.roi),
        )
        report = validate_extraction(extraction)
    except Exception as exc:  # pragma: no cover - argparse entrypoint guard
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if getattr(args, "quiet", False):
        reminder_stream = None
    else:
        reminder_stream = sys.stderr

    if reminder_stream is not None:
        print(OFFLINE_REMINDER, file=reminder_stream)

    if args.command == "audit":
        print(f"digest_sha256={extraction.digest_hex}")
        print(f"bytes_processed={extraction.bytes_processed}")
        print(f"deltas_processed={extraction.deltas_processed}")
        print(f"min_entropy_per_byte={report.min_entropy_per_byte:.4f}")
        print(f"max_probability={report.max_probability:.6f}")
        print(f"chi_square={report.chi_square:.4f}")
        for warning in report.warnings:
            print(f"warning: {warning}", file=sys.stderr)
        return 0 if report.passed else 1

    if not report.passed:
        for warning in report.warnings:
            print(f"warning: {warning}", file=sys.stderr)
        return 1

    mnemonic = entropy_to_mnemonic(extraction.digest)
    if args.quiet:
        print(format_mnemonic(mnemonic, numbered=False, masked=False))
    else:
        print(format_mnemonic(mnemonic, numbered=True, masked=args.mask))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
