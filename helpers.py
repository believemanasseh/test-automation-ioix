"""Helper functions."""


def convert_str_to_number(x: str) -> int:
    total_count = 0
    num_map = {"K": 1000, "M": 1000000, "B": 1000000000}
    if x.isdigit():
        total_count = int(x)
    else:
        if len(x) > 1:
            total_count = float(x[:-1]) * num_map.get(x[-1].upper(), 1)
    return int(total_count)
