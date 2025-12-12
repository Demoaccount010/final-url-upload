# database.py (FIXED & EXTENDED)
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

DAILY_LIMIT = int(getattr(Config, "DAILY_LIMIT", 5))


async def _ensure_user(user_id: int):
    user = await _users.find_one({"_id": user_id})
    if not user:
        user = {
            "_id": user_id,
            "premium": False,
            "premium_expiry": None,
            "limit_used": 0,
            "last_reset": datetime.utcnow(),
            "limit_custom": None,
            "referred_by": None,
            "ref_count": 0,
            "reminder_sent": False
        }
        await _users.insert_one(user)
    else:
        # normalize last_reset if stored as string
        if isinstance(user.get("last_reset"), str):
            try:
                user["last_reset"] = datetime.fromisoformat(user["last_reset"])
            except Exception:
                user["last_reset"] = datetime.utcnow()
    return user


async def _reset_if_needed(user):
    # ensure last_reset is datetime
    if not user.get("last_reset"):
        user["last_reset"] = datetime.utcnow()
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
    """
    Returns True if user is allowed to proceed (and consumes 1 for non-premium).
    """
    user = await _ensure_user(user_id)
    user = await _reset_if_needed(user)

    # auto-check expiry and update premium flag
    await _auto_check_and_clear_expiry(user)

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

    # Ensure expiry handled
    await _auto_check_and_clear_expiry(user)

    limit = user.get("limit_custom") or DAILY_LIMIT
    return {"limit_used": user.get("limit_used", 0), "daily_limit": limit}


# -----------------------
# premium functions
# -----------------------
async def set_premium(user_id: int, status: bool = True):
    """
    Simple boolean premium toggle.
    If status is False, clear expiry and reminder flags.
    If status is True, keep premium_expiry as-is (could be None).
    """
    await _ensure_user(user_id)
    if status:
        # set premium True but do not set expiry (unlimited)
        await _users.update_one({"_id": user_id}, {"$set": {"premium": True, "reminder_sent": False}})
    else:
        # remove premium and clear expiry/reminder
        await _users.update_one({"_id": user_id}, {"$set": {"premium": False, "premium_expiry": None, "reminder_sent": False}})


async def is_premium(user_id: int) -> bool:
    """
    Returns True if the user currently has premium (and not expired).
    Also clears premium flag if expiry is over.
    """
    user = await _ensure_user(user_id)
    # check expiry
    expiry = user.get("premium_expiry")
    if expiry:
        if isinstance(expiry, str):
            try:
                expiry = datetime.fromisoformat(expiry)
            except Exception:
                expiry = None
        if expiry:
            if datetime.utcnow() > expiry:
                # expired -> clear premium
                await _users.update_one({"_id": user_id}, {"$set": {"premium": False, "premium_expiry": None}})
                return False
            else:
                return True
    return bool(user.get("premium", False))


async def set_premium_days(user_id: int, days: int):
    """
    Grant premium for `days` days (expiry stored).
    Returns expiry datetime.
    """
    await _ensure_user(user_id)
    expiry = datetime.utcnow() + timedelta(days=int(days))
    await _users.update_one(
        {"_id": user_id},
        {"$set": {"premium": True, "premium_expiry": expiry, "reminder_sent": False}},
        upsert=True
    )
    return expiry


async def _auto_check_and_clear_expiry(user):
    """
    Internal helper: given a user dict, check expiry and clear if expired.
    """
    expiry = user.get("premium_expiry")
    if not expiry:
        return False
    # parse if str
    if isinstance(expiry, str):
        try:
            expiry = datetime.fromisoformat(expiry)
        except Exception:
            return False
    if expiry and datetime.utcnow() > expiry:
        await _users.update_one({"_id": user["_id"]}, {"$set": {"premium": False, "premium_expiry": None}})
        return True
    return False


async def check_expiry_and_update(user_id: int):
    """
    Public function: checks a user's expiry and updates DB.
    Returns True if we cleared an expired premium.
    """
    user = await _ensure_user(user_id)
    return await _auto_check_and_clear_expiry(user)


async def get_premium_expiry(user_id: int):
    """
    Returns expiry datetime or None. Also auto-clears expired.
    """
    user = await _ensure_user(user_id)
    expiry = user.get("premium_expiry")
    if not expiry:
        return None
    if isinstance(expiry, str):
        try:
            expiry = datetime.fromisoformat(expiry)
        except Exception:
            expiry = None
    if expiry:
        if datetime.utcnow() > expiry:
            # expired: clear and return None
            await _users.update_one({"_id": user_id}, {"$set": {"premium": False, "premium_expiry": None}})
            return None
        return expiry
    return None


# alias functions for compatibility with commands variants
async def activate_premium(user_id: int, days: int):
    return await set_premium_days(user_id, days)


async def remove_premium_db(user_id: int):
    return await set_premium(user_id, False)


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
    used_by = doc.get("used_by", [])
    if user_id in used_by:
        return False, "Already used"
    await _promo.update_one({"code": code}, {"$push": {"used_by": user_id}})
    # grant premium days
    expiry = await set_premium_days(user_id, doc["days"])
    return True, expiry


# referrals
async def create_referral(user_id: int, referred_by: int):
    await _ensure_user(user_id)
    if referred_by:
        # set referred_by only if not already set
        user = await _users.find_one({"_id": user_id})
        if not user.get("referred_by"):
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
