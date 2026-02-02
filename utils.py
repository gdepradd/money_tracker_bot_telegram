from datetime import datetime, timedelta
import pytz

def get_wib_now():
    # Mengambil waktu UTC server lalu tambah 7 jam
    utc_now = datetime.utcnow()
    wib_now = utc_now + timedelta(hours=7)
    return wib_now

def format_rupiah(amount):
    return f"Rp {amount:,.0f}".replace(",", ".")