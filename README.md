# fluid-entropy-bip39

`fluid-entropy-bip39` derives a 24-word BIP-39 mnemonic from frame-to-frame optical entropy in offline video recordings of chaotic macroscopic systems such as dyed boiling water, effervescent tablet plumes, and granular mixing.

## Introduction & Motivation

The project treats turbulent advection, multiphase bubbling, and granular collisions as a macroscopic entropy source. Rather than trusting a network-connected pseudorandom generator, it hashes frame deltas from a locally recorded video stream and converts the resulting 256-bit digest into a canonical BIP-39 mnemonic.

Two metrics matter:

- **Min-entropy** \(H\_\infty = -\\log\_2(p\_{max})\): a conservative lower bound dominated by the most common observed delta byte.
- **Chaotic divergence**: fluid and granular systems amplify microscopic perturbations through nonlinear transport, making repeated trajectories practically irreproducible under ordinary filming conditions.

This tool is not a formal certified RNG, but it provides a transparent, inspectable, open-source workflow for harvesting video-derived entropy in an air-gapped environment.

## Repository Layout

```text
fluid-entropy-bip39/
├── pyproject.toml
├── README.md
├── LICENSE
├── .gitignore
├── Makefile
├── data/
│   └── bip39_english.txt
├── scripts/
│   └── generate_synthetic_video.py
├── src/
│   └── fluid_entropy/
│       ├── __init__.py
│       ├── bip39.py
│       ├── cli.py
│       ├── extractor.py
│       ├── validation.py
│       └── utils.py
└── tests/
    ├── __init__.py
    ├── test_bip39.py
    ├── test_entropy.py
    └── test_extractor.py
```

## Recommended Filming Experiments

### 1. Dyed Effervescent Tablet in Oil/Water Bilayer

Drop a dyed effervescent tablet through an oil/water bilayer and film the bubble plumes, droplet shearing, and unstable interfaces. This creates strong optical gradients with Rayleigh-Taylor-like breakup and complex multiphase advection.

### 2. Food Dye in Boiling Water

Film dye injection into vigorously boiling water. Nucleate boiling, vapor collapse, and thermal turbulence create fast-changing color fields that are well suited to frame-difference extraction.

### 3. Mixed Granular Pouring

Pour mixed grains, seeds, or beads through a funnel onto a pile. Inelastic impacts and miniature avalanches create sharp, irregular motion boundaries with rich temporal variation.

## Camera Filming Protocol

For mobile capture, especially Samsung Pro Video style controls:

- Use **UHD 60 fps** where possible, or **UHD 30 fps** if lighting is limited.
- Prefer high bitrate / APV or the highest quality local codec available.
- Lock exposure manually.
- Use shutter speeds of roughly **1/500 s or faster** for granular motion and **1/120 s or faster** for fluid motion.
- Disable video stabilization.
- Lock manual focus.
- Lock white balance to avoid slow color drift from automatic correction.
- Avoid reflective container edges inside the frame when possible.

## Security & Air-Gap Instructions

1. Record video on a device that can stay offline during capture.
2. Transfer the source `.mp4` or other video file to an offline computer using removable media such as a USB drive.
3. Install dependencies on the offline machine from trusted packages obtained beforehand.
4. Run `fluid-entropy generate` only on the offline system.
5. Write the mnemonic down by hand; do not sync it to cloud notes, screenshots, or messaging apps.

The CLI prints an explicit offline reminder on every non-quiet invocation.

## Installation

```bash
python -m pip install -e .[test]
```

## Quickstart

Generate a numbered 24-word mnemonic:

```bash
fluid-entropy generate /path/to/video.mp4
```

Target the most chaotic time window and crop away static edges:

```bash
fluid-entropy generate /path/to/video.mp4 --start 2.5 --end 7.5 --roi 120,80,960,960
```

Mask terminal output while still confirming word positions:

```bash
fluid-entropy generate /path/to/video.mp4 --mask
```

Audit entropy without printing the mnemonic:

```bash
fluid-entropy audit /path/to/video.mp4
```

## CLI Behavior

- `generate` streams `cv2.absdiff` frame deltas into `hashlib.sha256()`.
- The 32-byte digest is converted into a BIP-39 mnemonic with the standard checksum procedure.
- `audit` reports byte-count statistics, MCV-derived min-entropy, and a chi-square summary.
- Videos that appear too static fail validation with a warning instead of silently generating a seed phrase.

## Development

Install and run the tests:

```bash
make install
make test
```

Generate a deterministic synthetic fixture:

```bash
python scripts/generate_synthetic_video.py /tmp/fluid-fixture.avi
```
