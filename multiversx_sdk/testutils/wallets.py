from pathlib import Path
from typing import Dict

from multiversx_sdk.wallet.user_pem import UserPEM

alice_pem = Path(__file__).parent / "testwallets" / "alice.pem"
bob_pem = Path(__file__).parent / "testwallets" / "bob.pem"
frank_pem = Path(__file__).parent / "testwallets" / "frank.pem"
grace_pem = Path(__file__).parent / "testwallets" / "grace.pem"
carol_pem = Path(__file__).parent / "testwallets" / "carol.pem"
sender_pem = Path(__file__).parent / "testwallets" / "sender.pem"
relayer_pem = Path(__file__).parent / "testwallets" / "relayer.pem"


def load_wallets() -> Dict[str, UserPEM]:
    wallets: Dict[str, UserPEM] = {}

    alice = UserPEM.from_file(Path(alice_pem))
    wallets["alice"] = alice

    bob = UserPEM.from_file(Path(bob_pem))
    wallets["bob"] = bob

    carol = UserPEM.from_file(Path(carol_pem))
    wallets["carol"] = carol

    frank = UserPEM.from_file(Path(frank_pem))
    wallets["frank"] = frank

    grace = UserPEM.from_file(Path(grace_pem))
    wallets["grace"] = grace

    sender = UserPEM.from_file(Path(sender_pem))
    wallets["sender"] = sender

    relayer = UserPEM.from_file(Path(relayer_pem))
    wallets["relayer"] = relayer

    return wallets
