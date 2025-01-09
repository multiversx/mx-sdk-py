class LedgerError(Exception):
    def __init__(self, message: str):
        super().__init__("Ledger error: " + message)
