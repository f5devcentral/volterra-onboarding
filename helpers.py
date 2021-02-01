import os
import json


def readConfig(config_file: str) -> str:
    """Read the supplied JSON config config_file"""
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            data = json.load(f)
        return data
    else:
        return None


def writeConfig(config_file: str, data: str) -> str:
    """Overwrite data to the supplied JSON config config_file"""
    os.makedirs(os.path.dirname(config_file), exist_ok=True)
    with open(config_file, 'w') as f:
        f.write(json.dumps(data))
        f.close
    os.chmod(config_file, 0o600)
