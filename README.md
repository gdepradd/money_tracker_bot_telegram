# 💰 Bot Telegram Money Tracker

Bot Telegram cerdas untuk mencatat keuangan (pemasukan & pengeluaran) secara otomatis menggunakan Artificial Intelligence. Bot ini mampu memproses input berupa **teks bahasa alami** maupun **foto struk belanja** secara real-time.

## 🚀 Fitur Utama

* **📝 Pencatatan via Teks Natural:** Cukup ketik seperti chat biasa (contoh: *"Beli nasi goreng 15k, es teh 5rb"*), AI akan mengekstrak nama barang, harga, dan kategori.
* **📸 Scan Struk (AI Vision):** Kirim foto struk belanja, bot akan membaca item dan total harga secara otomatis menggunakan Llama 3.2 Vision.
* **🧠 Auto-Categorization:** Membedakan otomatis antara **Pengeluaran** (Expense) dan **Pemasukan** (Income/Gaji).
* **🗑️ Hapus Data Interaktif:** Salah input? Bot menyediakan fitur *list & delete* untuk menghapus transaksi harian tertentu tanpa perlu akses database manual.
* **📊 Laporan Keuangan:**
    * Harian (*Spend today*) - Dilengkapi jam transaksi.
    * Mingguan (*Spend thisweek*).
    * Bulanan (*Spend thismonth*) - Dilengkapi tanggal transaksi.
* **📈 Kalkulasi Otomatis:** Menghitung total per sesi input dan total per periode laporan.
* **💾 Database Lokal:** Penyimpanan data ringan, cepat, dan aman menggunakan SQLite.
  
## 🛠️ Tech Stack

Project ini dibangun menggunakan teknologi berikut:

### Core
* **Python 3.10+**: Bahasa pemrograman utama.
* **Flask**: Web framework untuk menangani Webhook Telegram.
* **SQLAlchemy**: ORM untuk interaksi dengan database SQLite.

### Model LLM (via Groq Cloud)
* **llama-3.3-70b-versatile**: LLM untuk pemrosesan teks (NLP) dan ekstraksi entitas (JSON).
* **meta-llama/llama-4-scout-17b-16e-instruct**: Model Multimodal untuk membaca gambar/struk.

### Infrastructure & Tools
* **Telegram Bot API**: Antarmuka chat pengguna.
* **SQLite**: Database relasional (file-based).
* **PythonAnywhere**: Platform deployment/hosting (Serverless/WSGI).
* **Requests**: Untuk HTTP request ke API Telegram dan Groq.

## 📂 Struktur Project

```text
bot_tracker/
├── app.py           # Main logic, Webhook handler, Report & Delete logic
├── ai_service.py    # Logic komunikasi ke Groq API (Text & Vision)
├── utils.py         # Helper function (Waktu WIB & Format Rupiah)
├── keuangan_baru.db # File database SQLite (Auto-generated)
├── requirements.txt # Daftar library python
├── reset_bot.py     # Script utility untuk reset webhook
├── .env             # Menyimpan API KEY (Rahasia)
└── README.md        # Dokumentasi
