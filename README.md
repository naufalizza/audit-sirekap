# audit-sirekap

## Cara Validasi
1. Buat folder `private`.
2. Simpan data JSONL yang memuat seluruh informasi TPS (`all_tps_data.jsonl`, tidak publik).
3. Jalankan `py main.py private/all_tps_data.jsonl private/incomplete.jsonl private/invalid.jsonl private/next_url.txt`.
