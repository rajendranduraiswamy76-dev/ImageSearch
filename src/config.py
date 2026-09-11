"""Load project configuration, resolving data paths relative to the config file."""
import yaml
from pathlib import Path


def load_config(config_path):
    config_path = Path(config_path).resolve()
    with open(config_path, "r") as f:
        cfg = yaml.safe_load(f)

    base_dir = config_path.parent
    for key in ("data_dir", "sqlite_path", "vector_index_path"):
        cfg[key] = str((base_dir / cfg[key]).resolve())

    Path(cfg["data_dir"]).mkdir(parents=True, exist_ok=True)
    return cfg
