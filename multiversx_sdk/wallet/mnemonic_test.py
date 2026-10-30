from typing import Any

import pytest

from multiversx_sdk.wallet import core
from multiversx_sdk.wallet.errors import InvalidAddressIndexError, InvalidMnemonicError
from multiversx_sdk.wallet.mnemonic import Mnemonic


def test_assert_text_is_valid():
    with pytest.raises(InvalidMnemonicError):
        Mnemonic.assert_text_is_valid("bad mnemonic")
        Mnemonic.assert_text_is_valid("moral volcano peasant pass circle pen over picture")


def test_generate():
    mnemonic = Mnemonic.generate()
    words = mnemonic.get_words()
    assert len(words) == 24

    with pytest.raises(InvalidAddressIndexError):
        mnemonic.derive_key(-1)


def test_derive_keys():
    mnemonic = Mnemonic(
        "moral volcano peasant pass circle pen over picture flat shop clap goat never lyrics gather prepare woman film husband gravity behind test tiger improve"
    )
    assert mnemonic.derive_key(0).hex() == "413f42575f7f26fad3317a778771212fdb80245850981e48b58a4f25e344e8f9"
    assert mnemonic.derive_key(1).hex() == "b8ca6f8203fb4b545a8e83c5384da033c415db155b53fb5b8eba7ff5a039d639"
    assert mnemonic.derive_key(2).hex() == "e253a571ca153dc2aee845819f74bcc9773b0586edead15a94cb7235a5027436"

    # change the text to an invalid mnemonic
    mnemonic.text = "this is an invalid mnemonic"
    with pytest.raises(InvalidMnemonicError):
        mnemonic.derive_key()


def test_convert_entropy_to_mnemonic_and_back():
    def test_conversion(text: str, entropy_hex: str) -> None:
        entropy_from_mnemonic = Mnemonic(text).get_entropy()
        mnemonic_from_entropy = Mnemonic.from_entropy(bytes.fromhex(entropy_hex))

        assert entropy_from_mnemonic.hex() == entropy_hex
        assert mnemonic_from_entropy.get_text() == text

    test_conversion(
        text="abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about",
        entropy_hex="00000000000000000000000000000000",
    )

    test_conversion(
        text="moral volcano peasant pass circle pen over picture flat shop clap goat never lyrics gather prepare woman film husband gravity behind test tiger improve",
        entropy_hex="8fbeb688d0529344e77d225898d4a73209510ad81d4ffceac9bfb30149bf387b",
    )

    with pytest.raises(ValueError):
        Mnemonic.from_entropy(bytes.fromhex("abba"))


DUMMY_MNEMONIC = "moral volcano peasant pass circle pen over picture flat shop clap goat never lyrics gather prepare woman film husband gravity behind test tiger improve"
ALICE_SECRET_KEY = "413f42575f7f26fad3317a778771212fdb80245850981e48b58a4f25e344e8f9"


@pytest.mark.parametrize(
    "text",
    [
        DUMMY_MNEMONIC.replace(" ", "\u00a0"),  # no-break space
        DUMMY_MNEMONIC.replace(" ", "\u00a0", 1),  # a single no-break space
        DUMMY_MNEMONIC.replace(" ", "\u3000"),  # ideographic space (e.g. inserted by Japanese IMEs)
        DUMMY_MNEMONIC.replace(" ", "\u202f", 2),  # narrow no-break space
        DUMMY_MNEMONIC.replace(" ", "\u2002", 1),  # en space
        "\uff4d\uff4f\uff52\uff41\uff4c" + DUMMY_MNEMONIC[len("moral") :],  # fullwidth "moral"
    ],
)
def test_derive_keys_with_mnemonic_requiring_nfkd_normalization(text: str):
    # BIP-39 requires NFKD normalization: these must derive exactly the same keys as the canonical mnemonic.
    mnemonic = Mnemonic(text)

    assert mnemonic.get_text() == DUMMY_MNEMONIC
    assert mnemonic.get_words() == DUMMY_MNEMONIC.split(" ")
    assert mnemonic.derive_key(0).hex() == ALICE_SECRET_KEY
    assert mnemonic.get_entropy().hex() == "8fbeb688d0529344e77d225898d4a73209510ad81d4ffceac9bfb30149bf387b"


def test_mnemonic_to_bip39seed_with_mnemonic_requiring_nfkd_normalization():
    # Even when called directly (bypassing the Mnemonic class), the seed must be computed over the normalized text.
    text = DUMMY_MNEMONIC.replace(" ", "\u00a0")
    assert core.mnemonic_to_bip39seed(text) == core.mnemonic_to_bip39seed(DUMMY_MNEMONIC)
    assert core.derive_keys(text, 0).hex() == ALICE_SECRET_KEY


def test_mnemonic_with_zero_width_space_is_rejected():
    # NFKD does not remove zero-width spaces, so the text remains invalid (consistent with other BIP-39 implementations).
    with pytest.raises(InvalidMnemonicError):
        Mnemonic(DUMMY_MNEMONIC.replace("moral ", "moral\u200b ", 1))


def test_mnemonic_to_bip39seed_with_reference_vectors():
    # https://github.com/trezor/python-mnemonic/blob/master/vectors.json (passphrase "TREZOR")
    assert (
        core.mnemonic_to_bip39seed(
            "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about", "TREZOR"
        ).hex()
        == "c55257c360c07c72029aebc1b53c05ed0362ada38ead3e3e9efa3708e53495531f09a6987599d18264c1e1c92f2cf141630c7a3c4ab7c81b2f001698e7463b04"
    )
    assert (
        core.mnemonic_to_bip39seed(
            "zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo vote", "TREZOR"
        ).hex()
        == "dd48c104698c30cfe2b6142103248622fb7bb0ff692eebb00089b32d22484e1613912f0a5b694407be899ffd31ed3992c456cdf60f5d4564b8ba3f05a69890ad"
    )


def test_mnemonic_to_bip39seed_normalizes_passphrase():
    # "caf\u00e9" (composed, NFC) and "cafe\u0301" (decomposed, NFD) must yield the same seed (cross-checked with npm "bip39").
    text = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"
    expected = "af8bbd2566df7b69d926f2b09dfdbd75db6c994a3399b2cc65f928d63e3fd4e61218ee0d15f8c810be4d45e66d47b43c15a5cc753976b1666912377ff7ae9818"

    assert core.mnemonic_to_bip39seed(text, "caf\u00e9").hex() == expected
    assert core.mnemonic_to_bip39seed(text, "cafe\u0301").hex() == expected


@pytest.mark.parametrize("address_index", [-1, 2**31, 2**32, True, False, 1.0, "1", None])
def test_derive_key_with_invalid_address_index(address_index: Any):
    # Previously, e.g. 2^31 raised a bare "struct.error", while "True" was accepted (as index 1).
    mnemonic = Mnemonic(DUMMY_MNEMONIC)

    with pytest.raises(InvalidAddressIndexError):
        mnemonic.derive_key(address_index)

    with pytest.raises(InvalidAddressIndexError):
        core.derive_keys(DUMMY_MNEMONIC, address_index)


def test_derive_key_with_largest_address_index():
    # The hardened index (2^31 - 1) + 2^31 is the largest one that fits in 32 bits (cross-checked with npm "ed25519-hd-key").
    mnemonic = Mnemonic(DUMMY_MNEMONIC)
    assert mnemonic.derive_key(2**31 - 1).hex() == "7ee7bce4e4e4a5aa73184bc759684b3b613f1e18af8caa8c0cc6b2530a112765"
