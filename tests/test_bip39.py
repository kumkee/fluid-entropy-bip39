from fluid_entropy.bip39 import entropy_to_mnemonic, format_mnemonic, load_wordlist


def test_wordlist_has_expected_size():
    assert len(load_wordlist()) == 2048


def test_official_256_bit_vectors_match_canonical_mnemonics():
    vectors = {
        "0000000000000000000000000000000000000000000000000000000000000000": (
            "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon "
            "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon "
            "abandon abandon abandon art"
        ),
        "7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f": (
            "legal winner thank year wave sausage worth useful legal winner thank year wave "
            "sausage worth useful legal winner thank year wave sausage worth title"
        ),
        "68a79eaca2324873eacc50cb9c6eca8cc68ea5d936f98787c60c7ebc74e6ce7c": (
            "hamster diagram private dutch cause delay private meat slide toddler razor "
            "book happy fancy gospel tennis maple dilemma loan word shrug inflict delay length"
        ),
    }

    for entropy_hex, expected in vectors.items():
        assert " ".join(entropy_to_mnemonic(entropy_hex)) == expected


def test_format_mnemonic_supports_masking():
    mnemonic = entropy_to_mnemonic("00000000000000000000000000000000")
    formatted = format_mnemonic(mnemonic, numbered=True, masked=True)
    assert formatted.splitlines()[0].startswith("01. a")
    assert "about" not in formatted
