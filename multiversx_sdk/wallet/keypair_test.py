from multiversx_sdk.core.address import Address
from multiversx_sdk.core.transaction import Transaction
from multiversx_sdk.wallet.keypair import KeyPair
from multiversx_sdk.wallet.user_keys import UserSecretKey

from multiversx_sdk.core.transaction_computer import TransactionComputer


def test_create_keypair():
    buffer_hex = "413f42575f7f26fad3317a778771212fdb80245850981e48b58a4f25e344e8f9"
    buffer = bytes.fromhex(buffer_hex)

    user_secret_key = UserSecretKey(buffer)
    keypair = KeyPair.new_from_bytes(buffer)

    secret_key = keypair.get_secret_key()
    assert secret_key.hex() == buffer_hex
    assert secret_key == user_secret_key

    keypair = KeyPair(secret_key)
    assert keypair.get_secret_key() == user_secret_key
    assert keypair.get_public_key() == user_secret_key.generate_public_key()

    keypair = KeyPair.generate()
    pubkey = keypair.get_public_key()
    secret_key = keypair.get_secret_key()
    assert len(pubkey.get_bytes()) == 32
    assert len(secret_key.get_bytes()) == 32


def test_sign_and_verify_transaction():
    """
    Also see: https://github.com/multiversx/mx-chain-go/blob/master/examples/construction_test.go
    """

    tx = Transaction(
        nonce=89,
        value=0,
        receiver=Address.new_from_bech32("erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx"),
        sender=Address.new_from_bech32("erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"),
        data=None,
        gas_price=1000000000,
        gas_limit=50000,
        chain_id="local-testnet",
        version=1,
        options=0
    )

    buffer_hex = "413f42575f7f26fad3317a778771212fdb80245850981e48b58a4f25e344e8f9"
    buffer = bytes.fromhex(buffer_hex)
    keypair = KeyPair.new_from_bytes(buffer)

    transaction_computer = TransactionComputer()
    serialized_tx = transaction_computer.compute_bytes_for_signing(tx)

    tx.signature = keypair.sign(serialized_tx)
    assert tx.signature.hex() == "b56769014f2bdc5cf9fc4a05356807d71fcf8775c819b0f1b0964625b679c918ffa64862313bfef86f99b38cb84fcdb16fa33ad6eb565276616723405cd8f109"
    assert keypair.verify(serialized_tx, tx.signature)
