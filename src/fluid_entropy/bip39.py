"""BIP-39 encoding helpers."""

from __future__ import annotations

from functools import lru_cache
import hashlib
from importlib import resources


@lru_cache(maxsize=1)
def load_wordlist() -> tuple[str, ...]:
    text = resources.files("fluid_entropy").joinpath("bip39_english.txt").read_text(encoding="utf-8")
    words = tuple(line.strip() for line in text.splitlines() if line.strip())
    if len(words) != 2048:
        raise ValueError(f"Expected 2048 BIP-39 words, found {len(words)}")
    return words


def entropy_to_mnemonic(entropy: bytes | bytearray | memoryview | str) -> tuple[str, ...]:
    if isinstance(entropy, str):
        entropy_bytes = bytes.fromhex(entropy)
    else:
        entropy_bytes = bytes(entropy)
    entropy_bits = len(entropy_bytes) * 8
    if entropy_bits < 128 or entropy_bits > 256 or entropy_bits % 32 != 0:
        raise ValueError("BIP-39 entropy must be 128-256 bits in 32-bit increments")

    checksum_bits = entropy_bits // 32
    checksum = hashlib.sha256(entropy_bytes).digest()[0]
    combined = "".join(f"{byte:08b}" for byte in entropy_bytes) + f"{checksum:08b}"[:checksum_bits]
    wordlist = load_wordlist()
    return tuple(
        wordlist[int(combined[index : index + 11], 2)]
        for index in range(0, len(combined), 11)
    )


def format_mnemonic(
    mnemonic: tuple[str, ...] | list[str],
    *,
    numbered: bool = True,
    masked: bool = False,
) -> str:
    words = [_mask_word(word) if masked else word for word in mnemonic]
    if numbered:
        return "\n".join(f"{index:02d}. {word}" for index, word in enumerate(words, start=1))
    return " ".join(words)


def _mask_word(word: str) -> str:
    if len(word) < 2:
        return "•"
    return word[0] + ("•" * (len(word) - 1))
