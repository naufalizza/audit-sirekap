# Audit Sirekap: _Endpoint_

Cara jalankan:
1. Pasang Python. Program ini telah diuji dengan versi Python 3.11.5.
2. Jalankan perintah `pip install -r requirements.txt`.
3. Buat folder `private` dan simpan data JSON tidak valid dengan nama `raw_invalid.jsonl` pada folder tersebut. Data tersebut dapat dibangkitkan dari `../validation.py`.
4. Jalankan perintah `py make.py private/raw_invalid.jsonl private/invalid`.
5. Jalankan perintah `py main.py private/invalid`.
6. Buka `http://127.0.0.1:8000/docs` untuk menunjukkan _endpoint_ yang tersedia.
