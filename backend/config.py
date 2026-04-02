import json
import os

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")

DEFAULT_CONFIG = {
    "zt_url": "http://localhost:9993",
    "zt_token": "",
}


def read_config() -> dict:
    if not os.path.exists(CONFIG_PATH):
        return DEFAULT_CONFIG.copy()
    with open(CONFIG_PATH) as f:
        data = json.load(f)
    return {**DEFAULT_CONFIG, **data}


def write_config(data: dict) -> dict:
    current = read_config()
    current.update(data)
    with open(CONFIG_PATH, "w") as f:
        json.dump(current, f, indent=2)
    return current
