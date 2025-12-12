# features.py  (NEW)
import asyncio, os, time
from datetime import datetime, timedelta
from config import Config
from database import cleanup_old_files_older_than, _users
# background tasks: cleaner and expiry reminder

async def auto_cleaner_task(interval_minutes: int = 60):
    while True:
        try:
            deleted = await cleanup_old_files_older_than(48)
            print(f"[auto_cleaner] deleted {deleted} old DB file records")
            dl = Config.DOWNLOAD_LOCATION
            now = time.time()
            if os.path.isdir(dl):
                for filename in os.listdir(dl):
                    path = os.path.join(dl, filename)
                    try:
                        if os.path.isfile(path) and now - os.path.getmtime(path) > 48 * 3600:
                            os.remove(path)
                    except Exception:
                        pass
        except Exception as e:
            print("[auto_cleaner] error:", e)
        await asyncio.sleep(interval_minutes * 60)

async def premium_expiry_notify_task(check_interval_minutes: int = 60, bot=None):
    while True:
        try:
            cutoff_start = datetime.utcnow()
            cutoff_end = cutoff_start + timedelta(days=2)
            cursor = _users.find({"premium": True, "premium_expiry": {"$exists": True, "$lte": cutoff_end}})
            async for user in cursor:
                expiry = user.get("premium_expiry")
                if expiry and expiry > datetime.utcnow():
                    if not user.get("reminder_sent"):
                        try:
                            await bot.send_message(
                                int(user["_id"]),
                                "⏳ <b>Premium Expiry Reminder</b>\n\n"
                                f"Your premium will expire on <b>{expiry.strftime('%d-%m-%Y')}</b>.\n"
                                "Renew now to avoid interruption ▶ /buy 🚀"
                            )
                            await _users.update_one({"_id": user["_id"]}, {"$set": {"reminder_sent": True}})
                        except Exception:
                            pass
        except Exception as e:
            print("[expiry_task] error:", e)
        await asyncio.sleep(check_interval_minutes * 60)

async def do_broadcast(bot, message_text, batch_size=50, delay_seconds=0.5):
    sent = 0
    failed = 0
    cursor = _users.find({})
    async for u in cursor:
        uid = u["_id"]
        try:
            await bot.send_message(uid, message_text)
            sent += 1
        except Exception:
            failed += 1
        await asyncio.sleep(delay_seconds)
    return sent, failed
