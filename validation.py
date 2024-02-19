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

if __name__ == "__main__":
    import json
    raw_data = """{"mode": "hhcw", "chart": {"null": null, "100025": 44, "100026": 78, "100027": 18}, "images": ["https://sirekap-obj-formc.kpu.go.id/e768/pemilu/ppwp/17/01/08/20/01/1701082001002-20240216-161218--44560751-2bda-4951-977a-219e12177251.jpg", "https://sirekap-obj-formc.kpu.go.id/e768/pemilu/ppwp/17/01/08/20/01/1701082001002-20240216-163322--68eec787-d5b2-4702-9be2-0ce9ba529532.jpg", "https://sirekap-obj-formc.kpu.go.id/e768/pemilu/ppwp/17/01/08/20/01/1701082001002-20240216-162409--16a9177f-95bc-47d3-bdde-fd40246fa711.jpg"], "administrasi": {"suara_sah": 140, "suara_total": 140, "pemilih_dpt_j": 174, "pemilih_dpt_l": 88, "pemilih_dpt_p": 86, "pengguna_dpt_j": 137, "pengguna_dpt_l": 63, "pengguna_dpt_p": 74, "pengguna_dptb_j": 3, "pengguna_dptb_l": 2, "pengguna_dptb_p": 1, "suara_tidak_sah": 0, "pengguna_total_j": 140, "pengguna_total_l": 65, "pengguna_total_p": 75, "pengguna_non_dpt_j": 0, "pengguna_non_dpt_l": 0, "pengguna_non_dpt_p": 0}, "psu": null, "ts": "2024-02-16 23:00:00", "status_suara": true, "status_adm": true}"""
    data = json.loads(raw_data)
    result = get_validation_result(data)
    print(result)
