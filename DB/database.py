# =============================================================================
#  CipherElite Database Abstraction Layer
#
#  Provides unified interface for MongoDB + Local JSON fallback
#  If MONGO_URI is set, uses MongoDB; otherwise uses local JSON files
#
#  Author: CipherElite Dev (@rishabhops)
#  License: MIT
# =============================================================================

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional, Union

from config.config import Config

USE_MONGO = bool(Config.MONGO_URI)
mongo_client = None
mongo_db = None


async def init_db():
    global mongo_client, mongo_db, USE_MONGO
    if not USE_MONGO:
        return
    try:
        from motor.motor_asyncio import AsyncIOMotorClient
        mongo_client = AsyncIOMotorClient(Config.MONGO_URI)
        await mongo_client.admin.command('ping')
        mongo_db = mongo_client.get_database('cipherelite')
        print("\033[1;32m[DB] MongoDB Connected Successfully\033[0m")
    except Exception as e:
        print(f"\033[1;33m[DB] MongoDB connection failed: {e}\033[0m")
        print("\033[1;33m[DB] Falling back to local JSON storage\033[0m")
        USE_MONGO = False
        mongo_client = None
        mongo_db = None


def _get_json_path(collection: str) -> Path:
    if collection in ("assistant_db", "pmpermit_db"):
        base = Path("DB")
    elif collection in ("flashvault_db", "autofwd_db", "vault_db", "updater_db", "alive_config", "ai_config"):
        base = Path("DB")
    else:
        base = Path("data")
    base.mkdir(parents=True, exist_ok=True)
    return base / f"{collection}.json"


def _load_json(collection: str) -> Dict:
    path = _get_json_path(collection)
    if path.exists():
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def _save_json(collection: str, data: Dict):
    path = _get_json_path(collection)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


async def db_get(collection: str, key: Optional[str] = None, default: Any = None) -> Any:
    if USE_MONGO and mongo_db is not None:
        try:
            col = mongo_db[collection]
            if key is None:
                doc = await col.find_one({"_id": collection})
                return doc if doc else default
            else:
                doc = await col.find_one({"_id": collection})
                if doc and key in doc:
                    return doc[key]
                return default
        except Exception:
            pass
    
    data = _load_json(collection)
    if key is None:
        return data if data else default
    return data.get(key, default)


async def db_set(collection: str, key: Union[str, Dict], value: Any = None):
    if USE_MONGO and mongo_db is not None:
        try:
            col = mongo_db[collection]
            if isinstance(key, dict):
                await col.update_one({"_id": collection}, {"$set": key}, upsert=True)
            else:
                await col.update_one({"_id": collection}, {"$set": {key: value}}, upsert=True)
            return
        except Exception:
            pass
    
    data = _load_json(collection)
    if isinstance(key, dict):
        data.update(key)
    else:
        data[key] = value
    _save_json(collection, data)


async def db_delete(collection: str, key: Optional[str] = None):
    if USE_MONGO and mongo_db is not None:
        try:
            col = mongo_db[collection]
            if key is None:
                await col.delete_one({"_id": collection})
            else:
                await col.update_one({"_id": collection}, {"$unset": {key: ""}})
            return
        except Exception:
            pass
    
    data = _load_json(collection)
    if key is None:
        path = _get_json_path(collection)
        if path.exists():
            path.unlink()
    elif key in data:
        del data[key]
        _save_json(collection, data)


async def db_push(collection: str, key: str, value: Any):
    if USE_MONGO and mongo_db is not None:
        try:
            col = mongo_db[collection]
            await col.update_one(
                {"_id": collection},
                {"$addToSet": {key: value}},
                upsert=True
            )
            return
        except Exception:
            pass
    
    data = _load_json(collection)
    if key not in data:
        data[key] = []
    if isinstance(data[key], list) and value not in data[key]:
        data[key].append(value)
    _save_json(collection, data)


async def db_pull(collection: str, key: str, value: Any):
    if USE_MONGO and mongo_db is not None:
        try:
            col = mongo_db[collection]
            await col.update_one(
                {"_id": collection},
                {"$pull": {key: value}}
            )
            return
        except Exception:
            pass
    
    data = _load_json(collection)
    if key in data and isinstance(data[key], list):
        if value in data[key]:
            data[key].remove(value)
        _save_json(collection, data)


async def db_incr(collection: str, key: str, amount: int = 1):
    if USE_MONGO and mongo_db is not None:
        try:
            col = mongo_db[collection]
            await col.update_one(
                {"_id": collection},
                {"$inc": {key: amount}},
                upsert=True
            )
            return
        except Exception:
            pass
    
    data = _load_json(collection)
    data[key] = data.get(key, 0) + amount
    _save_json(collection, data)


async def db_find(collection: str, query: Dict) -> list:
    if USE_MONGO and mongo_db is not None:
        try:
            col = mongo_db[collection]
            results = []
            async for doc in col.find(query):
                results.append(doc)
            return results
        except Exception:
            pass
    return []


async def db_collection_dump(collection: str, data: Dict):
    if USE_MONGO and mongo_db is not None:
        try:
            col = mongo_db[collection]
            await col.update_one({"_id": collection}, {"$set": data}, upsert=True)
            return
        except Exception:
            pass
    _save_json(collection, data)


async def db_collection_load(collection: str, default: Optional[Dict] = None) -> Dict:
    result = await db_get(collection)
    if result is None:
        return default if default is not None else {}
    if isinstance(result, dict):
        result.pop("_id", None)
        return result
    return default if default is not None else {}
