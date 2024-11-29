from multiversx_sdk.core.address import Address

#  left for compatibility reasons; will be deleted in the future
ESDT_CONTRACT_ADDRESS = Address.new_from_bech32("erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u")

METACHAIN_ID = 4294967295
MAX_UINT64 = 18446744073709551615

#  left for compatibility reasons; will be deleted in the future
DEFAULT_ADDRESS_HRP = "erd"

DEFAULT_TRANSACTION_AWAITING_POLLING_TIMEOUT_IN_MILLISECONDS = 6000
DEFAULT_TRANSACTION_AWAITING_TIMEOUT_IN_MILLISECONDS = 15 * DEFAULT_TRANSACTION_AWAITING_POLLING_TIMEOUT_IN_MILLISECONDS
DEFAULT_TRANSACTION_AWAITING_PATIENCE_IN_MILLISECONDS = 0

BASE_USER_AGENT = "multiversx-sdk-py"
UNKNOWN_CLIENT_NAME = "unknown"
