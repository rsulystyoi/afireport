import streamlit as st
import pandas as pd
from datetime import datetime

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="PT. AFI - Report", layout="centered")

# --- FUNGSI KHUSUS RESET TOTAL DATA OVERTIME ---
def reset_data_ot():
    st.session_state.data_rows_ot = [
        {"nama": "", "mulai": "", "selesai": "", "makan": "Ya", "jemputan": "Ya"}
    ]
    for key in list(st.session_state.keys()):
        if key.startswith("ot_nama_") or key.startswith("ot_mulai_") or key.startswith("ot_selesai_"):
            del st.session_state[key]

# --- INISIALISASI SESSION STATE ---
if 'page' not in st.session_state:
    st.session_state.page = 'login'
if 'user_info' not in st.session_state:
    st.session_state.user_info = {}
if 'menu_params' not in st.session_state:
    st.session_state.menu_params = {}

if 'data_rows_ot' not in st.session_state:
    st.session_state.data_rows_ot = [
        {"nama": "", "mulai": "", "selesai": "", "makan": "Ya", "jemputan": "Ya"}
    ]

# State Khusus Tahap Daily Report
if 'dr_step' not in st.session_state:
    st.session_state.dr_step = 1
if 'dr_category' not in st.session_state:
    st.session_state.dr_category = ""
if 'dr_work_type' not in st.session_state:
    st.session_state.dr_work_type = "Regular"

# =====================================================================
# 1. HALAMAN LOGIN
# =====================================================================
if st.session_state.page == 'login':
    st.markdown("<h2 style='text-align: center;'>AFi - Report</h2>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center;'>PT. Automotive Fasteners Aoyama Indonesia</h4>", unsafe_allow_html=True)
    st.write("---")
    
    nama_user = st.text_input("Nama :")
    nik_user = st.text_input("NIK :", type="default")
    
    st.write("")
    if st.button("SUBMIT", use_container_width=True):
        if nama_user and nik_user:
            st.session_state.user_info = {"nama": nama_user, "nik": nik_user}
            st.session_state.page = 'select_menu'
            st.rerun()
        else:
            st.error("Silakan isi Nama User dan NIK User terlebih dahulu!")

# =====================================================================
# 2. HALAMAN SELECT MENU
# =====================================================================
elif st.session_state.page == 'select_menu':
    st.title("📋 Select Page")
    st.write(f"Logged in as: **{st.session_state.user_info.get('nama', '')}** ({st.session_state.user_info.get('nik', '')})")
    st.write("---")
    
    tahun = st.selectbox("Tahun :", [str(x) for x in range(2026, 2029)])
    bulan = st.selectbox("Bulan :", ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"])
    forecast = st.text_input("Forecast :")
    target_ot = st.number_input("Target OT (Jam) :", min_value=0, step=1)
    tanggal_input = st.date_input("Tanggal Input :", datetime.now())
    
    st.write("---")
    st.subheader("Pilih Laporan:")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Absensi", use_container_width=True):
            st.session_state.menu_params = {
                "tahun": tahun, "bulan": bulan, "forecast": forecast, "target_ot": target_ot, "tanggal": tanggal_input
            }
            st.session_state.page = 'input_absensi'
            st.rerun()
            
    with col2:
        if st.button("Over Time", use_container_width=True):
            st.session_state.menu_params = {
                "tahun": tahun, "bulan": bulan, "forecast": forecast, "target_ot": target_ot, "tanggal": tanggal_input
            }
            reset_data_ot()
            st.session_state.page = 'input_overtime'
            st.rerun()
            
    with col3:
        if st.button("Daily Report", use_container_width=True):
            st.session_state.menu_params = {
                "tahun": tahun, "bulan": bulan, "forecast": forecast, "target_ot": target_ot, "tanggal": tanggal_input
            }
            st.session_state.dr_step = 1  # Reset ke Tahap 1
            st.session_state.page = 'input_daily_report'
            st.rerun()

# =====================================================================
# 3. HALAMAN INPUT ABSENSI
# =====================================================================
elif st.session_state.page == 'input_absensi':
    st.title("📝 Attendance Page")
    p = st.session_state.menu_params
    st.caption(f"Parameter: {p.get('tanggal')} | Bulan: {p.get('bulan')} {p.get('tahun')} | Forecast: {p.get('forecast')} | Target OT: {p.get('target_ot')} Jam")
    st.write("---")
    
    col_a, col_b = st.columns(2)
    with col_a:
        shift = st.selectbox("Shift :", ["Shift 1", "Shift 2", "Non-Shift"])
        leader = st.text_input("Leader :")
    with col_b:
        total_member = st.number_input("Total Member :", min_value=0, step=1)
    
    st.write("---")
    st.subheader("Detail Ketidakhadiran / Kondisi:")

    kategori_absensi = ["Sakit", "Cuti Terencana", "Cuti Dadakan", "Cuti Khusus", "Izin", "Terlambat", "OSD"]
    
    if 'jumlah_input_absensi' not in st.session_state:
        st.session_state.jumlah_input_absensi = {kat: 1 for kat in kategori_absensi}
        
    data_nama_terinput = {}

    for kat in kategori_absensi:
        st.markdown(f"**{kat}**")
        list_nama_kat = []
        
        for i in range(st.session_state.jumlah_input_absensi[kat]):
            col_input, col_tombol = st.columns([5, 1])
            with col_input:
                nama = st.text_input(label=f"Nama {kat} {i}", value="", key=f"input_{kat}_{i}", label_visibility="collapsed")
                list_nama_kat.append(nama)
            with col_tombol:
                if i == st.session_state.jumlah_input_absensi[kat] - 1:
                    if st.button("➕", key=f"btn_{kat}_{i}"):
                        st.session_state.jumlah_input_absensi[kat] += 1
                        st.rerun()
                        
        data_nama_terinput[kat] = list_nama_kat
        st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)

    st.write("---")
    col_submit1, col_submit2 = st.columns(2)
    with col_submit1:
        if st.button("SUBMIT DATA ABSENSI", use_container_width=True, type="primary"):
            st.success("Data Absensi Berhasil Disimpan!")
            st.session_state.jumlah_input_absensi = {kat: 1 for kat in kategori_absensi}
            st.session_state.page = 'select_menu'
            st.rerun()
    with col_submit2:
        if st.button("Kembali ke Menu Utama", use_container_width=True, key="back_abs"):
            st.session_state.page = 'select_menu'
            st.rerun()

# =====================================================================
# 4. HALAMAN INPUT OVERTIME (SOLUSI MUTLAK LIVE TEXT DISPLAY)
# =====================================================================
elif st.session_state.page == 'input_overtime':    
    st.title("📝 Overtime Page")
    p = st.session_state.menu_params
    st.caption(f"Parameter: {p.get('tanggal')} | Bulan: {p.get('bulan')} {p.get('tahun')} | Forecast: {p.get('forecast')} | Target OT: {p.get('target_ot')} Jam")
    st.write("---")
    
    # Header Dokumen
    col_h1, col_h2 = st.columns(2)
    with col_h1:
        hari_tanggal = st.date_input("Hari / Tanggal :", key="ot_date")
        dept_section = st.text_input("Dept / Section :", key="ot_dept")
    with col_h2:
        st.write("**Shift :**")
        shift_normal = st.checkbox("Normal / Shift 1", key="ot_s1")
        shift_2 = st.checkbox("Shift 2", key="ot_s2")
        shift_libur = st.checkbox("Lembur Sabtu/Minggu/Libur", key="ot_sl")

    st.write("---")
    st.subheader("Daftar Karyawan Lembur")
    
    # Judul Label Kolom
    col_l1, col_l2, col_l3, col_l4, col_l5, col_l6, col_l7 = st.columns([2.5, 1.5, 1.5, 1.2, 1.2, 1.2, 0.8])
    col_l1.markdown("**Nama**")
    col_l2.markdown("**Mulai (HH:MM)**")
    col_l3.markdown("**Selesai (HH:MM)**")
    col_l4.markdown("**Jam OT**")
    col_l5.markdown("**Makan**")
    col_l6.markdown("**Jemput**")
    col_l7.markdown("**[+]**")

    # --- PERHITUNGAN DATA SECARA LIVE MURNI ---
    list_jam_terhitung = []
    total_jam_ot_kalkulasi = 0.0

    for j, row in enumerate(st.session_state.data_rows_ot):
        m_str = st.session_state.get(f"ot_mulai_{j}", row["mulai"]).strip()
        s_str = st.session_state.get(f"ot_selesai_{j}", row["selesai"]).strip()
        
        jam_ot_per_baris = 0.0
        if m_str != "" and s_str != "":
            try:
                t_mulai = datetime.strptime(m_str, "%H:%M")
                t_selesai = datetime.strptime(s_str, "%H:%M")
                
                selisih = t_selesai - t_mulai
                selisih_detik = selisih.total_seconds()
                
                if selisih_detik < 0:
                    selisih_detik += 24 * 3600  # Lintas tengah malam
                    
                jam_ot_per_baris = selisih_detik / 3600
            except ValueError:
                jam_ot_per_baris = 0.0
                
        list_jam_terhitung.append(jam_ot_per_baris)
        total_jam_ot_kalkulasi += jam_ot_per_baris

    # --- PENGGAMBARAN WIDGET INPUT KE LAYAR WEB ---
    for i, row in enumerate(st.session_state.data_rows_ot):
        c1, c2, c3, c4, c5, c6, c7 = st.columns([2.5, 1.5, 1.5, 1.2, 1.2, 1.2, 0.8])
        
        with c1:
            st.session_state.data_rows_ot[i]["nama"] = st.text_input("Nama", value=row["nama"], key=f"ot_nama_{i}", label_visibility="collapsed", placeholder="Nama")
        with c2:
            st.session_state.data_rows_ot[i]["mulai"] = st.text_input("Mulai", value=row["mulai"], key=f"ot_mulai_{i}", label_visibility="collapsed", placeholder="00:00")
        with c3:
            st.session_state.data_rows_ot[i]["selesai"] = st.text_input("Selesai", value=row["selesai"], key=f"ot_selesai_{i}", label_visibility="collapsed", placeholder="00:00")
        with c4:
            st.markdown(f"<div style='background-color:#f0f2f6; padding:6px; border-radius:4px; text-align:center; font-weight:bold; border:1px solid #dcdcdc; color:#333; margin-top:2px;'>{list_jam_terhitung[i]:.2f}</div>", unsafe_allow_html=True)
        with c5:
            opts_makan = ["Ya", "Tidak"]
            idx_m = opts_makan.index(row["makan"]) if row["makan"] in opts_makan else 0
            st.session_state.data_rows_ot[i]["makan"] = st.selectbox("Makan", options=opts_makan, index=idx_m, key=f"ot_makan_{i}", label_visibility="collapsed")
        with c6:
            opts_jemput = ["Ya", "Tidak"]
            idx_j = opts_jemput.index(row["jemputan"]) if row["jemputan"] in opts_jemput else 0
            st.session_state.data_rows_ot[i]["jemputan"] = st.selectbox("Jemputan", options=opts_jemput, index=idx_j, key=f"ot_jemput_{i}", label_visibility="collapsed")
        with c7:
            if i == len(st.session_state.data_rows_ot) - 1:
                if st.button("➕", key=f"btn_ot_plus_{i}"):
                    for k in range(len(st.session_state.data_rows_ot)):
                        st.session_state.data_rows_ot[k]["nama"] = st.session_state.get(f"ot_nama_{k}", "")
                        st.session_state.data_rows_ot[k]["mulai"] = st.session_state.get(f"ot_mulai_{k}", "")
                        st.session_state.data_rows_ot[k]["selesai"] = st.session_state.get(f"ot_selesai_{k}", "")
                    
                    st.session_state.data_rows_ot.append({
                        "nama": "", "mulai": "", "selesai": "", "makan": "Ya", "jemputan": "Ya"
                    })
                    st.rerun()

    st.write("---")
    st.markdown(f"### 📊 Total Keseluruhan Jam OT : `{total_jam_ot_kalkulasi:.2f}` Jam")
    st.write("---")
    
    # Footer Dokumen
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        st.write("**Yang Memerintah:**")
        st.text_input("Dibuat Oleh (Leader/Spv):", key="f_leader")
        st.text_input("Disetujui Oleh (Manager):", key="f_mgr1")
        st.text_input("Diketahui Oleh (HR & GA):", key="f_hr1")
    st.write("---")
    col_submit1, col_submit2 = st.columns(2)
    with col_submit1:
        if st.button("SUBMIT DATA OVERTIME", use_container_width=True, type="primary", key="submit_ot_final"):
            st.success("Data Lembur Berhasil Disimpan!")
            reset_data_ot()
            st.session_state.page = 'select_menu'
            st.rerun()
    with col_submit2:
        if st.button("Kembali ke Menu Utama", use_container_width=True, key="back_ot_final"):
            reset_data_ot()
            st.session_state.page = 'select_menu'
            st.rerun()

# =====================================================================
# 5. HALAMAN INPUT DAILY REPORT (SESUAI INPUT MANUAL KHUSUS)
# =====================================================================
elif st.session_state.page == 'input_daily_report':
    st.title("📝 Daily Report Page")
    p = st.session_state.menu_params
    st.caption(f"Parameter: {p.get('tanggal')} | Bulan: {p.get('bulan')} {p.get('tahun')} | Forecast: {p.get('forecast')} | Target OT: {p.get('target_ot')} Jam")
    st.write("---")

    # -----------------------------------------------------------------
    # TAHAP 1: PILIH KATEGORI & TIPE PEKERJAAN
    # -----------------------------------------------------------------
    if st.session_state.dr_step == 1:
        st.subheader("Pilih Kategori Pekerjaan & Tipe Kerja")

        list_kategori = [
            "Final Inspeksi Lokal",
            "Final Inspeksi Export",
            "Subcont",
            "Assy/Packing",
            "Sortir/Pilah",
            "Sortir/Pilah Eksternal",
            "Retagging",
            "PDI/Pre-Delivery",
            "5S/Internal",
            "Trial",
            "Training",
            "Others"
        ]

        kat_terpilih = st.radio("Kategori Pekerjaan :", list_kategori, key="dr_kat_radio")

        kategori_final = kat_terpilih
        if kat_terpilih == "Others":
            kategori_final = st.text_input("Sebutkan Kategori Pekerjaan Lainnya :", key="dr_kat_others")

        st.write("---")
        tipe_kerja = st.radio("Tipe Kerja :", ["Regular", "Overtime"], horizontal=True, key="dr_tipe_radio")

        st.write("---")
        col_next1, col_next2 = st.columns(2)
        with col_next1:
            if st.button("NEXT", use_container_width=True, type="primary", key="btn_dr_next"):
                if kat_terpilih == "Others" and not kategori_final.strip():
                    st.error("Silakan tulis nama kategori pekerjaan terlebih dahulu!")
                else:
                    st.session_state.dr_category = kategori_final
                    st.session_state.dr_work_type = tipe_kerja
                    st.session_state.dr_step = 2
                    st.rerun()
        with col_next2:
            if st.button("Kembali ke Menu Utama", use_container_width=True, key="btn_dr_back_menu1"):
                st.session_state.page = 'select_menu'
                st.rerun()

    # -----------------------------------------------------------------
    # TAHAP 2: FORM DETAIL LAPORAN (FORM MANUAL RINGKAS)
    # -----------------------------------------------------------------
    elif st.session_state.dr_step == 2:
        st.info(f"📌 **Kategori:** {st.session_state.dr_category} | **Tipe Kerja:** {st.session_state.dr_work_type}")
        st.write("---")

        # 1. Nama
        nama_dr = st.text_input("Nama :", key="dr_nama")

        # 2. NIK
        nik_dr = st.text_input("NIK :", key="dr_nik")

        # 3. No Meja
        no_meja = st.text_input("No. Meja :", key="dr_no_meja")

        # 4. Start Kerja & 5. Finish Kerja
        col_w1, col_w2 = st.columns(2)
        with col_w1:
            start_kerja = st.text_input("Start Kerja (HH:MM) :", placeholder="00:00", key="dr_start")
        with col_w2:
            finish_kerja = st.text_input("Finish Kerja (HH:MM) :", placeholder="00:00", key="dr_finish")

        # 6. Total Waktu Kerja (Kalkulasi Otomatis Live)
        total_waktu = 0.0
        s_str = start_kerja.strip()
        f_str = finish_kerja.strip()
        if s_str != "" and f_str != "":
            try:
                t_start = datetime.strptime(s_str, "%H:%M")
                t_finish = datetime.strptime(f_str, "%H:%M")
                selisih = (t_finish - t_start).total_seconds()
                if selisih < 0:
                    selisih += 24 * 3600
                total_waktu = selisih / 3600
            except ValueError:
                total_waktu = 0.0

        st.markdown(f"**Total Waktu Kerja :**")
        st.markdown(f"<div style='background-color:#f0f2f6; padding:8px; border-radius:4px; text-align:center; font-weight:bold; border:1px solid #dcdcdc; color:#333; margin-bottom:15px;'>{total_waktu:.2f} Jam</div>", unsafe_allow_html=True)

        # 7. Result (Box/Lot)
        result_box_lot = st.text_input("Result (Box/Lot) :", key="dr_result_box_lot")

        st.write("---")
        col_submit1, col_submit2, col_submit3 = st.columns([2, 1.5, 1.5])
        
        with col_submit1:
            if st.button("SUBMIT DAILY REPORT", use_container_width=True, type="primary", key="submit_dr_final"):
                st.success("Daily Report Berhasil Disimpan!")
                st.session_state.dr_step = 1
                st.session_state.page = 'select_menu'
                st.rerun()
                
        with col_submit2:
            if st.button("Kembali", use_container_width=True, key="back_dr_step1"):
                st.session_state.dr_step = 1
                st.rerun()

        with col_submit3:
            if st.button("Menu Utama", use_container_width=True, key="back_dr_final"):
                st.session_state.dr_step = 1
                st.session_state.page = 'select_menu'
                st.rerun()