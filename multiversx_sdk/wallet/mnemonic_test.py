import pytest

from multiversx_sdk.wallet.errors import InvalidMnemonicError
from multiversx_sdk.wallet.mnemonic import Mnemonic


def test_assert_text_is_valid():
    with pytest.raises(InvalidMnemonicError):
        Mnemonic.assert_text_is_valid("bad mnemonic")
        Mnemonic.assert_text_is_valid("moral volcano peasant pass circle pen over picture")


def test_generate():
    mnemonic = Mnemonic.generate()
    words = mnemonic.get_words()
    assert len(words) == 24


def test_derive_keys():
    mnemonic = Mnemonic("moral volcano peasant pass circle pen over picture flat shop clap goat never lyrics gather prepare woman film husband gravity behind test tiger improve")
    assert mnemonic.derive_key(0).hex() == "413f42575f7f26fad3317a778771212fdb80245850981e48b58a4f25e344e8f9"
    assert mnemonic.derive_key(1).hex() == "b8ca6f8203fb4b545a8e83c5384da033c415db155b53fb5b8eba7ff5a039d639"
    assert mnemonic.derive_key(2).hex() == "e253a571ca153dc2aee845819f74bcc9773b0586edead15a94cb7235a5027436"


def test_convert_entropy_to_mnemonic_and_back():
    def test_conversion(text: str, entropy_hex: str) -> None:
        entropy_from_mnemonic = Mnemonic(text).get_entropy()
        mnemonic_from_entropy = Mnemonic.from_entropy(bytes.fromhex(entropy_hex))

        assert entropy_from_mnemonic.hex() == entropy_hex
        assert mnemonic_from_entropy.get_text() == text

    test_conversion(
        text="abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about",
        entropy_hex="00000000000000000000000000000000"
    )

    test_conversion(
        text="moral volcano peasant pass circle pen over picture flat shop clap goat never lyrics gather prepare woman film husband gravity behind test tiger improve",
        entropy_hex="8fbeb688d0529344e77d225898d4a73209510ad81d4ffceac9bfb30149bf387b"
    )

    with pytest.raises(ValueError):
        Mnemonic.from_entropy(bytes.fromhex("abba"))
