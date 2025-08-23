import math
import time
from typing import Any
from decimal import Decimal


def get_timestamp_ms() -> int:
    return int(time.time() * 1000)


def is_numeric(n: Any) -> bool:
    try:
        Decimal(n)
        return True
    except ValueError:
        return False


def convert_to_numeric(data: Any) -> Any:
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, str) and is_numeric(v):
                data[k] = Decimal(v)
            else:
                data[k] = convert_to_numeric(v)
    elif isinstance(data, list):
        for i in data:
            convert_to_numeric(i)
    return data


def round_px(px: float, decimals: int) -> float | int:
    f = float(px)
    v = round_float(f, decimals)

    if abs(v - round(v)) < 1e-12:
        return int(round(v))

    if v >= 100_000:
        return int(v)

    return round(float(f"{v:.5g}"), decimals)


def round_float(value: float, decimals: int) -> float:
    v = float(value)
    return round(float(f"{v:.8g}"), decimals)


def round_token_amount(amount: float, decimals: int) -> str:
    factor = 10**decimals
    rounded = math.floor(amount * factor) / factor
    return f"{rounded:.{decimals}f}".rstrip("0").rstrip(".")
