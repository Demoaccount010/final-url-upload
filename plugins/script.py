# plugins/script.py
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton


class Translation:

    START_TEXT = """
👋✨ <b>Hey {mention}!</b>

🎉 Welcome to <b>Ultimate URL Uploader Bot</b> 🚀  
Yaha tum kisi bhi link ko — <b>Video, Audio, Document</b> —  
seedha <b>Telegram file</b> me convert kar sakte ho ⚡

🔥 <b>Features:</b>
• Direct Link ➜ Instant Upload 📤  
• High-Speed Processing ⚡  
• Premium Mode (Unlimited Uploads) 💎  
• Auto Clean System 🧹  
• Promo Codes & Referral Rewards 🎁  
• Daily Limit Tracking 📊  

💡 Start using by:  
👉 Just send me any <b>Direct URL / File Link</b>

Need help? Type /help 🆘  
Want premium? Type /buy 💎
"""

    HELP_TEXT = """
🆘✨ <b>Help Menu</b>

📥 <b>How to Upload?</b>
Bas mujhe koi bhi supported link bhejo:
• Direct File Links 📄  
• Video URLs 🎬  
• Audio URLs 🎵  
• Google Drive / Telegram Links ⚡  
Bot apne aap convert karke upload kar dega 🚀

📊 <b>Daily Limit System:</b>
• Free Users → 5 uploads/day  
• Premium Users → Unlimited 💎  
Check your usage → /usage

💎 <b>Premium Benefits:</b>
• Unlimited Uploads ♾️  
• Ultra Fast Processing ⚡  
• No Restrictions 🚫  
• Priority Queue 🎯  
• Special Rewards 🎁  
Premium buy → /buy

🔐 <b>Your Account Commands:</b>
• /profile → Your plan + usage  
• /usage → Today’s uploads  
• /redeem CODE → Promo redeem  
• /ref USERID → Add referral  

👑 <b>Owner Commands:</b>
• /stats  
• /broadcast  
• /createcode  
• /setlimit  

Need more help? Just type anything 😊
"""

    BUY_TEXT = """
💎 <b>Premium Plans</b>

Unlock next-level power 🚀:
• Unlimited Uploads ♾️  
• Turbo Processing Speed ⚡  
• No Daily Limit ❌  
• Priority Support 🎧  
• Promo Codes + Rewards 🎁  

💳 <b>Plans Available:</b>
• 7 Days → ₹39  
• 30 Days → ₹99  
• 90 Days → ₹249  

Payment via UPI:
📥 Contact Admin → @yoursmileyt

⚠️ After payment, send screenshot + your User ID.
"""

    ABOUT_TEXT = """
ℹ️ <b>About This Bot</b>

This bot converts any supported URL into a Telegram-friendly upload 🚀  
Made using Python + Pyrogram + MongoDB 💾  
Optimized with Auto Clean System 🧹  
Advanced Premium Engine + Promo Code System 🎁  

<b>♻️ My Name:</b> Url Uploader Bot  
<b>🌀 Channel:</b> <a href="https://t.me/crunchyroll_hindi_dub_yt">Join Here</a>  
<b>🌺 Heroku:</b> <a href="https://heroku.com/">Heroku</a>  
<b>📑 Language:</b> <a href="https://www.python.org/">Python 3.10.5</a>  
<b>🇵🇲 Framework:</b> <a href="https://docs.pyrogram.org/">Pyrogram 2.0.30</a>  
<b>👲 Developer:</b> <a href="https://t.me/yoursmileyt">yoursmileyt</a>  

❤️ Dedicated to users like you!
"""

    PING_TEXT = "🏓 Pong! Bot is active and running smoother than ever ⚡😎"

    PROGRESS = """
🔰 Speed : {3}/s

🌀 Done : {1}

🎥 Tᴏᴛᴀʟ sɪᴢᴇ : {2}

⏳ Tɪᴍᴇ ʟᴇғᴛ : {4}
"""

    ID_TEXT = """
🆔 Your Telegram ID 𝐢𝐬 :- <code>{}</code>
"""

    INFO_TEXT = """
🤹 First Name : <b>{}</b>
🚴‍♂️ Second Name : <b>{}</b>
🧑🏻‍🎓 Username : <b>@{}</b>
🆔 Telegram Id : <code>{}</code>
📇 Profile Link : <b>{}</b>
📡 Dc : <b>{}</b>
📑 Language : <b>{}</b>
👲 Status : <b>{}</b>
"""

    START_BUTTONS = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("❓ Help", callback_data="help"),
                InlineKeyboardButton("🦊 About", callback_data="about"),
            ],
            [InlineKeyboardButton("📛 Close", callback_data="close")],
        ]
    )

    HELP_BUTTONS = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🏠 Home", callback_data="home"),
                InlineKeyboardButton("🦊 About", callback_data="about"),
            ],
            [InlineKeyboardButton("📛 Close", callback_data="close")],
        ]
    )

    ABOUT_BUTTONS = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🏠 Home", callback_data="home"),
                InlineKeyboardButton("❓ Help", callback_data="help"),
            ],
            [InlineKeyboardButton("📛 Close", callback_data="close")],
        ]
    )

    BUTTONS = InlineKeyboardMarkup(
        [[InlineKeyboardButton("📛 Close", callback_data="close")]]
    )

    FORMAT_SELECTION = "Now Select the desired formats"
    SET_CUSTOM_USERNAME_PASSWORD = """"""
    DOWNLOAD_START = "Trying to Download ⌛\n\n <i>{} </i>"
    UPLOAD_START = "<i>{} </i>\n\n📤 Uploading Please Wait "
    RCHD_TG_API_LIMIT = (
        "Downloaded in {} seconds.\nDetected File Size: {}\n"
        "Sorry. But, I cannot upload files greater than 2GB due to Telegram API limitations."
    )
    AFTER_SUCCESSFUL_UPLOAD_MSG_WITH_TS = (
        "Dᴏᴡɴʟᴏᴀᴅᴇᴅ ɪɴ {} sᴇᴄᴏɴᴅs.\n\nTʜᴀɴᴋs Fᴏʀ Usɪɴɢ Mᴇ\n\nUᴘʟᴏᴀᴅᴇᴅ ɪɴ {} sᴇᴄᴏɴᴅs"
    )
    FF_MPEG_DEL_ETED_CUSTOM_MEDIA = "✅ Media cleared succesfully."
    CUSTOM_CAPTION_UL_FILE = ""
    NO_VOID_FORMAT_FOUND = "ERROR... <code>{}</code>"
    FREE_USER_LIMIT_Q_SZE = "Cannot Process, Time OUT..."
    SLOW_URL_DECED = """
Gosh that seems to be a very slow URL. Since you were screwing my home,
I am in no mood to download this file. Meanwhile, why don't you try this: ==> https://shrtz.me/PtsVnf6
and get me a fast URL so that I can upload to Telegram, without me slowing down for other users.
"""
