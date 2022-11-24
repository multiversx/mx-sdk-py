from erdpy_wallet.mnemonic import Mnemonic


def test_generate():
    mnemonic = Mnemonic.generate()
    words = mnemonic.get_words()
    assert len(words) == 24


def test_derive_keys():
    mnemonic = Mnemonic("moral volcano peasant pass circle pen over picture flat shop clap goat never lyrics gather prepare woman film husband gravity behind test tiger improve")
    assert mnemonic.derive_key(0).hex() == "413f42575f7f26fad3317a778771212fdb80245850981e48b58a4f25e344e8f9"
    assert mnemonic.derive_key(1).hex() == "b8ca6f8203fb4b545a8e83c5384da033c415db155b53fb5b8eba7ff5a039d639"
    assert mnemonic.derive_key(2).hex() == "e253a571ca153dc2aee845819f74bcc9773b0586edead15a94cb7235a5027436"
