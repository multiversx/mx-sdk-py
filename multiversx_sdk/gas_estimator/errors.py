class GasLimitEstimationError(Exception):
    def __init__(self, error: Exception) -> None:
        super().__init__(f"Failed to estimate gas limit: [{str(error)}]")
        self.error = error
