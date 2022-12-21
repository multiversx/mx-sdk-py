
from erdpy_core.account import AccountNonceHolder


def test_account_nonce_holder():
    account = AccountNonceHolder(41)
    account.nonce = 42
    assert account.get_nonce_then_increment() == 42
    assert account.get_nonce_then_increment() == 43

    account.increment_nonce()
    account.increment_nonce()
    account.increment_nonce()
    assert account.nonce == 47
