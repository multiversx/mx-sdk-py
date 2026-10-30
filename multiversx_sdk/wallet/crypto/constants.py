CIPHER_ALGORITHM_AES_128_CTR = "aes-128-ctr"
KEY_DERIVATION_FUNCTION_SCRYPT = "scrypt"
RANDOM_SALT_LENGTH = 32
RANDOM_IV_LENGTH = 16
ENCRYPTOR_VERSION = 4

# Bounds for the scrypt parameters read from keystore files (the SDKs write n = 4096, r = 8, p = 1, dklen = 32).
# The key derivation runs before the MAC is checked, so these bounds limit the cost of loading a malicious file:
# at most 256 MiB of memory (128 * n * r bytes) and a few seconds of CPU.
SCRYPT_MAX_N = 2**18
SCRYPT_MAX_R = 8
SCRYPT_MAX_P = 4
SCRYPT_DKLEN = 32
