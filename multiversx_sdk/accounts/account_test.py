
from pathlib import Path

from multiversx_sdk.accounts.account import Account

alice = Path(__file__).parent.parent / "testutils" / "testwallets" / "alice.pem"


def test_account_nonce_holder():
    account = Account.new_from_pem(alice)
    account.nonce = 42
    assert account.get_nonce_then_increment() == 42
    assert account.get_nonce_then_increment() == 43

    account.get_nonce_then_increment()
    account.get_nonce_then_increment()
    account.get_nonce_then_increment()
    assert account.nonce == 47
