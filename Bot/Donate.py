from telegram import LabeledPrice, Update, SuccessfulPayment
from telegram.ext import ContextTypes
from dotenv import load_dotenv
import os
LS_ORDER = []
pending_orders = {}
load_dotenv()

PROVIDER_TOKEN = os.getenv("PROVIDER_TOKEN")

async def precheckout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.pre_checkout_query
    order_id = query.invoice_payload

    if order_id not in pending_orders:
        await query.answer(
            ok = False,
            error_message = "سفارش یافت نشد. لطفا دوباره تلاش کنید."
        )
        return

    if query.from_user.id !=  pending_orders[order_id]["user_id"]:
        await query.answer(
            ok = False,
            error_message = "این سفارش متعلق به شما نیست."
        )
        return

    pending_orders[order_id]["verified"] = True
    await query.answer(ok = True)

async def invoice(update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.message.chat_id
        user_id = update.effective_user.id
        order_id = f"order-{user_id}-{chat_id}-{update.update_id}"
        if not context.args:
            await update.message.reply_text("لطفاً شناسه پرداخت را وارد کنید\n  /invoice ble.ir/join/0ABCDEFGHI ")
        
        elif len(context.args) > 1: 
            await update.message.reply_text(f" خرید برای 1 گروه هستش! شما {len(context.args)} گروه وارد کردین")
        
        else:
            pending_orders[order_id] = {
                "user_id": user_id,
                "chat_id": chat_id,
                "status": "pending",
                "verified": False,
                "Group": context.args[0]
            }
            LS_ORDER.append(LabeledPrice("محصول تستی", 100000))
            try:
                await context.bot.send_invoice(
                    chat_id = chat_id,
                    title = "محصول تستی",
                    description  = "این یک پرداخت تستی است",
                    payload = order_id,  
                    provider_token = PROVIDER_TOKEN,
                    currency = "IRR",
                    prices = LS_ORDER,
                    start_parameter = "test-payment"
                )
            
            except Exception as e:
                await update.message.reply_text(f"خطا: {e}")
                if order_id in pending_orders:
                    del pending_orders[order_id]

async def successful_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    payment: SuccessfulPayment = update.message.successful_payment
    order_id = payment.invoice_payload
    new_m = str(order_id).replace("order","")
    new_m = str(new_m).replace("-","")
    if order_id not in pending_orders:
        await update.message.reply_text(
            "❌ خطا: اطلاعات سفارش یافت نشد. لطفا با پشتیبانی تماس بگیرید."
        )
        return

    order = pending_orders[order_id]
    if update.effective_user.id !=  order["user_id"]:
        await update.message.reply_text(
            "❌ خطا: این پرداخت متعلق به شما نیست."
        )
        return

    if not order["verified"]:
        await update.message.reply_text(
            "❌ خطا: پرداخت تأیید نشده بود."
        )
        return

    if order["status"] ==  "completed":
        await update.message.reply_text(
            "⚠️ این سفارش قبلاً پرداخت شده بود."
        )
        return

    if payment.total_amount <=  0:
        await update.message.reply_text(
            "❌ خطا: مبلغ پرداخت نامعتبر است."
        )
        return

    order["status"] = "completed"
    order["payment_date"] = update.message.date
    order["telegram_payment_charge_id"] = payment.telegram_payment_charge_id
    order["provider_payment_charge_id"] = payment.provider_payment_charge_id

    await update.message.reply_text(
        f"✅ پرداخت با موفقیت انجام شد!\n\n"
        f"📋 شماره سفارش: {order_id}\n"
        f"💰 مبلغ: {payment.total_amount / 100:.0f} تومان\n"
        f"🆔 شناسه پرداخت تلگرام: {payment.telegram_payment_charge_id}\n"
        f"📅 تاریخ: {update.message.date.strftime('%Y/%m/%d %H:%M')}\n\n"
        f" کد فعال سازی : {new_m} "
        f" کد فعال سازی فقط در گروه یا کانال {order["Group"]} قابل استفاده هستش"
    )
    del pending_orders[order_id]

async def verify_payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat.type not in [Chat.GROUP, Chat.SUPERGROUP]:
        await update.message.reply_text("این دستور فقط در گروه‌ها قابل استفاده است.")
        return

    else:
        if not context.args:
            await update.message.reply_text("لطفاً شناسه پرداخت را وارد کنید. مثال: /verify 112233")
            return

        payment_id = context.args[0]
        chat_id = update.effective_chat.id
        payment_data = find_payment_in_db(payment_id)
        if payment_data and payment_data['status'] ==  'paid':
            if payment_data['used_in_group'] is None:
                register_group_active(chat_id, payment_id)
                await update.message.reply_text("✅ پرداخت تأیید شد! اشتراک این گروه فعال گردید.")
            
            else:
                await update.message.reply_text("❌ این شناسه پرداخت قبلاً برای گروه دیگری استفاده شده است.")
        
        else:
            await update.message.reply_text("❌ شناسه پرداخت نامعتبر است یا هنوز پرداخت نشده.")
