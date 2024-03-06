EGLD_NUM_DECIMALS = 18


def create_account_egld_balance(egld: int | str) -> int:
    value_as_str = str(egld) + ("0" * EGLD_NUM_DECIMALS)
    return int(value_as_str)
