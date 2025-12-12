# database.py (EXTENDED)
import asyncio
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from config import Config
import random, string

_mongo = AsyncIOMotorClient(Config.MONGO_URL)
_db = _mongo["UploaderBot"]
_users = _db["users"]
_files = _db["files"]            # store uploaded files metadata (temporary)
_promo = _db["promo_codes"]      # promo codes collection
_ref = _db["referrals"]          # referrals collection

DAILY_LIMIT = Config.DAILY_LIMIT

async def _ensure_user(user_id: int):
    user = await _users.find_one({"_id": user_id})
    if not user:
        user = {
            "_id": user_id,
            "premium": False,
            "limit_used": 0,
            "last_reset": datetime.utcnow(),
            "limit_custom": None,
            "referred_by": None,
            "ref_count": 0
        }
        await _users.insert_one(user)
    return user

async def _reset_if_needed(user):
    if isinstance(user.get("last_reset"), str):
        try:
            user["last_reset"] = datetime.fromisoformat(user["last_reset"])
        except Exception:
            user["last_reset"] = datetime.utcnow()

    if datetime.utcnow() - user["last_reset"] > timedelta(hours=24):
        await _users.update_one(
            {"_id": user["_id"]},
            {"$set": {"limit_used": 0, "last_reset": datetime.utcnow()}}
        )
        user["limit_used"] = 0
        user["last_reset"] = datetime.utcnow()
    return user

async def consume_quota(user_id: int) -> bool:
    # returns True if allowed; consumes one for free users (or custom limit)
    user = await _ensure_user(user_id)
    user = await _reset_if_needed(user)

    if user.get("premium", False):
        return True

    limit = user.get("limit_custom") or DAILY_LIMIT
    if user.get("limit_used", 0) >= limit:
        return False

    await _users.update_one({"_id": user_id}, {"$inc": {"limit_used": 1}})
    return True

async def get_usage(user_id: int):
    user = await _ensure_user(user_id)
    user = await _reset_if_needed(user)
    limit = user.get("limit_custom") or DAILY_LIMIT
    return {"limit_used": user.get("limit_used", 0), "daily_limit": limit}

# premium functions
async def set_premium(user_id: int, status: bool = True):
    await _ensure_user(user_id)
    await _users.update_one({"_id": user_id}, {"$set": {"premium": status}})
async def is_premium(user_id: int) -> bool:
    user = await _ensure_user(user_id)
    return bool(user.get("premium", False))

async def set_premium_days(user_id: int, days: int):
    await _ensure_user(user_id)
    expiry = datetime.utcnow() + timedelta(days=days)
    await _users.update_one(
        {"_id": user_id},
        {"$set": {"premium": True, "premium_expiry": expiry, "reminder_sent": False}}
    )
    return expiry

async def check_expiry_and_update(user_id: int):
    user = await _ensure_user(user_id)
    expiry = user.get("premium_expiry")
    if user.get("premium") and expiry:
        if datetime.utcnow() > expiry:
            await _users.update_one({"_id": user_id}, {"$set": {"premium": False}})
            return True
    return False

async def get_premium_expiry(user_id: int):
    user = await _ensure_user(user_id)
    return user.get("premium_expiry")

# per-user custom limit
async def set_custom_limit(user_id: int, limit: int):
    await _ensure_user(user_id)
    await _users.update_one({"_id": user_id}, {"$set": {"limit_custom": int(limit)}})

# files logging (temporary records; will be deleted after upload or after TTL)
async def add_file_record(user_id: int, filename: str, size: int = 0, created_at: datetime = None):
    created_at = created_at or datetime.utcnow()
    rec = {"user_id": user_id, "filename": filename, "size": size, "created_at": created_at}
    await _files.insert_one(rec)
    return rec

async def remove_file_record(user_id: int, filename: str):
    await _files.delete_many({"user_id": user_id, "filename": filename})

async def cleanup_old_files_older_than(hours: int = 48):
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    res = await _files.delete_many({"created_at": {"$lt": cutoff}})
    return res.deleted_count

# promo code functions
def _make_code(length=8):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(length))

async def create_promo(code: str = None, days: int = 7):
    if not code:
        code = _make_code(8)
    doc = {"code": code, "days": int(days), "used_by": [], "created_at": datetime.utcnow()}
    await _promo.insert_one(doc)
    return doc

async def use_promo(code: str, user_id: int):
    doc = await _promo.find_one({"code": code})
    if not doc:
        return False, "Invalid code"
    if user_id in doc.get("used_by", []):
        return False, "Already used"
    await _promo.update_one({"code": code}, {"$push": {"used_by": user_id}})
    # grant premium days
    expiry = await set_premium_days(user_id, doc["days"])
    return True, expiry

# referrals
async def create_referral(user_id: int, referred_by: int):
    await _ensure_user(user_id)
    if referred_by:
        await _users.update_one({"_id": user_id}, {"$set": {"referred_by": referred_by}})
        await _users.update_one({"_id": referred_by}, {"$inc": {"ref_count": 1}})

async def get_ref_count(user_id: int):
    user = await _ensure_user(user_id)
    return user.get("ref_count", 0)

# stats (simple)
async def get_stats():
    total_users = await _users.count_documents({})
    premium_users = await _users.count_documents({"premium": True})
    files_count = await _files.count_documents({})
    return {"total_users": total_users, "premium_users": premium_users, "files_count": files_count}
