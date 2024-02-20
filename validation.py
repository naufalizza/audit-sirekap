import json

REQUIRED_ADMINISTRASI_ATTRIBUTE_PREFIX_WITH_SPECIFIC_GENDER = [
    "pengguna_dpt_",
    "pengguna_dptb_",
    "pengguna_non_dpt_",
    "pengguna_total_",
]

required_administrasi_attributes = [
    "suara_sah",
    "suara_tidak_sah",
    "suara_total"
]

for prefix in REQUIRED_ADMINISTRASI_ATTRIBUTE_PREFIX_WITH_SPECIFIC_GENDER:
    required_administrasi_attributes.append(f"{prefix}j")
    required_administrasi_attributes.append(f"{prefix}l")
    required_administrasi_attributes.append(f"{prefix}p")

required_attributes = {
    "administrasi": required_administrasi_attributes,
    "chart": ["100025", "100026", "100027"]
}

def get_validation_result(data: dict):
    reasons = get_incomplete_reasons(data)
    if len(reasons) > 0:
        return {
            "status": "incomplete",
            "reason": reasons
        }
    
    # Validation
    reasons = get_invalid_reasons(data)
    return {
        "status": "invalid" if len(reasons) > 0 else "valid",
        "reason": reasons
    }

def get_incomplete_reasons(data: dict):
    # Incomplete
    if not isinstance(data, dict):
        return ["Data bukan objek."]
    
    reasons = []
    for first_attribute, second_attribute_list in required_attributes.items():
        if first_attribute not in data:
            reasons.append(f"Kunci \"{first_attribute}\" tidak ditemukan.")
            continue

        first_level_data = data[first_attribute]
        if not isinstance(first_level_data, dict):
            reasons.append(f"Nilai \"{first_attribute}\" bukan objek.")
            continue
        
        for second_attribute in second_attribute_list:
            if second_attribute not in first_level_data:
                reasons.append(f"Kunci \"{first_attribute}.{second_attribute}\" tidak ditemukan.")
                continue
            
            second_level_data = first_level_data[second_attribute]
            if not isinstance(second_level_data, int):
                reasons.append(f"Nilai \"{first_attribute}.{second_attribute}\" adalah {second_level_data} ({type(second_level_data)}), bukan bilangan bulat.")
    
    return reasons

def get_invalid_reasons(data):
    reasons = []
    reasons += get_reasons_from_jumlah_pengguna_hak_pilih_tidak_sama_dengan_jumlah_pengguna_hak_pilih_dpt_dptb_dpk(data)
    reasons += get_reasons_from_jumlah_tidak_sama_dengan_penjumlahan_laki_laki_dan_perempuan(data)
    reasons += get_reasons_from_jumlah_seluruh_suara_sah_dan_tidak_sah_tidak_konsisten(data)
    reasons += get_reasons_from_jumlah_perolehan_suara_tidak_sama_dengan_jumlah_seluruh_suara_sah(data)
    reasons += get_reasons_from_jumlah_seluruh_suara_sah_dan_tidak_sah_lebih_dari_jumlah_pengguna_hak_pilih(data)
    return reasons

def create_reason(statement: str, detail: str):
    return f"{statement} Rincian: {detail}"

def get_reasons_from_jumlah_pengguna_hak_pilih_tidak_sama_dengan_jumlah_pengguna_hak_pilih_dpt_dptb_dpk(data):
    administrasi: dict[str, int] = data["administrasi"]
    assert isinstance(administrasi, dict)

    # Check jumlah pengguna hak pilih
    jumlah_pengguna_hak_pilih_dalam_dpt = administrasi["pengguna_dpt_j"]
    jumlah_pengguna_hak_pilih_dalam_dptb = administrasi["pengguna_dptb_j"]
    jumlah_pengguna_hak_pilih_dalam_dpk = administrasi["pengguna_non_dpt_j"]
    jumlah_pengguna_hak_pilih = administrasi["pengguna_total_j"]

    jumlah_pengguna_hak_pilih_dpt_dptb_dpk = (
        jumlah_pengguna_hak_pilih_dalam_dpt
        + jumlah_pengguna_hak_pilih_dalam_dptb
        + jumlah_pengguna_hak_pilih_dalam_dpk
    )

    if jumlah_pengguna_hak_pilih == jumlah_pengguna_hak_pilih_dpt_dptb_dpk:
        return []
    else:
        return [create_reason(
            "Jumlah pengguna hak pilih tidak sama dengan jumlah pengguna hak pilih DPT, DPTb, dan DPK.",
            f"Jumlah pengguna hak pilih bernilai {jumlah_pengguna_hak_pilih}, sedangkan jumlah pengguna hak pilih DPT ({jumlah_pengguna_hak_pilih_dalam_dpt}), DPTb ({jumlah_pengguna_hak_pilih_dalam_dptb}), dan DPK ({jumlah_pengguna_hak_pilih_dalam_dpk}) bernilai {jumlah_pengguna_hak_pilih_dpt_dptb_dpk}."
        )]

def get_reasons_from_jumlah_tidak_sama_dengan_penjumlahan_laki_laki_dan_perempuan(data):
    administrasi: dict[str, int] = data["administrasi"]
    assert isinstance(administrasi, dict)

    reasons = []
    for prefix in REQUIRED_ADMINISTRASI_ATTRIBUTE_PREFIX_WITH_SPECIFIC_GENDER:
        jumlah_value = administrasi[f"{prefix}j"]
        laki_laki_value = administrasi[f"{prefix}l"]
        perempuan_value = administrasi[f"{prefix}p"]
        laki_laki_plus_perempuan_value = laki_laki_value + perempuan_value

        if jumlah_value != laki_laki_plus_perempuan_value:
            reasons.append(create_reason(
                f"Untuk atribut dengan prefiks administrasi.{prefix}, jumlah tidak sama dengan penjumlahan laki-laki dan perempuan.",
                f"Jumlah bernilai {jumlah_value}, sedangkan penjumlahan laki-laki ({laki_laki_value}) dan perempuan ({perempuan_value}) bernilai {laki_laki_plus_perempuan_value}."
            ))

    return reasons

def get_reasons_from_jumlah_seluruh_suara_sah_dan_tidak_sah_tidak_konsisten(data):
    administrasi: dict[str, int] = data["administrasi"]
    assert isinstance(administrasi, dict)

    jumlah_seluruh_suara_sah = administrasi["suara_sah"]
    jumlah_seluruh_suara_tidak_sah = administrasi["suara_tidak_sah"]
    jumlah_seluruh_suara_sah_dan_tidak_sah = administrasi["suara_total"]
    jumlah_seluruh_suara_dari_penjumlahan = jumlah_seluruh_suara_sah + jumlah_seluruh_suara_tidak_sah

    if jumlah_seluruh_suara_sah_dan_tidak_sah == jumlah_seluruh_suara_dari_penjumlahan:
        return []
    else:
        return [create_reason(
            "Jumlah seluruh suara sah dan tidak sah tidak konsisten.",
            f"Jumlah seluruh suara sah dan tidak sah dari data bernilai {jumlah_seluruh_suara_sah_dan_tidak_sah}, sedangkan penjumlahan seluruh suara sah ({jumlah_seluruh_suara_sah}) dan tidak sah ({jumlah_seluruh_suara_tidak_sah}) adalah {jumlah_seluruh_suara_dari_penjumlahan}."
        )]

def get_reasons_from_jumlah_perolehan_suara_tidak_sama_dengan_jumlah_seluruh_suara_sah(data):
    administrasi: dict[str, int] = data["administrasi"]
    chart: dict[str, int] = data["chart"]
    assert isinstance(chart, dict)
    assert isinstance(administrasi, dict)

    jumlah_seluruh_suara_sah = administrasi["suara_sah"]
    jumlah_suara_dari_chart = 0
    suara_dari_chart = []
    
    for a in required_attributes["chart"]:
        jumlah_suara_dari_chart += chart[a]
        suara_dari_chart.append(chart[a])

    if jumlah_seluruh_suara_sah == jumlah_suara_dari_chart:
        return []
    else:
        return [create_reason(
            "Jumlah perolehan suara tidak sama dengan jumlah seluruh suara sah.",
            f"Penjumlahan perolehan suara 01 ({suara_dari_chart[0]}), 02 ({suara_dari_chart[1]}), dan 03 ({suara_dari_chart[2]}) bernilai {jumlah_suara_dari_chart}, sedangkan jumlah seluruh suara sah bernilai {jumlah_seluruh_suara_sah}."
        )]

def get_reasons_from_jumlah_seluruh_suara_sah_dan_tidak_sah_lebih_dari_jumlah_pengguna_hak_pilih(data):
    administrasi: dict[str, int] = data["administrasi"]
    assert isinstance(administrasi, dict)

    jumlah_seluruh_suara_sah_dan_tidak_sah = administrasi["suara_total"]
    jumlah_pengguna_hak_pilih = administrasi["pengguna_total_j"]

    if jumlah_seluruh_suara_sah_dan_tidak_sah <= jumlah_pengguna_hak_pilih:
        return []
    else:
        return [create_reason(
            "Jumlah seluruh suara sah dan tidak sah lebih dari jumlah pengguna hak pilih.",
            f"Jumlah seluruh suara sah dan tidak sah bernilai {jumlah_seluruh_suara_sah_dan_tidak_sah}, sedangkan jumlah pengguna hak pilih adalah {jumlah_pengguna_hak_pilih}."
        )]
    
def validation_procedure(update_folder_path):
    input_path = f"{update_folder_path}/all_tps_data.jsonl"
    incomplete_path = f"{update_folder_path}/incomplete.jsonl"
    invalid_path = f"{update_folder_path}/invalid.jsonl"
    next_url_path = f"{update_folder_path}/next_url.txt"

    count = 0
    incomplete_count = 0
    invalid_count = 0
    next_url_count = 0
    with (
            open(input_path) as input_fp,
            open(incomplete_path, mode="w+") as incomplete_fp,
            open(invalid_path, mode="w+") as invalid_fp,
            open(next_url_path, mode="w+") as next_url_fp,
    ):
        for line in input_fp:
            if not line.startswith("{\"url\":"):
                raise ValueError(f"Unexpected line: {line}")
        
            count += 1

            json_data = json.loads(line)
            url = json_data["url"]
            data = json_data["data"]
            validation_result = get_validation_result(data)
            status = validation_result["status"]
            if status == "valid":
                continue

            json_data["reason"] = validation_result["reason"]
            dumped_json_data = json.dumps(json_data)
            if status == "incomplete":
                print(dumped_json_data, file=incomplete_fp)
                incomplete_count += 1

                print(url, file=next_url_fp)
                next_url_count += 1

            elif status == "invalid":
                print(dumped_json_data, file=invalid_fp)
                invalid_count += 1

                print(url, file=next_url_fp)
                next_url_count += 1

            else:
                raise ValueError(f"Unexpected status: {status}")

    print(f"validation result: {count=};{incomplete_count=};{invalid_count=};{next_url_count=}")
