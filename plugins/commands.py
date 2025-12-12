from pyrogram import Client, filters
from pyrogram.types import Message
from plugins.script import Translation
from config import Config
from database import (
    set_premium, get_usage, is_premium, create_promo, use_promo,
    get_stats, set_custom_limit, get_premium_expiry, create_referral, get_ref_count
)
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
        f"📞 Contact Owner: <code>{Config.OWNER_ID}</code>",
    )



# ================================================================
# PREMIUM CONTROL
# ================================================================
@Client.on_message(filters.command("givepremium") & filters.private)
async def give_premium(bot, m):

    try:
        owner_id = int(Config.OWNER_ID)
    except:
        return await m.reply_text("⚠️ OWNER_ID not set in config!")

    if m.from_user.id != owner_id:
        return await m.reply_text("❌ Only owner can use this.")

    parts = m.text.split()
    if len(parts) < 2:
        return await m.reply_text("Usage: /givepremium <user_id>")

    try:
        target = int(parts[1])
    except:
        return await m.reply_text("❌ Invalid user ID.")

    await set_premium(target, True)
    return await m.reply_text(f"✅ Premium activated for <code>{target}</code>")



@Client.on_message(filters.command("removepremium") & filters.private)
async def remove_premium(bot, m):

    try:
        owner_id = int(Config.OWNER_ID)
    except:
        return await m.reply_text("⚠️ OWNER_ID missing!")

    if m.from_user.id != owner_id:
        return await m.reply_text("❌ Only owner can use this.")

    parts = m.text.split()
    if len(parts) < 2:
        return await m.reply_text("Usage: /removepremium <user_id>")

    try:
        target = int(parts[1])
    except:
        return await m.reply_text("❌ Invalid user ID.")

    await set_premium(target, False)
    return await m.reply_text(f"🗑 Premium removed from <code>{target}</code>")



# ================================================================
# CREATE PROMO
# ================================================================
@Client.on_message(filters.command("createcode") & filters.private)
async def create_code(bot, m):

    owner = int(Config.OWNER_ID)
    if m.from_user.id != owner:
        return await m.reply_text("❌ Only owner can create promo codes.")

    parts = m.text.split()
    days = 7
    code = None

    if len(parts) >= 2:
        try:
            days = int(parts[1])
        except:
            pass
    
    if len(parts) >= 3:
        code = parts[2]

    doc = await create_promo(code, days)
    return await m.reply_text(
        f"🎁 Promo Created!\n"
        f"🔑 Code: <code>{doc['code']}</code>\n"
        f"📅 Valid: {days} days"
    )



# ================================================================
# REDEEM
# ================================================================
@Client.on_message(filters.command("redeem") & filters.private)
async def redeem_code(bot, m):

    parts = m.text.split()
    if len(parts) < 2:
        return await m.reply_text("Usage: /redeem <CODE>")

    code = parts[1].upper()
    ok, res = await use_promo(code, m.from_user.id)

    if not ok:
        return await m.reply_text(f"❌ {res}")

    expiry = res
    return await m.reply_text(
        f"🎉 Promo Applied!\nPremium until: <b>{expiry.strftime('%d-%m-%Y')}</b>"
    )



# ================================================================
# BROADCAST
# ================================================================
@Client.on_message(filters.command("broadcast") & filters.private)
async def broadcast_cmd(bot, m):

    owner = int(Config.OWNER_ID)
    if m.from_user.id != owner:
        return await m.reply_text("❌ Only owner can broadcast.")

    msg = m.text.partition(" ")[2]
    if not msg:
        return await m.reply_text("Usage: /broadcast text")

    await m.reply_text("📣 Broadcasting started…")
    sent, failed = await do_broadcast(bot, msg)

    return await m.reply_text(
        f"📡 Done!\n"
        f"✅ Sent: {sent}\n"
        f"❌ Failed: {failed}"
    )



# ================================================================
# STATS
# ================================================================
@Client.on_message(filters.command("stats") & filters.private)
async def stats_cmd(bot, m):

    owner = int(Config.OWNER_ID)
    if m.from_user.id != owner:
        return await m.reply_text("❌ Only owner can view stats.")

    stats = await get_stats()

    return await m.reply_text(
        f"📊 <b>Bot Stats</b>\n\n"
        f"👥 Users: <b>{stats['total_users']}</b>\n"
        f"💎 Premium: <b>{stats['premium_users']}</b>\n"
        f"📁 Files: <b>{stats['files_count']}</b>"
    )



# ================================================================
# SET LIMIT
# ================================================================
@Client.on_message(filters.command("setlimit") & filters.private)
async def set_limit_cmd(bot, m):

    owner = int(Config.OWNER_ID)
    if m.from_user.id != owner:
        return await m.reply_text("❌ Only owner can set limits.")

    parts = m.text.split()
    if len(parts) != 3:
        return await m.reply_text("Usage: /setlimit <user_id> <limit>")

    target = int(parts[1])
    limit = int(parts[2])

    await set_custom_limit(target, limit)

    return await m.reply_text(
        f"⚙️ Limit Updated\n"
        f"User: <code>{target}</code>\n"
        f"Limit: <b>{limit}</b> /day"
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
        f"👤 <b>Your Profile</b>\n\n"
        f"🆔 ID: <code>{m.from_user.id}</code>\n"
        f"📊 Used Today: {usage.get('limit_used')} / {usage.get('daily_limit')}\n"
        f"💎 Premium: <b>{expiry_text}</b>\n"
        f"🔗 Referrals: <b>{ref}</b>\n\n"
        f"⚡ Enjoy your experience!"
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
