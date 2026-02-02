import os
import requests
from flask import Flask, request, jsonify
from database import db, Transaction
from ai_service import analyze_text, analyze_image
from utils import get_wib_now, format_rupiah
from datetime import timedelta
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'financial.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
with app.app_context(): db.create_all()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

def send_telegram(chat_id, text):
    try: requests.post(TELEGRAM_API_URL, json={'chat_id': chat_id, 'text': text, 'parse_mode': 'Markdown'}, timeout=10)
    except: pass

def get_telegram_photo(file_id):
    try:
        r = requests.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getFile?file_id={file_id}", timeout=5)
        path = r.json()['result']['file_path']
        file_url = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{path}"
        return requests.get(file_url, timeout=10).content
    except: return None

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    if not data or 'message' not in data: return jsonify({'status': 'ignored'})

    msg = data['message']
    chat_id = msg['chat']['id']

    # --- [FIX UTAMA] DEFINISIKAN TEXT DI ATAS AGAR TIDAK ERROR ---
    text = msg.get('text', '').lower()

    items = []

    # 1. LOGIKA GAMBAR
    if 'photo' in msg:
        send_telegram(chat_id, "📸 *Sedang membaca struk...*")
        file_id = msg['photo'][-1]['file_id']
        image_bytes = get_telegram_photo(file_id)
        if image_bytes:
            items = analyze_image(image_bytes)

    # 2. LOGIKA TEKS (COMMANDS & TRANSAKSI)
    elif text:
        # Cek Command Info
        if text in ['info', 'help', '/start']:
            send_telegram(chat_id, "🤖 *Bot Ready!* \nKirim teks: _'Nasi 10k'_ \nAtau foto struk!")
            return jsonify({'status': 'ok'})

        # Cek Command Laporan
        if any(k in text for k in ['spend', 'laporan', 'income']):
            handle_report(chat_id, text)
            return jsonify({'status': 'ok'})

        # Kalau bukan command, berarti TRANSAKSI BIASA
        items = analyze_text(text)

    # 3. PROSES SIMPAN (DENGAN TOTAL & DETEKSI GAJI)
    if items:
        save_transactions(chat_id, items)

    return jsonify({'status': 'ok'})

def save_transactions(chat_id, items):
    saved_msg = []
    total_input = 0 # Variabel untuk menghitung total sesi ini

    for item in items:
        name = item.get('item_name') or item.get('item') or 'Barang'
        try: amount = float(item.get('amount', 0))
        except: amount = 0

        # --- LOGIKA DETEKSI INCOME (GAJI) ---
        tipe = item.get('transaction_type', 'Expense')
        # Jika nama barang mengandung kata 'gaji' atau 'income', paksa jadi Income
        if 'gaji' in name.lower() or 'income' in name.lower():
            tipe = 'Income'

        new_tx = Transaction(
            chat_id=chat_id, item_name=name, amount=amount,
            category=item.get('category', 'Umum'), transaction_type=tipe,
            transaction_date=get_wib_now()
        )
        db.session.add(new_tx)

        # Pilih Ikon
        icon = "📈" if tipe == 'Income' else "🛒"
        saved_msg.append(f"{icon} {name} ({format_rupiah(amount)})")

        # Tambahkan ke total
        total_input += amount

    db.session.commit()

    # --- BALASAN DENGAN TOTAL ---
    if saved_msg:
        msg = f"✅ *Tersimpan ({len(saved_msg)} item):*\n"
        msg += "\n".join(saved_msg)
        # Tampilkan Total
        msg += f"\n\n💰 *Total Input: {format_rupiah(total_input)}*"
        send_telegram(chat_id, msg)

def handle_report(chat_id, text):
    now = get_wib_now()
    start_date = None
    period_title = ""
    date_info = ""

    tx_type = 'Income' if 'income' in text else 'Expense'
    label_tipe = "Pemasukan" if tx_type == 'Income' else "Pengeluaran"

    # 1. Tentukan Waktu
    if 'today' in text:
        start_date = now.replace(hour=0, minute=0, second=0)
        period_title = "Hari Ini"
        date_info = now.strftime("%d %b %Y")
    elif 'week' in text:
        start_date = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0)
        period_title = "Minggu Ini"
        date_info = f"Sejak {start_date.strftime('%d %b')}"
    elif 'month' in text:
        start_date = now.replace(day=1, hour=0, minute=0, second=0)
        period_title = "Bulan Ini"
        date_info = now.strftime("%B %Y")

    # 2. Ambil Data
    if start_date:
        txs = Transaction.query.filter(
            Transaction.chat_id==chat_id,
            Transaction.transaction_type==tx_type,
            Transaction.transaction_date>=start_date
        ).order_by(Transaction.transaction_date.desc()).all()

        if not txs:
            send_telegram(chat_id, f"Belum ada data {label_tipe} {period_title}.")
        else:
            total_all = sum(t.amount for t in txs)

            # Header
            msg = f"📊 *Laporan {label_tipe} {period_title}*\n"
            msg += f"🗓️ _{date_info}_\n\n"

            # ISI LAPORAN (LOOP SEMUA DATA)
            # Saya hapus limit [:20] agar semua muncul
            for t in txs:
                if period_title == "Hari Ini":
                    waktu = t.transaction_date.strftime('%H:%M')
                    row = f"• `{waktu}` {t.item_name} ({format_rupiah(t.amount)})\n"
                else:
                    tanggal = t.transaction_date.strftime('%d/%m')
                    row = f"• `{tanggal}` {t.item_name} ({format_rupiah(t.amount)})\n"

                # Cek jika pesan hampir penuh (Batas Telegram ~4096 karakter)
                if len(msg) + len(row) > 4000:
                    msg += "\n...(Dipotong karena pesan terlalu panjang)..."
                    break

                msg += row

            msg += f"\n💰 *Total: {format_rupiah(total_all)}*"
            send_telegram(chat_id, msg)
if __name__ == '__main__':
    app.run(debug=True)