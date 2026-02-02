import os
import json
import base64
from groq import Groq
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# --- FUNGSI 1: TEKS (TANPA RESPONSE_FORMAT) ---
def analyze_text(text):
    # 1. Debugging: Cek apa yang sebenarnya dikirim
    print(f"DEBUG AI INPUT: {text}")

    if not text or len(text.strip()) < 2:
        return []

    # 2. Prompt yang sangat eksplisit (Memohon JSON)
    system_prompt = """
    Kamu asisten pencatat keuangan.
    Tugas: Ubah input user menjadi format JSON Array.

    CONTOH INPUT: "Beli nasi 10rb"
    CONTOH OUTPUT: [{"item_name": "nasi", "amount": 10000, "category": "Makanan", "transaction_type": "Expense"}]

    ATURAN KERAS:
    - JANGAN ada kata pengantar. Langsung kurung siku `[...]`.
    - HANYA Output JSON valid.
    """

    try:
        # HAPUS response_format={"type": "json_object"} (Ini biang kerok error 400)
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            temperature=0
        )
        content = completion.choices[0].message.content
        print(f"DEBUG AI OUTPUT: {content}") # Cek di error log nanti
        return parse_json(content)

    except Exception as e:
        print(f"❌ ERROR AI: {e}")
        return []

# --- FUNGSI 2: GAMBAR (SAMA, TANPA FORMAT KETAT) ---
def analyze_image(image_bytes):
    try:
        base64_image = base64.b64encode(image_bytes).decode('utf-8')

        completion = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Ambil data belanja dari struk ini. Biasanya input harga disingkat k atau rb. padahal normalnya ribuan harganya. Output HANYA JSON Array: [{'item_name': '...', 'amount': 0, 'category': '...', 'transaction_type': 'Expense'}]"},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            temperature=0,
            max_tokens=1024
        )
        content = completion.choices[0].message.content
        print(f"DEBUG VISION OUTPUT: {content}")
        return parse_json(content)

    except Exception as e:
        print(f"❌ ERROR VISION: {e}")
        return []

# --- PARSER JSON MANUAL (LEBIH KUAT) ---
def parse_json(content):
    try:
        # Cari kurung siku pembuka '[' pertama dan penutup ']' terakhir
        start = content.find('[')
        end = content.rfind(']') + 1

        if start != -1 and end != -1:
            json_str = content[start:end]
            return json.loads(json_str)

        # Kalau formatnya dictionary (kurung kurawal)
        start_dict = content.find('{')
        end_dict = content.rfind('}') + 1
        if start_dict != -1 and end_dict != -1:
            data = json.loads(content[start_dict:end_dict])
            # Bungkus jadi list
            if isinstance(data, dict):
                # Cek jika ada key 'transactions'
                for k in ['transactions', 'items']:
                    if k in data: return data[k]
                return [data]

        return []
    except Exception as e:
        print(f"⚠️ Gagal Parse JSON Manual: {e}")
        return []