import os
import json
import tempfile
import base64
import hashlib
import hmac
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import schema

APP_NAME = "lineage_rpg"
SAVE_FILENAME = "player_data.dat"
KEY_SIZE = 32

def _generate_key() -> bytes:
    system_data = []
    system_data.append(os.getenv('USERNAME', os.getenv('USER', 'unknown')))
    
    try:
        import socket
        system_data.append(socket.gethostname())
    except Exception:
        system_data.append('localhost')
    
    system_data.append(APP_NAME)
    combined = ''.join(system_data).encode('utf-8')
    salt = hashlib.sha256(combined).digest()[:16]
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=KEY_SIZE,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(combined))
    return key

def _encrypt_data(data: str, key: bytes) -> bytes:
    fernet = Fernet(key)
    return fernet.encrypt(data.encode('utf-8'))

def _decrypt_data(encrypted_data: bytes, key: bytes) -> str:
    fernet = Fernet(key)
    return fernet.decrypt(encrypted_data).decode('utf-8')

def _calculate_integrity_hash(data: Dict[str, Any], key: bytes) -> str:
    data_str = json.dumps(data, sort_keys=True)
    return hmac.new(key, data_str.encode('utf-8'), hashlib.sha256).hexdigest()

def _verify_integrity_hash(data: Dict[str, Any], stored_hash: str, key: bytes) -> bool:
    calculated_hash = _calculate_integrity_hash(data, key)
    return hmac.compare_digest(calculated_hash, stored_hash)

def _get_save_directory() -> Path:
    if os.name == 'nt':
        base_dir = os.getenv('LOCALAPPDATA') or os.getenv('APPDATA') or os.path.expanduser("~")
    else:
        base_dir = os.getenv('XDG_DATA_HOME') or os.path.expanduser("~/.local/share")
    
    return Path(base_dir) / APP_NAME

SAVE_DIR = _get_save_directory()
SAVE_FILE = SAVE_DIR / SAVE_FILENAME

def _validate_save_data(data: Dict[str, Any]) -> bool:
    if not isinstance(data, dict):
        return False
    
    try:
        for key, expected_value in schema.DATA_SCHEMA.items():
            if key not in data:
                return False
            
            if not isinstance(data[key], type(expected_value)):
                if data[key] is not None:
                    return False
        return True
    except Exception:
        return False

def _merge_with_schema(data: Dict[str, Any]) -> Dict[str, Any]:
    merged_data = schema.DATA_SCHEMA.copy()
    
    def deep_merge(base: Dict, update: Dict) -> Dict:
        result = base.copy()
        for key, value in update.items():
            if (key in result and 
                isinstance(result[key], dict) and 
                isinstance(value, dict)):
                result[key] = deep_merge(result[key], value)
            else:
                result[key] = value
        return result
    
    return deep_merge(merged_data, data)

def load_save() -> Dict[str, Any]:
    if not SAVE_FILE.exists():
        return schema.DATA_SCHEMA.copy()
    
    try:
        key = _generate_key()
        
        with SAVE_FILE.open('rb') as f:
            encrypted_content = f.read()
        
        try:
            decrypted_content = _decrypt_data(encrypted_content, key)
        except Exception:
            print("Your save file appears to be corrupted or tampered with. Your data has been reset.")
            return schema.DATA_SCHEMA.copy()
        
        save_container = json.loads(decrypted_content)
        
        if not isinstance(save_container, dict) or 'data' not in save_container or 'hash' not in save_container:
            print("Your save file appears to be corrupted or tampered with. Your data has been reset.")
            return schema.DATA_SCHEMA.copy()
        
        data = save_container['data']
        stored_hash = save_container['hash']
        
        if not _verify_integrity_hash(data, stored_hash, key):
            print("Your save file appears to be corrupted or tampered with. Your data has been reset.")
            return schema.DATA_SCHEMA.copy()
        
        if not _validate_save_data(data):
            print("Your save file appears to be corrupted or tampered with. Your data has been reset.")
            return schema.DATA_SCHEMA.copy()
        
        merged_data = _merge_with_schema(data)
        return merged_data
        
    except Exception:
        print("Your save file appears to be corrupted or tampered with. Your data has been reset.")
        return schema.DATA_SCHEMA.copy()

def save_data(data: Dict[str, Any]) -> bool:
    try:
        if not _validate_save_data(data):
            return False
        
        SAVE_DIR.mkdir(parents=True, exist_ok=True)
        
        key = _generate_key()
        integrity_hash = _calculate_integrity_hash(data, key)
        
        save_container = {
            'data': data,
            'hash': integrity_hash,
            'version': 1,
            'timestamp': datetime.now().isoformat()
        }
        
        json_data = json.dumps(save_container, ensure_ascii=False, sort_keys=True)
        encrypted_data = _encrypt_data(json_data, key)
        
        with tempfile.NamedTemporaryFile(
            mode='wb',
            suffix='.tmp',
            dir=SAVE_DIR,
            delete=False
        ) as temp_file:
            temp_file.write(encrypted_data)
            temp_path = temp_file.name
        
        if os.name == 'nt':
            if SAVE_FILE.exists():
                SAVE_FILE.unlink()
        
        Path(temp_path).rename(SAVE_FILE)
        return True
        
    except Exception:
        try:
            if 'temp_path' in locals():
                Path(temp_path).unlink(missing_ok=True)
        except Exception:
            pass
        
        return False