# audit-sirekap

## Cara Pembaruan
1. Pasang Python. Program ini telah diuji dengan versi Python 3.11.5.
2. Jalankan perintah `pip install -r requirements.txt`.
3. Jalankan perintah `py update.py private 512`.

## Cara Validasi
1. Buat folder `private`.
2. Simpan data JSONL yang memuat seluruh informasi TPS (`all_tps_data.jsonl`, tidak publik).
3. Jalankan `py main.py private/all_tps_data.jsonl private/incomplete.jsonl private/invalid.jsonl private/next_url.txt`.
