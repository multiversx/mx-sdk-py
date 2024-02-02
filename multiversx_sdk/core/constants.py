TRANSACTION_MIN_GAS_PRICE = 1000000000
TRANSACTION_VERSION_DEFAULT = 2
TRANSACTION_OPTIONS_DEFAULT = 0
ARGS_SEPARATOR = "@"
METACHAIN_ID = 4294967295
VM_TYPE_WASM_VM = bytes([0x05, 0x00])

# 64 bytes = 512 bits
INTEGER_MAX_NUM_BYTES = 64

EGLD_TOKEN_IDENTIFIER = "EGLD"
EGLD_NUM_DECIMALS = 18

DELEGATION_MANAGER_SC_ADDRESS = "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqylllslmq6y6"
DEFAULT_HRP = "erd"
CONTRACT_DEPLOY_ADDRESS = "erd1qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq6gq4hu"
TRANSACTION_OPTIONS_TX_GUARDED = 0b0010

DIGEST_SIZE = 32

TOKEN_RANDOM_SEQUENCE_LENGTH = 6

# Sentinel: 2 (2 ^ 1)
testVectors1 = [
    [-1, 0XFF],
    [1, 0X01],
    [2, 0X02],
    [-2, 0XFE],
    [3, 0X03],
    [-3, 0XFD],
    [4, 0X04],
    [-4, 0XFC],
]

# Sentinel: 4 (2 ^ 2)
testVectors2 = [
    [-1, 0XFF],
    [1, 0X01],
    [2, 0X02],
    [-2, 0XFE],
    [3, 0X03],
    [-3, 0XFD],
    [4, 0X04],
    [-4, 0XFC],
    [5, 0X05],
    [-5, 0XFB],
    [6, 0X06],
    [-6, 0XFA],
]

# Sentinel: 128 (2 ^ 7)
testVectors3 = [
    [125, 0X7D],
    [-125, 0X83],
    [126, 0X7E],
    [-126, 0X82],
    [127, 0X7F],
    [-127, 0X81],
    [-128, 0X80],
]

# Sentinel: 256 (2 ^ 8)
testVectors4 = [
    [128, [0x00, 0x80]],
    [129, [0x00, 0x81]],
    [-129, [0xFF, 0x7F]],
    [130, [0x00, 0x82]],
    [-130, [0xFF, 0x7E]],
    [253, [0x00, 0xFD]],
    [256, [0x01, 0x00]],
    [-256, [0xFF, 0x00]],
    [-257, [0xFE, 0xFF]],
    [258, [0x01, 0x02]],
]
