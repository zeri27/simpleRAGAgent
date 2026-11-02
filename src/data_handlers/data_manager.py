from pathlib import Path
import hashlib
import json

PROJECT_ROOT = Path(__file__).resolve().parents[2]
STORAGE_DIR = PROJECT_ROOT / "storage"
DATA_DIR = PROJECT_ROOT / "data"
MANIFEST_PATH = STORAGE_DIR / "manifest.json"

def hash_file(path):
    # Hashes a file and returns the hash value (string).
    hasher = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hasher.update(chunk)
    return hasher.hexdigest()

def load_manifest():
    if MANIFEST_PATH.exists():
        with MANIFEST_PATH.open("r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def scan():
    # Reads raw data files and hashes them to create a fresh manifest. 
    manifest = {}

    for file_path in DATA_DIR.rglob("*"):
        if file_path.is_file():
            file_hash = hash_file(file_path)
            relative_path = str(file_path.relative_to(DATA_DIR))
            manifest[relative_path] = file_hash
    
    # Write the updated manifest back to the file
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    with MANIFEST_PATH.open("w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=4)

    return manifest
