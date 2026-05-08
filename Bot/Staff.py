from telegram import *
from telegram.ext import *
from telegram.constants import ParseMode
from telegram.error import BadRequest
from loguru import logger
import json
import os

async def get_perm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    try:
        chat_member = await context.bot.get_chat_member(chat_id=chat_id, user_id=user_id)
        alias = update.effective_user.full_name
        status = chat_member.status
        custom_title = getattr(chat_member, "custom_title", None)
        return {
            "status": status,
            "alias": alias,
            "custom_title": custom_title
        }

    except Exception as e:
        return {
            "status": "Helper",
            "alias": update.effective_user.full_name,
            "custom_title": None
        }

async def myperm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat.type not in [Chat.GROUP, Chat.SUPERGROUP]:
        await update.message.reply_text("این دستور فقط در گروه‌ها قابل استفاده است.")
    else:
        info  = await get_perm(update,context)
        Your_Perm = info["status"]
        NickName = info["custom_title"]
        
        if Your_Perm == 'administrator':
            if NickName == "Admin":
                await update.message.reply_text(
                    f"👤 کاربر: {info['alias']}\n"
                    f"🔖 سطح دسترسی: {info['custom_title']}\n"
                )
            else:
                await update.message.reply_text(
                    f"👤 کاربر: {info['alias']}\n"
                    f"🔖 سطح دسترسی: {info['status']}\n"
                    f"🏷 عنوان سفارشی: {info['custom_title'] }"
                )
            
        elif Your_Perm == 'creator':
            await update.message.reply_text(
                f"👤 کاربر: {info['alias']}\n"
                f"🔖 سطح دسترسی: {info['status']}\n"
            )


        else:
            await update.message.reply_text(
                "شما دسترسی ادمین برای استفاده از این دستور را ندارید."
                f"👤 کاربر: {info['alias']}\n"
                f"🔖 سطح دسترسی: {info['custom_title']}\n"
                )


async def Command_Helper(update:Update,context:ContextTypes.DEFAULT_TYPE):
    if context.args:
        if len(context.args) > 1:
            await update.message.reply_text(f"Enter 1 Command")
        else:
            await update.message.reply_text(f"You Say: {" ".join(context.args)} ")
    else:
        await update.message.reply_text("No Command Received! /p Command,for example /p hael")
