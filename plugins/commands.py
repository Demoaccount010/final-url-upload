from pyrogram import Client, filters
from pyrogram.types import Message
from plugins.script import Translation
from config import Config
from database import (
    set_premium, get_usage, is_premium, create_promo, use_promo,
    get_stats, set_custom_limit, get_premium_expiry, create_referral, get_ref_count
)
import database  # to check for activate_premium at runtime
from features import do_broadcast


# ================================================================
# START
# ================================================================
@Client.on_message(filters.command("start") & filters.private)
async def start_bot(_bot, m: Message):
    text = Translation.START_TEXT.replace("{mention}", m.from_user.mention)
    return await m.reply_text(
        text,
        reply_markup=Translation.START_BUTTONS,
        disable_web_page_preview=True,
        quote=True
    )


# ================================================================
# HELP
# ================================================================
@Client.on_message(filters.command("help") & filters.private)
async def help_bot(_bot, m: Message):
    return await m.reply_text(
        Translation.HELP_TEXT,
        reply_markup=Translation.HELP_BUTTONS,
        disable_web_page_preview=True
    )


# ================================================================
# ABOUT
# ================================================================
@Client.on_message(filters.command("about") & filters.private)
async def aboutme(_bot, m: Message):
    return await m.reply_text(
        Translation.ABOUT_TEXT,
        reply_markup=Translation.ABOUT_BUTTONS,
        disable_web_page_preview=True
    )


# ================================================================
# BUY
# ================================================================
@Client.on_message(filters.command("buy") & filters.private)
async def buy(bot, m):
    return await m.reply_text(
        "💎 <b>Premium Plans</b>\n\n"
        "🔹 Unlimited Uploads\n"
        "🔹 No Daily Limit\n"
        "🔹 Fast Processing ⚡\n\n"
        f"📞 Contact Owner: <code>{Config.OWNER_ID}</code>"
    )


# ================================================================
# PREMIUM CONTROL: give/removepremium
# Usage: /givepremium <user_id> [days]
# ================================================================
@Client.on_message(filters.command("givepremium") & filters.private)
async def give_premium(bot, m):
    # only owner
    try:
        owner_id = int(Config.OWNER_ID)
    except:
        return await m.reply_text("⚠️ OWNER_ID not set in config!")

    if m.from_user.id != owner_id:
        return await m.reply_text("❌ Only owner can use this command.")

    parts = m.text.strip().split()
    if len(parts) < 2:
        return await m.reply_text("Usage: /givepremium <user_id> [days]")

    try:
        target = int(parts[1])
    except:
        return await m.reply_text("❌ Invalid user ID.")

    # days optional: if provided and database.activate_premium exists, use it
    days = None
    if len(parts) >= 3:
        try:
            days = int(parts[2])
        except:
            days = None

    if days and hasattr(database, "activate_premium"):
        # use expiry-based activation
        expiry = await database.activate_premium(target, days)
        # owner confirmation (styled)
        await m.reply_text(
            "🎉 <b>Premium Activated</b>\n\n"
            f"👤 User: <code>{target}</code>\n"
            f"⏳ Duration: <b>{days} day(s)</b>\n"
            f"📅 Expires: <b>{expiry.strftime('%d-%m-%Y')}</b>\n\n"
            "✅ User has been notified (if not blocked)."
        )
        # notify the user
        try:
            await bot.send_message(
                target,
                "🎉 <b>Congratulations — Premium Activated!</b>\n\n"
                "💎 You now have Premium access. Enjoy unlimited uploads, faster processing and priority.\n\n"
                f"📅 Valid Until: <b>{expiry.strftime('%d-%m-%Y')}</b>\n\n"
                "👉 Thank you for using the bot!"
            )
        except Exception:
            # user might have blocked the bot / cannot be messaged
            pass

    else:
        # fallback: plain boolean premium (no expiry)
        await set_premium(target, True)
        await m.reply_text(
            "🎉 <b>Premium Activated</b>\n\n"
            f"👤 User: <code>{target}</code>\n"
            "⏳ Duration: <b>Unlimited / Not set</b>\n\n"
            "✅ User has been notified (if not blocked)."
        )
        try:
            await bot.send_message(
                target,
                "🎉 <b>Your account has been granted Premium!</b>\n\n"
                "💎 Enjoy unlimited uploads & faster processing. If you think this is a mistake, contact the owner."
            )
        except Exception:
            pass


@Client.on_message(filters.command("removepremium") & filters.private)
async def remove_premium(bot, m):
    try:
        owner_id = int(Config.OWNER_ID)
    except:
        return await m.reply_text("⚠️ OWNER_ID missing!")

    if m.from_user.id != owner_id:
        return await m.reply_text("❌ Only owner can use this command.")

    parts = m.text.strip().split()
    if len(parts) < 2:
        return await m.reply_text("Usage: /removepremium <user_id>")

    try:
        target = int(parts[1])
    except:
        return await m.reply_text("❌ Invalid user ID.")

    # try to remove expiry if function exists, else boolean
    if hasattr(database, "remove_premium_db"):
        await database.remove_premium_db(target)
    else:
        await set_premium(target, False)

    await m.reply_text(
        "🗑 <b>Premium Removed</b>\n\n"
        f"👤 User: <code>{target}</code>\n"
        "✅ User's premium access has been revoked."
    )
    try:
        await bot.send_message(
            target,
            "⚠️ <b>Your Premium access has been removed by the owner.</b>\n\n"
            "If you think this is a mistake, please contact the owner."
        )
    except Exception:
        pass


# ================================================================
# CREATE PROMO
# Usage: /createcode [days] [CODE]
# ================================================================
@Client.on_message(filters.command("createcode") & filters.private)
async def create_code(bot, m):
    try:
        owner = int(Config.OWNER_ID)
    except:
        return await m.reply_text("⚠️ OWNER_ID not configured!")

    if m.from_user.id != owner:
        return await m.reply_text("❌ Only owner can create promo codes.")

    parts = m.text.split()
    days = 7
    code = None

    if len(parts) >= 2:
        try:
            days = int(parts[1])
        except:
            days = 7
    if len(parts) >= 3:
        code = parts[2].strip().upper()

    doc = await create_promo(code, days)
    return await m.reply_text(
        "🎁 <b>Promo Created</b>\n\n"
        f"🔑 Code: <code>{doc['code']}</code>\n"
        f"📅 Valid: <b>{days} day(s)</b>\n\n"
        "👉 Users can redeem with <code>/redeem CODE</code>"
    )


# ================================================================
# REDEEM
# Usage: /redeem CODE
# ================================================================
@Client.on_message(filters.command("redeem") & filters.private)
async def redeem_code(bot, m):
    parts = m.text.split()
    if len(parts) < 2:
        return await m.reply_text("Usage: /redeem <CODE>")

    code = parts[1].strip().upper()
    ok, res = await use_promo(code, m.from_user.id)

    if not ok:
        return await m.reply_text(f"❌ {res}")

    expiry = res
    return await m.reply_text(
        "🎉 <b>Promo Applied!</b>\n\n"
        f"💎 You have Premium until: <b>{expiry.strftime('%d-%m-%Y')}</b>\n"
        "Enjoy unlimited uploads 🚀"
    )


# ================================================================
# BROADCAST
# ================================================================
@Client.on_message(filters.command("broadcast") & filters.private)
async def broadcast_cmd(bot, m):
    try:
        owner = int(Config.OWNER_ID)
    except:
        return await m.reply_text("⚠️ OWNER_ID not configured!")

    if m.from_user.id != owner:
        return await m.reply_text("❌ Only owner can broadcast.")

    msg = m.text.partition(" ")[2]
    if not msg:
        return await m.reply_text("Usage: /broadcast <message>")

    await m.reply_text("📣 Broadcasting started…")
    sent, failed = await do_broadcast(bot, msg)

    return await m.reply_text(
        "📡 <b>Broadcast Finished</b>\n\n"
        f"✅ Sent: <b>{sent}</b>\n"
        f"❌ Failed: <b>{failed}</b>"
    )


# ================================================================
# STATS
# ================================================================
@Client.on_message(filters.command("stats") & filters.private)
async def stats_cmd(bot, m):
    try:
        owner = int(Config.OWNER_ID)
    except:
        return await m.reply_text("⚠️ OWNER_ID not configured!")

    if m.from_user.id != owner:
        return await m.reply_text("❌ Only owner can view stats.")

    stats = await get_stats()
    return await m.reply_text(
        "📊 <b>Bot Stats</b>\n\n"
        f"👥 Users: <b>{stats.get('total_users', 0)}</b>\n"
        f"💎 Premium: <b>{stats.get('premium_users', 0)}</b>\n"
        f"📁 Files: <b>{stats.get('files_count', 0)}</b>"
    )


# ================================================================
# SET LIMIT
# ================================================================
@Client.on_message(filters.command("setlimit") & filters.private)
async def set_limit_cmd(bot, m):
    try:
        owner = int(Config.OWNER_ID)
    except:
        return await m.reply_text("⚠️ OWNER_ID not configured!")

    if m.from_user.id != owner:
        return await m.reply_text("❌ Only owner can set limits.")

    parts = m.text.split()
    if len(parts) != 3:
        return await m.reply_text("Usage: /setlimit <user_id> <limit>")

    target = int(parts[1])
    limit = int(parts[2])
    await set_custom_limit(target, limit)

    return await m.reply_text(
        "⚙️ <b>Limit Updated</b>\n\n"
        f"👤 User: <code>{target}</code>\n"
        f"🔢 New Limit: <b>{limit}</b> per day"
    )


# ================================================================
# PROFILE
# ================================================================
@Client.on_message(filters.command("profile") & filters.private)
async def profile_cmd(bot, m):
    usage = await get_usage(m.from_user.id)
    expiry = await get_premium_expiry(m.from_user.id)
    ref = await get_ref_count(m.from_user.id)

    expiry_text = expiry.strftime("%d-%m-%Y") if expiry else "Not Premium"

    return await m.reply_text(
        "👤 <b>Your Profile</b>\n\n"
        f"🆔 ID: <code>{m.from_user.id}</code>\n"
        f"📊 Used Today: <b>{usage.get('limit_used')}</b> / <b>{usage.get('daily_limit')}</b>\n"
        f"💎 Premium: <b>{expiry_text}</b>\n"
        f"🔗 Referrals: <b>{ref}</b>\n\n"
        "⚡ <b>Enjoy your premium features!</b>"
    )


# ================================================================
# REFERRAL
# ================================================================
@Client.on_message(filters.command("ref") & filters.private)
async def ref_cmd(bot, m):
    parts = m.text.split()
    if len(parts) != 2:
        return await m.reply_text("Usage: /ref <referrer_user_id>")

    referrer = int(parts[1])
    await create_referral(m.from_user.id, referrer)

    return await m.reply_text("🎉 Referral added successfully!")
