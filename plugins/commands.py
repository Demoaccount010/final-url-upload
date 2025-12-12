from pyrogram import Client, filters
from pyrogram.types import Message
from plugins.script import Translation


# ---------------------- START ----------------------
@Client.on_message(
    filters.command("start") & filters.private,
)
async def start_bot(_bot, m: Message):
    return await m.reply_text(
        Translation.START_TEXT.format(mention=m.from_user.mention),
        reply_markup=Translation.START_BUTTONS,
        disable_web_page_preview=True,
        quote=True,
        parse_mode="HTML"
    )


# ---------------------- HELP ----------------------
@Client.on_message(
    filters.command("help") & filters.private,
)
async def help_bot(_bot, m: Message):
    return await m.reply_text(
        Translation.HELP_TEXT,
        reply_markup=Translation.HELP_BUTTONS,
        disable_web_page_preview=True,
        parse_mode="HTML"
    )


# ---------------------- ABOUT ----------------------
@Client.on_message(
    filters.command("about") & filters.private,
)
async def aboutme(_bot, m: Message):
    return await m.reply_text(
        Translation.ABOUT_TEXT,
        reply_markup=Translation.ABOUT_BUTTONS,
        disable_web_page_preview=True,
        parse_mode="HTML"
    )


# ---------------------- BUY ----------------------
from config import Config
from database import set_premium, get_usage, is_premium
from pyrogram import filters

@Client.on_message(filters.command("buy") & filters.private)
async def buy(bot, m):
    return await m.reply_text(
        "**Premium Plans 💎**\n\n"
        "🔹 Unlimited Uploads\n"
        "🔹 No daily limit\n"
        "🔹 Fast processing\n\n"
        f"Contact owner: {Config.OWNER_ID}",
        disable_web_page_preview=True,
        parse_mode="HTML"
    )


# ---------------------- PREMIUM CONTROL ----------------------
@Client.on_message(filters.command("givepremium") & filters.private)
async def give_premium(bot, m):
    try:
        owner_id = int(Config.OWNER_ID)
    except Exception:
        return await m.reply_text("Owner not configured in Config. OWNER_ID missing.", parse_mode="HTML")

    if m.from_user.id != owner_id:
        return await m.reply_text("Only owner can run this command.", parse_mode="HTML")

    parts = m.text.strip().split()
    if len(parts) < 2:
        return await m.reply_text("Usage: /givepremium <user_id>", parse_mode="HTML")

    try:
        target = int(parts[1])
    except:
        return await m.reply_text("Invalid user id. Usage: /givepremium <user_id>", parse_mode="HTML")

    await set_premium(target, True)
    return await m.reply_text(f"User <code>{target}</code> ko PREMIUM de diya gaya ✅", parse_mode="HTML")


@Client.on_message(filters.command("removepremium") & filters.private)
async def remove_premium(bot, m):
    try:
        owner_id = int(Config.OWNER_ID)
    except Exception:
        return await m.reply_text("Owner not configured in Config. OWNER_ID missing.", parse_mode="HTML")

    if m.from_user.id != owner_id:
        return await m.reply_text("Only owner can run this command.", parse_mode="HTML")

    parts = m.text.strip().split()
    if len(parts) < 2:
        return await m.reply_text("Usage: /removepremium <user_id>", parse_mode="HTML")

    try:
        target = int(parts[1])
    except:
        return await m.reply_text("Invalid user id. Usage: /removepremium <user_id>", parse_mode="HTML")

    await set_premium(target, False)
    return await m.reply_text(f"User <code>{target}</code> ka PREMIUM hata diya gaya ✅", parse_mode="HTML")


# ---------------------- PROMO / REFERRAL / STATS ----------------------
from config import Config
from database import create_promo, use_promo, get_stats, set_custom_limit, get_usage, get_premium_expiry, create_referral, get_ref_count
from features import do_broadcast
from pyrogram import filters


@Client.on_message(filters.command("createcode") & filters.private)
async def create_code(bot, m):
    owner = int(Config.OWNER_ID)
    if m.from_user.id != owner:
        return await m.reply_text("❌ Only owner can create promo codes.", parse_mode="HTML")

    parts = m.text.split()
    days = 7
    code = None

    if len(parts) >= 2:
        try: days = int(parts[1])
        except: pass
    if len(parts) >= 3:
        code = parts[2]

    doc = await create_promo(code, days)
    await m.reply_text(f"✅ Promo created: <code>{doc['code']}</code> for {days} days", parse_mode="HTML")


@Client.on_message(filters.command("redeem") & filters.private)
async def redeem_code(bot, m):
    parts = m.text.split()
    if len(parts) < 2:
        return await m.reply_text("Usage: /redeem <CODE>", parse_mode="HTML")

    code = parts[1].strip().upper()
    ok, res = await use_promo(code, m.from_user.id)

    if not ok:
        return await m.reply_text(f"❌ {res}", parse_mode="HTML")

    expiry = res
    await m.reply_text(f"🎉 Promo accepted! Premium active till {expiry.strftime('%d-%m-%Y')}", parse_mode="HTML")


@Client.on_message(filters.command("broadcast") & filters.private)
async def broadcast_cmd(bot, m):
    owner = int(Config.OWNER_ID)

    if m.from_user.id != owner:
        return await m.reply_text("❌ Only owner can broadcast.", parse_mode="HTML")

    txt = m.text.partition(" ")[2]
    if not txt:
        return await m.reply_text("Usage: /broadcast your message", parse_mode="HTML")

    await m.reply_text("📣 Starting broadcast...", parse_mode="HTML")
    sent, failed = await do_broadcast(bot, txt)

    await m.reply_text(f"✅ Broadcast finished. Sent: {sent} Failed: {failed}", parse_mode="HTML")


@Client.on_message(filters.command("stats") & filters.private)
async def stats_cmd(bot, m):
    owner = int(Config.OWNER_ID)

    if m.from_user.id != owner:
        return await m.reply_text("❌ Only owner can view stats.", parse_mode="HTML")

    stats = await get_stats()

    await m.reply_text(
        f"📊 <b>Bot Stats</b>\n\n"
        f"👥 Total Users: <b>{stats['total_users']}</b>\n"
        f"💎 Premium Users: <b>{stats['premium_users']}</b>\n"
        f"📁 Tracked Files: <b>{stats['files_count']}</b>",
        parse_mode="HTML"
    )


@Client.on_message(filters.command("setlimit") & filters.private)
async def set_limit_cmd(bot, m):
    owner = int(Config.OWNER_ID)

    if m.from_user.id != owner:
        return await m.reply_text("❌ Only owner can set custom limit.", parse_mode="HTML")

    parts = m.text.split()
    if len(parts) != 3:
        return await m.reply_text("Usage: /setlimit <user_id> <limit>", parse_mode="HTML")

    target = int(parts[1])
    limit = int(parts[2])

    await set_custom_limit(target, limit)
    await m.reply_text(f"✅ Limit set for <code>{target}</code> to <b>{limit}</b> daily.", parse_mode="HTML")


# ---------------------- PROFILE ----------------------
@Client.on_message(filters.command("profile") & filters.private)
async def profile_cmd(bot, m):
    usage = await get_usage(m.from_user.id)
    expiry = await get_premium_expiry(m.from_user.id)
    refc = await get_ref_count(m.from_user.id)

    expiry_text = expiry.strftime('%d-%m-%Y') if expiry else "Not Premium"

    text = (
        "👤 <b>Your Profile</b>\n\n"
        f"🆔 ID: <code>{m.from_user.id}</code>\n"
        f"🔗 Used Today: <b>{usage.get('limit_used')}</b> / <b>{usage.get('daily_limit')}</b>\n"
        f"💎 Premium Expiry: <b>{expiry_text}</b>\n"
        f"🔗 Referrals: <b>{refc}</b>\n\n"
        "⚡ Keep sharing to earn free premium!"
    )

    await m.reply_text(text, parse_mode="HTML")


# ---------------------- REFERRAL ----------------------
@Client.on_message(filters.command("ref") & filters.private)
async def ref_cmd(bot, m):
    parts = m.text.split()
    if len(parts) != 2:
        return await m.reply_text("Usage: /ref <referrer_user_id>", parse_mode="HTML")

    referrer = int(parts[1])
    await create_referral(m.from_user.id, referrer)

    await m.reply_text("🎉 Thanks! Your referral has been recorded.", parse_mode="HTML")
