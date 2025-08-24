import json
from pathlib import Path
from typing import Any, Dict

PROFILES_PATH = Path.cwd() / "profiles.json"

def save_profile(name: str, options: Dict[str, Any]):
	profiles = load_profiles()
	profiles[name] = options
	with open(PROFILES_PATH, "w", encoding="utf-8") as f:
		json.dump(profiles, f, indent=2)

def load_profiles() -> Dict[str, Any]:
	if not PROFILES_PATH.exists():
		return {}
	with open(PROFILES_PATH, "r", encoding="utf-8") as f:
		return json.load(f)

def get_profile(name: str) -> Dict[str, Any]:
	return load_profiles().get(name, {})
# Export/import app state (stub)
