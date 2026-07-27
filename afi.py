import streamlit as st
import pandas as pd
from datetime import datetime
import io
from sqlalchemy import text

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="PT. AFI - Report", layout="centered")

# --- KONEKSI KE DATABASE POSTGRESQL ---
try:
    conn = st.connection("postgresql", type="sql")
except Exception as e:
    st.error("Gagal terhubung ke database PostgreSQL. Pastikan PostgreSQL berjalan dan file .streamlit/secrets.toml sudah dikonfigurasi dengan benar.")

# --- FUNGSI RESET DATA OVERTIME ---
def reset_data_ot():
    st.session_state.data_rows_ot = [
        {"nama": "", "mulai": "", "selesai": "", "makan": "Ya", "jemputan": "Ya"}
    ]
    for key in list(st.session_state.keys()):
        if key.startswith("ot_nama_") or key.startswith("ot_mulai_") or key.startswith("ot_selesai_"):
            del st.session_state[key]

# --- INISIALISASI SESSION STATE UI ---
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
    st.subheader("Pilih Laporan / Menu:")
    
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
            st.session_state.dr_step = 1
            st.session_state.page = 'input_daily_report'
            st.rerun()

    st.write("")
    if st.button("Summary Report", use_container_width=True, type="secondary"):
        st.session_state.page = 'rekap_data'
        st.rerun()

# =====================================================================
# 3. HALAMAN INPUT ABSENSI (POSTGRESQL - FIXED)
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
            # INSERT DATA KE POSTGRESQL MENGGUNAKAN ENGINE CONNECT
            with conn.engine.begin() as connection:
                for kat, list_nama in data_nama_terinput.items():
                    for nm in list_nama:
                        if nm.strip() != "":
                            query = text("""
                                INSERT INTO db_absensi (user_input, nik_user, tahun, bulan, tanggal, shift, leader, total_member, kategori, nama_karyawan)
                                VALUES (:user_input, :nik_user, :tahun, :bulan, :tanggal, :shift, :leader, :total_member, :kategori, :nama_karyawan)
                            """)
                            connection.execute(query, {
                                "user_input": st.session_state.user_info.get("nama", ""),
                                "nik_user": st.session_state.user_info.get("nik", ""),
                                "tahun": p.get("tahun"),
                                "bulan": p.get("bulan"),
                                "tanggal": str(p.get("tanggal")),
                                "shift": shift,
                                "leader": leader,
                                "total_member": total_member,
                                "kategori": kat,
                                "nama_karyawan": nm
                            })

            st.success("Data Absensi Berhasil Disimpan ke PostgreSQL!")
            st.session_state.jumlah_input_absensi = {kat: 1 for kat in kategori_absensi}
            st.session_state.page = 'select_menu'
            st.rerun()

    with col_submit2:
        if st.button("Kembali ke Menu Utama", use_container_width=True, key="back_abs"):
            st.session_state.page = 'select_menu'
            st.rerun()

# =====================================================================
# 4. HALAMAN INPUT OVERTIME (POSTGRESQL - FIXED)
# =====================================================================
elif st.session_state.page == 'input_overtime':    
    st.title("📝 Overtime Page")
    p = st.session_state.menu_params
    st.caption(f"Parameter: {p.get('tanggal')} | Bulan: {p.get('bulan')} {p.get('tahun')} | Forecast: {p.get('forecast')} | Target OT: {p.get('target_ot')} Jam")
    st.write("---")
    
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
    
    col_l1, col_l2, col_l3, col_l4, col_l5, col_l6, col_l7 = st.columns([2.5, 1.5, 1.5, 1.2, 1.2, 1.2, 0.8])
    col_l1.markdown("**Nama**")
    col_l2.markdown("**Mulai (HH:MM)**")
    col_l3.markdown("**Selesai (HH:MM)**")
    col_l4.markdown("**Jam OT**")
    col_l5.markdown("**Makan**")
    col_l6.markdown("**Jemput**")
    col_l7.markdown("**[+]**")

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
                    selisih_detik += 24 * 3600
                    
                jam_ot_per_baris = selisih_detik / 3600
            except ValueError:
                jam_ot_per_baris = 0.0
                
        list_jam_terhitung.append(jam_ot_per_baris)
        total_jam_ot_kalkulasi += jam_ot_per_baris

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
    
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        st.write("**Yang Memerintah:**")
        f_leader = st.text_input("Dibuat Oleh (Leader/Spv):", key="f_leader")
        f_mgr1 = st.text_input("Disetujui Oleh (Manager):", key="f_mgr1")
        f_hr1 = st.text_input("Diketahui Oleh (HR & GA):", key="f_hr1")
    st.write("---")
    col_submit1, col_submit2 = st.columns(2)
    with col_submit1:
        if st.button("SUBMIT DATA OVERTIME", use_container_width=True, type="primary", key="submit_ot_final"):
            shift_info = []
            if shift_normal: shift_info.append("Normal/Shift 1")
            if shift_2: shift_info.append("Shift 2")
            if shift_libur: shift_info.append("Lembur Libur")
            shift_str = ", ".join(shift_info) if shift_info else "-"

            # INSERT DATA OVERTIME KE POSTGRESQL
            with conn.engine.begin() as connection:
                for k, row_ot in enumerate(st.session_state.data_rows_ot):
                    nm_ot = st.session_state.get(f"ot_nama_{k}", row_ot["nama"]).strip()
                    if nm_ot != "":
                        query = text("""
                            INSERT INTO db_overtime (user_input, hari_tanggal, dept_section, shift, nama_karyawan, jam_mulai, jam_selesai, jam_ot, makan, jemputan, leader, manager, hr_ga)
                            VALUES (:user_input, :hari_tanggal, :dept_section, :shift, :nama_karyawan, :jam_mulai, :jam_selesai, :jam_ot, :makan, :jemputan, :leader, :manager, :hr_ga)
                        """)
                        connection.execute(query, {
                            "user_input": st.session_state.user_info.get("nama", ""),
                            "hari_tanggal": str(hari_tanggal),
                            "dept_section": dept_section,
                            "shift": shift_str,
                            "nama_karyawan": nm_ot,
                            "jam_mulai": st.session_state.get(f"ot_mulai_{k}", row_ot["mulai"]),
                            "jam_selesai": st.session_state.get(f"ot_selesai_{k}", row_ot["selesai"]),
                            "jam_ot": list_jam_terhitung[k],
                            "makan": st.session_state.get(f"ot_makan_{k}", row_ot["makan"]),
                            "jemputan": st.session_state.get(f"ot_jemput_{k}", row_ot["jemputan"]),
                            "leader": f_leader,
                            "manager": f_mgr1,
                            "hr_ga": f_hr1
                        })

            st.success("Data Lembur Berhasil Disimpan ke PostgreSQL!")
            reset_data_ot()
            st.session_state.page = 'select_menu'
            st.rerun()

    with col_submit2:
        if st.button("Kembali ke Menu Utama", use_container_width=True, key="back_ot_final"):
            reset_data_ot()
            st.session_state.page = 'select_menu'
            st.rerun()

# =====================================================================
# 5. HALAMAN INPUT DAILY REPORT (POSTGRESQL - FIXED)
# =====================================================================
elif st.session_state.page == 'input_daily_report':
    st.title("📝 Daily Report Page")
    p = st.session_state.menu_params
    st.caption(f"Parameter: {p.get('tanggal')} | Bulan: {p.get('bulan')} {p.get('tahun')} | Forecast: {p.get('forecast')} | Target OT: {p.get('target_ot')} Jam")
    st.write("---")

    if st.session_state.dr_step == 1:
        st.subheader("Pilih Kategori Pekerjaan & Tipe Kerja")

        list_kategori = [
            "Final Inspeksi Lokal", "Final Inspeksi Export", "Subcont", "Assy/Packing",
            "Sortir/Pilah", "Sortir/Pilah Eksternal", "Retagging", "PDI/Pre-Delivery",
            "5S/Internal", "Trial", "Training", "Others"
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

    elif st.session_state.dr_step == 2:
        st.info(f"📌 **Kategori:** {st.session_state.dr_category} | **Tipe Kerja:** {st.session_state.dr_work_type}")
        st.write("---")

        nama_dr = st.text_input("Nama :", key="dr_nama")
        nik_dr = st.text_input("NIK :", key="dr_nik")
        no_meja = st.text_input("No. Meja :", key="dr_no_meja")

        col_w1, col_w2 = st.columns(2)
        with col_w1:
            start_kerja = st.text_input("Start Kerja (HH:MM) :", placeholder="00:00", key="dr_start")
        with col_w2:
            finish_kerja = st.text_input("Finish Kerja (HH:MM) :", placeholder="00:00", key="dr_finish")

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

        result_box_lot = st.text_input("Result (Box/Lot) :", key="dr_result_box_lot")

        st.write("---")
        col_submit1, col_submit2, col_submit3 = st.columns([2, 1.5, 1.5])
        
        with col_submit1:
            if st.button("SUBMIT DAILY REPORT", use_container_width=True, type="primary", key="submit_dr_final"):
                # INSERT DAILY REPORT KE POSTGRESQL
                with conn.engine.begin() as connection:
                    query = text("""
                        INSERT INTO db_daily_report (user_input, tahun, bulan, tanggal, kategori_pekerjaan, tipe_kerja, nama, nik, no_meja, start_kerja, finish_kerja, total_waktu, result_box_lot)
                        VALUES (:user_input, :tahun, :bulan, :tanggal, :kategori_pekerjaan, :tipe_kerja, :nama, :nik, :no_meja, :start_kerja, :finish_kerja, :total_waktu, :result_box_lot)
                    """)
                    connection.execute(query, {
                        "user_input": st.session_state.user_info.get("nama", ""),
                        "tahun": p.get("tahun"),
                        "bulan": p.get("bulan"),
                        "tanggal": str(p.get("tanggal")),
                        "kategori_pekerjaan": st.session_state.dr_category,
                        "tipe_kerja": st.session_state.dr_work_type,
                        "nama": nama_dr,
                        "nik": nik_dr,
                        "no_meja": no_meja,
                        "start_kerja": start_kerja,
                        "finish_kerja": finish_kerja,
                        "total_waktu": total_waktu,
                        "result_box_lot": result_box_lot
                    })

                st.success("Daily Report Berhasil Disimpan ke PostgreSQL!")
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

# =====================================================================
# 6. HALAMAN REKAP DATA POSTGRESQL & EXCEL
# =====================================================================
elif st.session_state.page == 'rekap_data':
    st.title("Smmary Report")
    st.caption("")
    st.write("---")

    tab1, tab2, tab3 = st.tabs(["📋 Data Absensi", "⏰ Data Overtime", "📝 Data Daily Report"])

    # TAB 1: ABSENSI
    with tab1:
        st.subheader("Data Laporan Absensi")
        try:
            df_abs = conn.query("SELECT * FROM db_absensi ORDER BY id DESC;", ttl="0s")
            if len(df_abs) > 0:
                st.dataframe(df_abs, use_container_width=True)

                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    df_abs.to_excel(writer, index=False, sheet_name='Absensi')
                st.download_button(
                    label="📥 Download Excel - Absensi",
                    data=buffer.getvalue(),
                    file_name=f"Rekap_Absensi_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    type="primary"
                )
            else:
                st.info("Belum ada data Absensi di PostgreSQL.")
        except Exception as err:
            st.error(f"Gagal membaca tabel db_absensi: {err}")

    # TAB 2: OVERTIME
    with tab2:
        st.subheader("Data Laporan Overtime")
        try:
            df_ot = conn.query("SELECT * FROM db_overtime ORDER BY id DESC;", ttl="0s")
            if len(df_ot) > 0:
                st.dataframe(df_ot, use_container_width=True)

                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    df_ot.to_excel(writer, index=False, sheet_name='Overtime')
                st.download_button(
                    label="📥 Download Excel - Overtime",
                    data=buffer.getvalue(),
                    file_name=f"Rekap_Overtime_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    type="primary"
                )
            else:
                st.info("Belum ada data Overtime di PostgreSQL.")
        except Exception as err:
            st.error(f"Gagal membaca tabel db_overtime: {err}")

    # TAB 3: DAILY REPORT
    with tab3:
        st.subheader("Data Daily Report")
        try:
            df_dr = conn.query("SELECT * FROM db_daily_report ORDER BY id DESC;", ttl="0s")
            if len(df_dr) > 0:
                st.dataframe(df_dr, use_container_width=True)

                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    df_dr.to_excel(writer, index=False, sheet_name='DailyReport')
                st.download_button(
                    label="📥 Download Excel - Daily Report",
                    data=buffer.getvalue(),
                    file_name=f"Rekap_DailyReport_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    type="primary"
                )
            else:
                st.info("Belum ada data Daily Report di PostgreSQL.")
        except Exception as err:
            st.error(f"Gagal membaca tabel db_daily_report: {err}")

    st.write("---")
    if st.button("⬅️ Kembali ke Menu Utama", use_container_width=True, key="back_rekap"):
        st.session_state.page = 'select_menu'
        st.rerun()
