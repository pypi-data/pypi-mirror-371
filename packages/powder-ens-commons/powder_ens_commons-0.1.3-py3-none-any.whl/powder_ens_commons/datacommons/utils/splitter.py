import json
import random
from typing import Dict, Tuple

def split_train_test_json(
    json_data: Dict[str, dict], test_size: float = 0.2
) -> Tuple[Dict[str, dict], Dict[str, dict]]:
    """
    Split the given JSON dataset into train and test sets,
    maintaining the same proportion of one-TX and two-TX samples.

    Args:
        json_data (dict): Dictionary loaded from JSON.
        test_size (float): Fraction of data to be used as test set (e.g., 0.2).

    Returns:
        Tuple of (train_json, test_json), both as dictionaries.
    """
    one_tx_keys = [k for k, v in json_data.items() if len(v["tx_coords"]) == 1]
    two_tx_keys = [k for k, v in json_data.items() if len(v["tx_coords"]) == 2]

    print(f"Total samples: {len(json_data)}")
    print(f"One-TX samples: {len(one_tx_keys)}")
    print(f"Two-TX samples: {len(two_tx_keys)}")

    # Shuffle
    random.shuffle(one_tx_keys)
    random.shuffle(two_tx_keys)

    # Calculate split indices
    num_test_one_tx = int(len(one_tx_keys) * test_size)
    num_test_two_tx = int(len(two_tx_keys) * test_size)

    test_keys = one_tx_keys[:num_test_one_tx] + two_tx_keys[:num_test_two_tx]
    train_keys = one_tx_keys[num_test_one_tx:] + two_tx_keys[num_test_two_tx:]

    # Construct split dicts
    train_json = {k: json_data[k] for k in train_keys}
    test_json = {k: json_data[k] for k in test_keys}

    return train_json, test_json
