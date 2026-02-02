import os
import requests
from dotenv import load_dotenv

# 1. Load Environment Variables
load_dotenv()

username = os.getenv("PYTHONANYWHERE_USERNAME")
token = os.getenv("PYTHONANYWHERE_API_TOKEN")
host = "www.pythonanywhere.com"

# Sesuaikan path ini dengan lokasi file di server PythonAnywhere Anda
remote_file_path = f"/home/{username}/bot_tracker/financial.db"
local_file_name = "financial_local.db"

print("⏳ Sedang mendownload database...")

# 2. Request ke API
response = requests.get(
    f"https://{host}/api/v0/user/{username}/files/path{remote_file_path}",
    headers={"Authorization": f"Token {token}"}
)

# 3. Cek Status & Simpan
if response.status_code == 200:
    with open(local_file_name, "wb") as f:
        f.write(response.content)
    print(f"✅ SUKSES! Database tersimpan sebagai: {local_file_name}")
    print("👉 Silakan buka file tersebut menggunakan Extension 'SQLite Viewer' di VS Code.")
else:
    print("❌ GAGAL DOWNLOAD!")
    print(f"Status Code: {response.status_code}")
    print(f"Pesan Error: {response.text}")