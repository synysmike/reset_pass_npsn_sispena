import asyncio
import json
import os
import re
import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

load_dotenv()

session = requests.Session()
# Supaya server mengembalikan JSON, bukan HTML (banyak aplikasi Sispena memeriksa ini)
session.headers.update({
    "X-Requested-With": "XMLHttpRequest",
    "Accept": "application/json",
    "Referer": "https://apps.ban-pdm.id/sispena3/sekolah",
})

AJAX_LIST_URL = "https://apps.ban-pdm.id/sispena3/sekolah/ajax_list"
AJAX_UPDATE_URL = "https://apps.ban-pdm.id/sispena3/sekolah/ajax_update"

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
SISPENA_USERNAME = os.environ.get("SISPENA_USERNAME")
SISPENA_PASSWORD = os.environ.get("SISPENA_PASSWORD")

CREDIT = (
    "Terimakasih sudah menggunakan Aplikasi reset password dari Ir.Teguh (https://github.com/synysmike), "
    "mohon dukungannya dengan memberikan like pada project ini: https://github.com/synysmike/reset_pass_npsn_sispena"
)


def login_helper(username, password):
    info = {"username": username, "password": password}
    url = "https://apps.ban-pdm.id/sispena3/login/proses"
    login = session.post(url, data=info)
    if login.url == "https://apps.ban-pdm.id/sispena3/dashboard":
        return 200
    return 401


def logout_helper():
    """
    Clear Sispena session after finishing one reset flow.
    If Sispena later requires a specific logout URL, it can be added here.
    """
    session.cookies.clear()


def build_datatable_params(npsn, draw=1, start=0, length=10):
    """Build simplified DataTables server-side params for NPSN search."""
    params = {
        "draw": str(draw),
        "start": start,
        "length": length,
        "search[value]": str(npsn),
        "search[regex]": "false",
    }
    for i in range(10):
        params[f"columns[{i}][data]"] = str(i)
        params[f"columns[{i}][name]"] = ""
        params[f"columns[{i}][searchable]"] = "true"
        params[f"columns[{i}][orderable]"] = "true" if i else "false"
        params[f"columns[{i}][search][value]"] = ""
        params[f"columns[{i}][search][regex]"] = "false"
    return params


def get_sekolah_id_by_npsn(npsn):
    """POST to ajax_list with DataTables search, return sekolah id from first row."""
    params = build_datatable_params(npsn)
    r = session.post(AJAX_LIST_URL, data=params)
    r.raise_for_status()
    text = r.text.strip()
    if not text:
        raise requests.RequestException("Respons server kosong (mungkin sesi habis atau NPSN di luar wilayah akses).")
    try:
        data = r.json()
    except json.JSONDecodeError:
        raise requests.RequestException(
            "Respons server bukan JSON (mungkin sesi habis—coba restart bot, atau NPSN di luar wilayah akses)."
        )
    rows = data.get("data") or []
    if not rows:
        return None
    # Last column contains HTML with edit('117323')
    last_cell = rows[0][-1] if rows[0] else ""
    match = re.search(r"edit\s*\(\s*['\"]?(\d+)['\"]?\s*\)", last_cell)
    return match.group(1) if match else None


def reset_password(sekolah_id, new_password):
    """POST to ajax_update to set new password for sekolah."""
    body = {"sekolah_id": sekolah_id, "password": new_password}
    r = session.post(AJAX_UPDATE_URL, data=body)
    r.raise_for_status()
    return r


def do_reset_by_npsn(npsn, new_password=None):
    """
    Look up sekolah by NPSN, reset password. Returns (success: bool, message: str).
    When new_password is None, uses NPSN as the new password (e.g. from chat).
    """
    npsn = str(npsn).strip()
    if not npsn or not npsn.isdigit():
        return False, "NPSN tidak valid. Kirim angka NPSN saja (contoh: 20411899)."
    password = new_password if new_password is not None else npsn
    try:
        # Login setiap kali sebelum reset password
        if login_helper(SISPENA_USERNAME, SISPENA_PASSWORD) != 200:
            return False, "Login ke Sispena gagal."

        sekolah_id = get_sekolah_id_by_npsn(npsn)
        if not sekolah_id:
            return False, f"NPSN {npsn} tidak ditemukan."
        reset_password(sekolah_id, password)
        return True, f"NPSN {npsn} telah berhasil direset."
    finally:
        # Logout setelah satu proses reset selesai untuk mengosongkan sesi
        logout_helper()
    except requests.RequestException as e:
        return False, f"Gagal reset NPSN {npsn}: {e}"
    except json.JSONDecodeError as e:
        return False, f"Gagal reset NPSN {npsn}: respons server tidak valid. Coba restart bot atau cek NPSN/wilayah akses."


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message and update.message.text or "").strip()
    if not text:
        await update.message.reply_text("Kirim NPSN sekolah (angka saja).\n\n" + CREDIT)
        return
    npsn = text.split()[0] if text else ""
    loop = asyncio.get_event_loop()
    success, msg = await loop.run_in_executor(
        None, do_reset_by_npsn, npsn, None
    )
    await update.message.reply_text(f"{msg}\n\n{CREDIT}")


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Kirim NPSN sekolah untuk mereset password.\nContoh: 20411899\n\n" + CREDIT
    )


def run_bot():
    if not TELEGRAM_BOT_TOKEN:
        raise RuntimeError("Set TELEGRAM_BOT_TOKEN in .env (copy .env.example to .env).")
    if not SISPENA_USERNAME or not SISPENA_PASSWORD:
        raise RuntimeError("Set SISPENA_USERNAME and SISPENA_PASSWORD in .env.")
    if login_helper(SISPENA_USERNAME, SISPENA_PASSWORD) != 200:
        raise RuntimeError("Login Sispena gagal. Cek username/password.")
    print(CREDIT)
    print()
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    run_bot()