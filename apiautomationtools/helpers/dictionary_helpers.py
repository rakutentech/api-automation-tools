import re


def flatten(d: dict | list) -> dict:
    """
    This flattens a nested dictionary.

    Args:
        d: The object to flatten.

    Returns:
        flat_d: The flattened object.
    """

    def recurse(value, parent_key=""):
        if isinstance(value, list):
            for i in range(len(value)):
                recurse(value[i], f"{parent_key}.{str(i)}" if parent_key else str(i))
        elif isinstance(value, dict):
            for k, v in value.items():
                recurse(v, f"{parent_key}.{k}" if parent_key else k)
        else:
            obj[parent_key] = value

    obj = {}
    recurse(d)
    return obj


def unflatten(d: dict | list) -> dict:
    """
    This unflattens a flattened dictionary.

    Args:
        d: The object to flatten.

    Returns:
        items: The unflattened object.
    """
    items = {}
    for k, v in d.items():
        keys = k.split(".")
        sub_items = items

        index = None
        if keys[-1].isdigit():
            index = int(keys[-1])
        list_action = type(index) is int

        for ki in keys[:-1]:
            try:
                sub_items = sub_items[ki]
            except KeyError:
                if list_action:
                    sub_items[ki] = []
                else:
                    sub_items[ki] = {}
                sub_items = sub_items[ki]
        if list_action:
            sub_items.insert(index, v)
        else:
            sub_items[keys[-1]] = v
    return items


def compare_dictionaries(
    d1: dict,
    d2: dict,
    skipped_keys: None | list = None,
    exclusive_keys: None | list = None,
    normalize: bool = False,
) -> dict:
    """
    This does a general key then value mismatch comparison of two dictionaries.

    Args:
        d1: The first dictionary to compare.
        d2: The second dictionary to compare.
        skipped_keys: The keys to skip in the comparison.
        exclusive_keys: The keys to exclusively check ignoring any skipped keys passed.
        normalize: Whether to convert each of the comparable values in the same casing.

    Returns:
        mismatches: The record of any key and value mismatches.
    """
    flat_d1 = flatten(d1)
    flat_d2 = flatten(d2)
    flat_d1_keys = list(flat_d1.keys())
    flat_d2_keys = list(flat_d2.keys())
    thin_keys = set(flat_d1_keys + flat_d2_keys)
    skipped_keys = skipped_keys or []

    if skipped_keys:
        skipped_keys += [
            k for k in thin_keys if any(sk for sk in skipped_keys if sk in k)
        ]
    if exclusive_keys:
        skipped_keys += [
            key for key in thin_keys if len(re.split("|".join(exclusive_keys), key)) < 2
        ]

    mismatches = {}
    f1_not_in_f2 = (
        set(flat_d1_keys).difference(set(skipped_keys)).difference(set(flat_d2_keys))
    )
    f2_not_in_f1 = (
        set(flat_d2_keys).difference(set(skipped_keys)).difference(set(flat_d1_keys))
    )
    mismatched_keys = list(f1_not_in_f2) + list(f2_not_in_f1)

    mismatched_skipped_keys = mismatched_keys + skipped_keys
    if normalize:
        flat_d1 = {
            k: v.lower() if type(v) is str else v
            for k, v in flat_d1.items()
            if k not in mismatched_skipped_keys
        }
        flat_d2 = {
            k: v.lower() if type(v) is str else v
            for k, v in flat_d2.items()
            if k not in mismatched_skipped_keys
        }
    mismatched_values = [
        {"key": k, "d1": v, "d2": flat_d2[k]}
        for k, v in flat_d1.items()
        if k not in mismatched_skipped_keys and v != flat_d2[k]
    ]

    if mismatched_keys:
        keys = {"f1_not_in_f2": list(f1_not_in_f2), "f2_not_in_f1": list(f2_not_in_f1)}
        mismatches["keys"] = [{k: v for k, v in keys.items() if v}]
    if mismatched_values:
        mismatches["values"] = mismatched_values
    if skipped_keys:
        mismatches["skipped_keys"] = skipped_keys
    return mismatches
