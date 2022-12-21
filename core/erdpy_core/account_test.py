
from erdpy_core.account import AccountNonceHolder
from erdpy_core.address import Address


def test_account_nonce_holder():
    address = Address.from_bech32("erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th")
    account = AccountNonceHolder(address)
    account.nonce = 42
    assert account.get_nonce_then_increment() == 42
    assert account.get_nonce_then_increment() == 43

    account.increment_nonce()
    account.increment_nonce()
    account.increment_nonce()
    assert account.nonce == 47
