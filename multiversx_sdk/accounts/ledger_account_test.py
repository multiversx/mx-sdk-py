import pytest

from multiversx_sdk.accounts.ledger_account import LedgerAccount
from multiversx_sdk.core.message import Message, MessageComputer
from multiversx_sdk.wallet.user_keys import UserPublicKey
from multiversx_sdk.wallet.user_verifer import UserVerifier


@pytest.mark.skip("Requires Ledger Device")
def test_sign_message():
    account = LedgerAccount()
    address = account.address

    message = Message(data=b"this is a test message")
    signature = account.sign_message(message)

    message_computer = MessageComputer()
    verifier = UserVerifier(UserPublicKey(address.get_public_key()))
    is_signed_by_account = verifier.verify(
        data=message_computer.compute_bytes_for_verifying(message), signature=signature
    )

    assert is_signed_by_account
