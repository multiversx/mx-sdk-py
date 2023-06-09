from pathlib import Path
from typing import Dict

from multiversx_sdk_wallet import UserPEM

alice_pem = Path(__file__).parent / "testwallets" / "alice.pem"
bob_pem = Path(__file__).parent / "testwallets" / "bob.pem"
frank_pem = Path(__file__).parent / "testwallets" / "frank.pem"
grace_pem = Path(__file__).parent / "testwallets" / "grace.pem"


def load_wallets():
    wallets: Dict[str, UserPEM] = {}

    alice = UserPEM.from_file(Path(alice_pem))
    wallets["alice"] = alice

    bob = UserPEM.from_file(Path(bob_pem))
    wallets["bob"] = bob

    frank = UserPEM.from_file(Path(frank_pem))
    wallets["frank"] = frank

    grace = UserPEM.from_file(Path(grace_pem))
    wallets["grace"] = grace

    return wallets
