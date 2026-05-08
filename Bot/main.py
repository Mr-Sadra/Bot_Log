from telegram import Update, Chat
from telegram.ext import ContextTypes
from telegram.error import BadRequest
from telegram.constants import ParseMode
from dotenv import load_dotenv
from loguru import logger
import logging
import pandas as pd
import json
import os

from Donate import *
from Staff import *
from Test_Code import LOG
load_dotenv()
TOKEN = os.getenv("TOKEN")
BASE_URL = os.getenv("BASE_URL")

SUPPORT_CHAT_ID = 4473333989  
async def support_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id
    if context.args:
        user_message = " ".join(context.args)
        support_text = (
            f"پیام جدید از کاربر:\n"
            f"👤 نام: {user.first_name}\n"
            f"🆔 یوزرنیم: @{user.username}\n"
            f"📌 شناسه کاربر: {user.id}\n\n"
            f"📨 متن پیام:\n{user_message}"
        )

        try:
            await context.bot.send_message(
                chat_id=SUPPORT_CHAT_ID,
                text=support_text
            )

            await update.message.reply_text(
                "پیام شما با موفقیت برای پشتیبانی ارسال شد.\n"
                "لطفاً منتظر پاسخ کارشناسان باشید."
            )

        except Exception as e:
            await update.message.reply_text(
                "خطا در ارسال پیام به پشتیبانی.\n"
                "لطفاً دوباره تلاش کنید."
            )

    else:
        await update.message.reply_text(
            "برای ارسال پیام به پشتیبانی از فرمت زیر استفاده کنید:\n"
            "/support پیام شما"
        )


async def help(update:Update,context : ContextTypes.DEFAULT_TYPE):
    text = (
    "📦 دستورات مخصوص چت خصوصی:\n"
    "/start برای شروع بات! \n "
    "/help برای نمایش دستورات بات! \n "
    "/buy برای خرید بسته! \n "
    "/Support برای تماس با پشیبانی بات! \n "
    "👥 دستورات مخصوص گروه:\n"
    "همه دستوراتی که داخل بات کار میکنه به همراه کد های زیر: \n"
    "/help برای نمایش دستورات بات!فقط برای ادمین ها \n "
    )
    await update.message.reply_text(
        text, parse_mode="Markdown"
        )




async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    chat_type = update.effective_chat.type
    if chat_type in ['group', 'supergroup', 'channel']:
        response_text = f"Channel id is : {chat_id}"
        await update.message.reply_text(
        f"{response_text}"
        )


def main():
    os.system("cls")
    print("Bot STARTED!")
    
    # Starting Bot
    application = Application.builder().token(TOKEN).base_url(BASE_URL).build()
    
    # Commands:Users
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("Support", support_bot))
    application.add_handler(CommandHandler("help", help))

    # Commands:Staff
    # application.add_handler(CommandHandler("help_admin", admin_help))
    application.add_handler(CommandHandler("Perm", myperm))
    application.add_handler(CommandHandler("Command", Command_Helper))
    application.add_handler(CommandHandler("p", LOG))


    # Donate
    application.add_handler(CommandHandler("buy", invoice))
    application.add_handler(PreCheckoutQueryHandler(precheckout_callback))
    application.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_callback))

    # Reloading
    application.run_polling(allowed_updates=Update.ALL_TYPES)

    # https://tapi.bale.ai/bot{bot_Token}/sendmessage?token=&channel_id={channel_id}&text={Your_Text}
    # https://tapi.bale.ai/bot106421354:mqwPQ0_gJNXV3rw0GG701S16bVbBAG9A8WU/sendmessage?token=&channel_id=4473333989&text=message_Text
    
if __name__ == "__main__":
    main()
