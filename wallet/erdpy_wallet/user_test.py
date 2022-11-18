from pathlib import Path

from erdpy_wallet.user_keys import UserSecretKey
from erdpy_wallet.user_signer import UserSigner


def test_user_secret_key_create():
    buffer_hex = "413f42575f7f26fad3317a778771212fdb80245850981e48b58a4f25e344e8f9"
    buffer = bytes.fromhex(buffer_hex)
    secret_key = UserSecretKey(buffer)
    secret_key_from_string = UserSecretKey.from_string(buffer_hex)

    assert secret_key.hex() == buffer_hex
    assert secret_key_from_string.hex() == buffer_hex


def test_user_secret_key_generate_public_key():
    assert UserSecretKey.from_string("413f42575f7f26fad3317a778771212fdb80245850981e48b58a4f25e344e8f9").generate_public_key().hex() == "0139472eff6886771a982f3083da5d421f24c29181e63888228dc81ca60d69e1"
    assert UserSecretKey.from_string("b8ca6f8203fb4b545a8e83c5384da033c415db155b53fb5b8eba7ff5a039d639").generate_public_key().hex() == "8049d639e5a6980d1cd2392abcce41029cda74a1563523a202f09641cc2618f8"
    assert UserSecretKey.from_string("e253a571ca153dc2aee845819f74bcc9773b0586edead15a94cb7235a5027436").generate_public_key().hex() == "b2a11555ce521e4944e09ab17549d85b487dcd26c84b5017a39e31a3670889ba"


def test_from_pem_file():
    assert UserSigner.from_pem_file(Path("./erdpy_wallet/testdata/alice.pem"), 0).get_address().bech32() == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
    assert UserSigner.from_pem_file(Path("./erdpy_wallet/testdata/bob.pem"), 0).get_address().bech32() == "erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx"
    assert UserSigner.from_pem_file(Path("./erdpy_wallet/testdata/carol.pem"), 0).get_address().bech32() == "erd1k2s324ww2g0yj38qn2ch2jwctdy8mnfxep94q9arncc6xecg3xaq6mjse8"


