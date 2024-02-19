# Audit Sirekap: _Endpoint_

Cara jalankan:
1. Jalankan perintah `pip install -r requirements.txt`.
2. Buat folder `private` dan simpan data JSON tidak valid dengan nama `raw_invalid.jsonl` pada folder tersebut.
3. Jalankan perintah `py make.py private/raw_invalid.jsonl private/invalid`.
4. Jalankan perintah `py main.py private/invalid`.
5. Buka `http://127.0.0.1:8000/docs` untuk menunjukkan _endpoint_ yang tersedia.
