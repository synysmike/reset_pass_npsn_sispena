# Reset Password Sispena (Bot Telegram)

Aplikasi bot Telegram untuk mereset password akun sekolah di **Sispena-PDM** (Sistem Penilaian Akreditasi BAN-PDM) berdasarkan NPSN. Bot akan mencari sekolah menurut NPSN yang dikirim pengguna, lalu mengatur ulang password menjadi NPSN tersebut.

## Fitur

- **Reset password via Telegram**: Kirim NPSN sekolah ke bot, password akun sekolah akan direset menjadi NPSN yang dikirim.
- **Integrasi Sispena**: Login ke [Sispena-PDM](https://apps.ban-pdm.id/sispena3), cari sekolah lewat NPSN, dan kirim permintaan ganti password ke API Sispena.

## Cara Pakai

1. Buka bot di Telegram dan kirim perintah `/start` untuk panduan singkat.
2. Kirim **NPSN** sekolah (angka saja), contoh: `20411899`.
3. Bot akan mereset password akun sekolah tersebut menjadi NPSN yang dikirim dan membalas dengan konfirmasi, misalnya: *"NPSN 20411899 telah berhasil direset."*

## Persyaratan

- Python 3.10+
- Akun Sispena (username & password) yang punya akses reset password sekolah.
- Token bot Telegram dari [@BotFather](https://t.me/BotFather).

## Instalasi

1. Clone repositori:
   ```bash
   git clone <url-repo>
   cd sekolah
   ```

2. Buat lingkungan virtual (opsional):
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Linux/macOS
   # atau: .venv\Scripts\activate   # Windows
   ```

3. Pasang dependensi:
   ```bash
   pip install -r requirements.txt
   ```

4. Atur variabel lingkungan:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` dan isi:
   - `TELEGRAM_BOT_TOKEN` — token dari BotFather
   - `SISPENA_USERNAME` — username login Sispena
   - `SISPENA_PASSWORD` — password login Sispena

5. Jalankan bot:
   ```bash
   python reset.py
   ```

## Konfigurasi (.env)

| Variabel             | Keterangan                              |
|----------------------|-----------------------------------------|
| `TELEGRAM_BOT_TOKEN` | Token bot Telegram dari @BotFather     |
| `SISPENA_USERNAME`   | Username untuk login ke Sispena-PDM     |
| `SISPENA_PASSWORD`   | Password untuk login ke Sispena-PDM     |

Jangan commit file `.env` ke repositori; gunakan `.env.example` sebagai contoh.

## Lisensi

Bebas dipakai dan dimodifikasi sesuai kebutuhan.
