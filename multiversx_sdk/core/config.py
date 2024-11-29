from dataclasses import dataclass


@dataclass
class LibraryConfig:
    """
    Global configuration of the library.

    Generally speaking, this configuration should only be altered in exotic use cases.
    It can be seen as a collection of constants or, more precisely, variables that are rarely changed and used throughout the library.

    Never alter the configuration within a library!
    Only alter the configuration, if needed, within a final application that uses this library.
    """

    # The human-readable part of the bech32 addresses
    default_address_hrp: str = "erd"
