import streamlit as st
import pandas as pd
from datetime import datetime
import io
from sqlalchemy import text

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="PT. AFI - Report", layout="wide")

st.markdown("""
    <style>
    /* Mengatur lebar area utama aplikasi agar tidak terlalu lebar & tidak terlalu sempit */
    .block-container {
        max-width: 85% !important;
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        margin: auto !important;
    }
    
    /* Merampingkan dan menyejajarkan input box */
    div[data-baseweb="input"] {
        min-height: 32px !important;
    }
    .stTextInput input {
        padding: 4px 8px !important;
        font-size: 13px !important;
    }
    .stSelectbox div[data-baseweb="select"] {
        min-height: 32px !important;
    }
    
    /* Tombol Plus (+) & Tombol Standar Lainnya */
    div.stButton > button {
        height: 32px !important;
        padding: 0px 6px !important;
        font-size: 14px !important;
        line-height: 1 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        margin-top: 0px !important;
    }

    /* 🎨 WARNA BIRU UNTUK TOMBOL UTAMA & NAVIGASI */
    div.stButton > button:first-child {
        background-color: #78A4CB !important;
        color: white !important;
        border-radius: 6px !important;
        border: none !important;
        font-weight: bold !important;
        transition: 0.3s;
    }
    
    /* Efek saat tombol di-hover (diarahkan kursor) */
    div.stButton > button:first-child:hover {
        background-color: #2F578A !important;
        color: white !important;
        border: none !important;
    }

    /* Menjaga Tombol SUBMIT/Primary tetap berwarna Merah */
    div.stButton > button[kind="primary"] {
        background-color: #ff4b4b !important;
        color: white !important;
    }
    div.stButton > button[kind="primary"]:hover {
        background-color: #d33333 !important;
        color: white !important;
    }

    /* Style khusus header tabel */
    .table-header {
        font-size: 13px;
        font-weight: bold;
        white-space: nowrap;
        text-align: left;
        margin-bottom: 5px;
    }
    </style>
""", unsafe_allow_html=True)
# --- KONEKSI KE DATABASE POSTGRESQL ---
try:
    conn = st.connection("postgresql", type="sql")
except Exception as e:
    st.error("Gagal terhubung ke database PostgreSQL. Pastikan PostgreSQL berjalan dan file .streamlit/secrets.toml sudah dikonfigurasi dengan benar.")

# --- FUNGSI RESET DATA SHIFT SCHEDULE (SCHEDULE SHIFT) ---
def reset_data_ot():
    st.session_state.data_rows_ot = [
        {"nama": "", "nik": "", "section": "", "job": "", "jemputan": "", "nohp": "", "shift": "1"}
    ]
    for key in list(st.session_state.keys()):
        if (key.startswith("ot_nama_") or key.startswith("ot_nik_") or key.startswith("ot_section_") or 
            key.startswith("ot_job_") or key.startswith("ot_jemputan_") or key.startswith("ot_nohp_") or key.startswith("ot_shift_")):
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
        {"nama": "", "nik": "", "section": "", "job": "", "jemputan": "", "nohp": "", "shift": "1"}
    ]

if 'dr_step' not in st.session_state:
    st.session_state.dr_step = 1
if 'dr_category' not in st.session_state:
    st.session_state.dr_category = ""
if 'dr_work_type' not in st.session_state:
    st.session_state.dr_work_type = "Regular"


# =====================================================================
# 1. HALAMAN LOGIN (AKUN STATIS: admin / 1234)
# =====================================================================
if st.session_state.page == 'login':
    st.markdown("<h2 style='text-align: center;'>AFi - Report</h2>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center;'>PT. Automotive Fasteners Aoyama Indonesia</h4>", unsafe_allow_html=True)
    st.write("---")
    
    # Input Username dan Password
    nama_user = st.text_input("Username :")
    nik_user = st.text_input("Password :", type="password")  # type="password" agar karakter tersamar
    
    st.write("")
    if st.button("Login", use_container_width=True):
        # Validasi akun statis (Username: admin & Password: 1234)
        if nama_user.strip() == "rorojonggrang" and nik_user.strip() == "pr4mb4n4n1927":
            st.session_state.user_info = {"nama": nama_user, "nik": "Administrator"}
            st.session_state.page = 'select_menu'
            st.success("Login Berhasil!")
            st.rerun()
        else:
            st.error("Username atau Password salah!")
# =====================================================================
# 2. HALAMAN SELECT MENU (DESAIN CLEAN + LOGOUT DI POJOK KANAN BAWAH)
# =====================================================================
elif st.session_state.page == 'select_menu':
    st.markdown("<h4 style='text-align: right; color:#555; margin-bottom:0px;'>PT. Automotive Fasteners Aoyama Indonesia</h4>", unsafe_allow_html=True)
    st.title("📋 Select Page")
    st.write(f"Logged in as: **{st.session_state.user_info.get('nama', '')}**")
    st.write("---")
     
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Schedule Shift", use_container_width=True):
            st.session_state.menu_params = {}
            reset_data_ot()
            st.session_state.page = 'input_overtime'
            st.rerun()

    with col2:
        if st.button("Attendance", use_container_width=True):
            st.session_state.menu_params = {}
            st.session_state.page = 'input_absensi'
            st.rerun()

    with col3:
        if st.button("Daily Report", use_container_width=True):
            st.session_state.menu_params = {}
            st.session_state.dr_step = 1
            st.session_state.page = 'input_daily_report'
            st.rerun()

    st.write("")
    if st.button("Summary Report", use_container_width=True, type="secondary"):
        st.session_state.page = 'rekap_data'
        st.rerun()

    st.write("---")

    # BARIS PALING BAWAH: Sub-kolom untuk menggeser tombol Logout ke Pojok Kanan Bawah
    col_bot_left, col_bot_right = st.columns([6, 1])
    with col_bot_right:
        if st.button("Logout", key="btn_logout_bottom_right", use_container_width=True, type="primary"):
            st.session_state.user_info = {}
            st.session_state.page = 'login'
            st.success("Berhasil Logout!")
            st.rerun()
# =====================================================================
# 3. HALAMAN INPUT ABSENSI (SESUAI STRUKTUR POSTGRESQL TERBARU)
# =====================================================================
elif st.session_state.page == 'input_absensi':
    st.markdown("<h4 style='text-align: right; color:#555; margin-bottom:0px;'>PT. Automotive Fasteners Aoyama Indonesia</h4>", unsafe_allow_html=True)
    st.title("📝 Attendance Page")
    st.write(f"Logged in as: **{st.session_state.user_info.get('nama', '')}**")
    p = st.session_state.get('menu_params', {})
    
    st.write("---")
    
    # 1. PERIODE 2 KOLOM TANGGAL TERPISAH
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        tgl_mulai_abs = st.date_input("Dari Tanggal :", value=datetime.now(), key="abs_tgl_mulai")
    with col_p2:
        tgl_selesai_abs = st.date_input("Sampai Tanggal :", value=datetime.now(), key="abs_tgl_selesai")
    
    # Format teks periode
    str_mulai_abs = tgl_mulai_abs.strftime("%d/%m/%Y")
    str_selesai_abs = tgl_selesai_abs.strftime("%d/%m/%Y")
    if str_mulai_abs == str_selesai_abs:
        periode_abs_val = str_mulai_abs
    else:
        periode_abs_val = f"{str_mulai_abs} s/d {str_selesai_abs}"

    # 2. MENGAMBIL TOTAL MEMBER DARI DATABASE DB_SHIFT
    total_member_db = 0
    try:
        df_shift_member = conn.query("SELECT COUNT(*) as total FROM db_shift;", ttl="0s")
        if len(df_shift_member) > 0:
            total_member_db = int(df_shift_member['total'].iloc[0])
    except Exception as e:
        total_member_db = 0

    col_a, col_b = st.columns(2)
    with col_a:
        shift = st.selectbox("Shift :", ["Shift 1", "Shift 2", "Non-Shift"])
        leader = st.text_input("Leader :")
    with col_b:
        total_member = st.number_input("Total Member (Schedule Shift) :", min_value=0, value=total_member_db, step=1)

    # 3. MENGHITUNG TOTAL TIDAK HADIR UNTUK RINGKASAN
    kategori_absensi = ["Sakit", "Cuti Terencana", "Cuti Dadakan", "Cuti Khusus", "Izin", "Terlambat", "OSD"]
    
    if 'jumlah_input_absensi' not in st.session_state:
        st.session_state.jumlah_input_absensi = {kat: 1 for kat in kategori_absensi}

    total_tidak_hadir = 0
    for kat in kategori_absensi:
        for i in range(st.session_state.jumlah_input_absensi[kat]):
            nama_val = st.session_state.get(f"input_{kat}_{i}", "")
            if nama_val.strip() != "":
                total_tidak_hadir += 1

    total_hadir = total_member - total_tidak_hadir
    if total_hadir < 0:
        total_hadir = 0

    st.write("---")

    # 📌 DASHBOARD KOTAK RINGKASAN DI ATAS
    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        st.markdown(f"<div style='background-color:#e2e3e5; padding:10px; border-radius:5px; text-align:center;'><b>Total Member</b><br><span style='font-size:20px;'>{total_member}</span></div>", unsafe_allow_html=True)
    with col_m2:
        st.markdown(f"<div style='background-color:#f8d7da; padding:10px; border-radius:5px; text-align:center; color:#721c24;'><b>Total Tidak Hadir</b><br><span style='font-size:20px;'>{total_tidak_hadir} </span></div>", unsafe_allow_html=True)
    with col_m3:
        st.markdown(f"<div style='background-color:#d4edda; padding:10px; border-radius:5px; text-align:center; color:#155724;'><b>Total Hadir</b><br><span style='font-size:20px; font-weight:bold;'>{total_hadir}</span></div>", unsafe_allow_html=True)

    st.write("---")
    st.subheader("Detail Ketidakhadiran / Kondisi:")

    # 4. RENDER INPUT NAMA BERDASARKAN KATEGORI
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
        if st.button("Submit Attendance", use_container_width=True, type="primary"):
            with conn.engine.begin() as connection:
                for kat, list_nama in data_nama_terinput.items():
                    for nm in list_nama:
                        if nm.strip() != "":
                            # QUERY HANYA MEMASUKKAN KOLOM YANG TERSEDIA DI TABEL DB_ABSENSI
                            query = text("""
                                INSERT INTO db_absensi (user_input, tanggal, shift, leader, total_member, kategori, nama_karyawan)
                                VALUES (:user_input, :tanggal, :shift, :leader, :total_member, :kategori, :nama_karyawan)
                            """)
                            connection.execute(query, {
                                "user_input": st.session_state.user_info.get("nama", ""),
                                "tanggal": str(periode_abs_val),
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
# 4. HALAMAN SCHEDULE SHIFT (MENYIMPAN KE TABEL DB_SHIFT)
# =====================================================================
elif st.session_state.page == 'input_overtime':    
    # Header Judul PT. AFI
    st.markdown("<h4 style='text-align: right; color:#555; margin-bottom:0px;'>PT. Automotive Fasteners Aoyama Indonesia</h4>", unsafe_allow_html=True)
    st.title("📝 Schedule Shift")
    st.write(f"Logged in as: **{st.session_state.user_info.get('nama', '')}**")
    st.write("---")
    st.write("")
    
    # PERIODE 2 KOLOM TANGGAL TERPISAH
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        tgl_mulai_input = st.date_input("Dari Tanggal :", value=datetime.now(), key="ot_tgl_mulai")
    with col_p2:
        tgl_selesai_input = st.date_input("Sampai Tanggal :", value=datetime.now(), key="ot_tgl_selesai")
    
    # Format teks periode otomatis
    str_mulai = tgl_mulai_input.strftime("%d/%m/%Y")
    str_selesai = tgl_selesai_input.strftime("%d/%m/%Y")
    if str_mulai == str_selesai:
        periode_val = str_mulai
    else:
        periode_val = f"{str_mulai} s/d {str_selesai}"

    st.write("---")
    
    # Sub-header Tabel Database Quality Member
    st.markdown("<div style='background-color:#e9ecef; border:1px solid #ccc; text-align:center; padding:6px; font-weight:bold; font-size:15px; border-radius:4px;'>Database Quality Member</div>", unsafe_allow_html=True)
    st.write("")
    
    # PROPORSI RASIO DIPERBAIKI SANGAT PAS
    ratio_cols = [0.6, 2.0, 1.1, 1.1, 1.5, 1.5, 1.3, 1.0, 0.5]

    # Header Judul Kolom
    col_l0, col_l1, col_l2, col_l3, col_l4, col_l5, col_l6, col_l7, col_l8 = st.columns(ratio_cols)
    col_l0.markdown("<div class='table-header'>No</div>", unsafe_allow_html=True)
    col_l1.markdown("<div class='table-header' style='text-align:left;'>Nama</div>", unsafe_allow_html=True)
    col_l2.markdown("<div class='table-header' style='text-align:left;'>NIK</div>", unsafe_allow_html=True)
    col_l3.markdown("<div class='table-header' style='text-align:left;'>Section</div>", unsafe_allow_html=True)
    col_l4.markdown("<div class='table-header' style='text-align:left;'>Job</div>", unsafe_allow_html=True)
    col_l5.markdown("<div class='table-header' style='text-align:left;'>Titik Jemputan</div>", unsafe_allow_html=True)
    col_l6.markdown("<div class='table-header' style='text-align:left;'>No HP</div>", unsafe_allow_html=True)
    col_l7.markdown("<div class='table-header' style='text-align:left;'>Shift</div>", unsafe_allow_html=True)
    col_l8.markdown("<div class='table-header'>[+]</div>", unsafe_allow_html=True)

    # Render Baris Input Dinamis
    for i, row in enumerate(st.session_state.data_rows_ot):
        c0, c1, c2, c3, c4, c5, c6, c7, c8 = st.columns(ratio_cols)
        
        with c0:
            st.markdown(f"<div style='text-align:center; padding-top:6px; font-size:13px; font-weight:bold;'>{i+1}</div>", unsafe_allow_html=True)
        with c1:
            st.session_state.data_rows_ot[i]["nama"] = st.text_input("Nama", value=row.get("nama", ""), key=f"ot_nama_{i}", label_visibility="collapsed", placeholder="Nama")
        with c2:
            st.session_state.data_rows_ot[i]["nik"] = st.text_input("NIK", value=row.get("nik", ""), key=f"ot_nik_{i}", label_visibility="collapsed", placeholder="NIK")
        with c3:
            st.session_state.data_rows_ot[i]["section"] = st.text_input("Section", value=row.get("section", ""), key=f"ot_section_{i}", label_visibility="collapsed", placeholder="Sec")
        with c4:
            st.session_state.data_rows_ot[i]["job"] = st.text_input("Job", value=row.get("job", ""), key=f"ot_job_{i}", label_visibility="collapsed", placeholder="Job")
        with c5:
            st.session_state.data_rows_ot[i]["jemputan"] = st.text_input("Jemputan", value=row.get("jemputan", ""), key=f"ot_jemputan_{i}", label_visibility="collapsed", placeholder="Titik")
        with c6:
            st.session_state.data_rows_ot[i]["nohp"] = st.text_input("No HP", value=row.get("nohp", ""), key=f"ot_nohp_{i}", label_visibility="collapsed", placeholder="08xxx")
        with c7:
            opts_shift = ["Shift 1", "Shift 2", "Non-Shift"]
            s_val = str(row.get("shift", "1"))
            idx_s = opts_shift.index(s_val) if s_val in opts_shift else 0
            st.session_state.data_rows_ot[i]["shift"] = st.selectbox("Shift", options=opts_shift, index=idx_s, key=f"ot_shift_{i}", label_visibility="collapsed")
        with c8:
            if i == len(st.session_state.data_rows_ot) - 1:
                if st.button("➕", key=f"btn_ot_plus_{i}"):
                    for k in range(len(st.session_state.data_rows_ot)):
                        st.session_state.data_rows_ot[k]["nama"] = st.session_state.get(f"ot_nama_{k}", "")
                        st.session_state.data_rows_ot[k]["nik"] = st.session_state.get(f"ot_nik_{k}", "")
                        st.session_state.data_rows_ot[k]["section"] = st.session_state.get(f"ot_section_{k}", "")
                        st.session_state.data_rows_ot[k]["job"] = st.session_state.get(f"ot_job_{k}", "")
                        st.session_state.data_rows_ot[k]["jemputan"] = st.session_state.get(f"ot_jemputan_{k}", "")
                        st.session_state.data_rows_ot[k]["nohp"] = st.session_state.get(f"ot_nohp_{k}", "")
                        st.session_state.data_rows_ot[k]["shift"] = st.session_state.get(f"ot_shift_{k}", "1")
                    
                    st.session_state.data_rows_ot.append({
                        "nama": "", "nik": "", "section": "", "job": "", "jemputan": "", "nohp": "", "shift": "1"
                    })
                    st.rerun()

    st.write("---")
    col_submit1, col_submit2 = st.columns(2)
    with col_submit1:
        if st.button("Submit Schedule Shift", use_container_width=True, type="primary", key="submit_ot_final"):
            with conn.engine.begin() as connection:
                for k, row_ot in enumerate(st.session_state.data_rows_ot):
                    nm_ot = st.session_state.get(f"ot_nama_{k}", row_ot["nama"]).strip()
                    if nm_ot != "":
                        query = text("""
                            INSERT INTO db_shift (user_input, periode, nama, nik, section, job, titik_jemputan, no_hp, shift)
                            VALUES (:user_input, :periode, :nama, :nik, :section, :job, :titik_jemputan, :no_hp, :shift)
                        """)
                        connection.execute(query, {
                            "user_input": str(st.session_state.user_info.get("nama", "")),
                            "periode": str(periode_val),
                            "nama": str(nm_ot),
                            "nik": str(st.session_state.get(f"ot_nik_{k}", row_ot["nik"])),
                            "section": str(st.session_state.get(f"ot_section_{k}", row_ot["section"])),
                            "job": str(st.session_state.get(f"ot_job_{k}", row_ot["job"])),
                            "titik_jemputan": str(st.session_state.get(f"ot_jemputan_{k}", row_ot["jemputan"])),
                            "no_hp": str(st.session_state.get(f"ot_nohp_{k}", row_ot["nohp"])),
                            "shift": str(st.session_state.get(f"ot_shift_{k}", row_ot["shift"]))
                        })

            st.success("Data Schedule Shift Berhasil Disimpan ke PostgreSQL (db_shift)!")
            reset_data_ot()
            st.session_state.page = 'select_menu'
            st.rerun()

    with col_submit2:
        if st.button("Kembali ke Menu Utama", use_container_width=True, key="back_ot_final"):
            reset_data_ot()
            st.session_state.page = 'select_menu'
            st.rerun()
# =====================================================================
# 5. HALAMAN INPUT DAILY REPORT (AMBIL NAMA DARI DB_SHIFT)
# =====================================================================
elif st.session_state.page == 'input_daily_report':
    st.markdown("<h4 style='text-align: right; color:#555; margin-bottom:0px;'>PT. Automotive Fasteners Aoyama Indonesia</h4>", unsafe_allow_html=True)
    st.title("📝 Daily Report Page")
    st.write(f"Logged in as: **{st.session_state.user_info.get('nama', '')}**")
    
    # -----------------------------------------------------------------
    # MENGAMBIL DATA HEADER & TOTAL MP HADIR DARI ABSENSI / SHIFT
    # -----------------------------------------------------------------
    shift_val = "Shift 1"
    leader_val = "-"
    total_mp_hadir = 0
    
    try:
        df_abs_last = conn.query("SELECT shift, leader, total_member FROM db_absensi ORDER BY id DESC LIMIT 1;", ttl="0s")
        if len(df_abs_last) > 0:
            shift_val = df_abs_last['shift'].iloc[0]
            leader_val = df_abs_last['leader'].iloc[0]
            tot_mem = int(df_abs_last['total_member'].iloc[0])
            
            df_absen_count = conn.query("""
                SELECT COUNT(*) as tidak_hadir 
                FROM db_absensi 
                WHERE waktu_submit = (SELECT MAX(waktu_submit) FROM db_absensi);
            """, ttl="0s")
            
            tot_tidak_hadir = int(df_absen_count['tidak_hadir'].iloc[0]) if len(df_absen_count) > 0 else 0
            total_mp_hadir = tot_mem - tot_tidak_hadir
            if total_mp_hadir < 0:
                total_mp_hadir = 0
        else:
            df_shift_count = conn.query("SELECT COUNT(*) as total FROM db_shift;", ttl="0s")
            if len(df_shift_count) > 0:
                total_mp_hadir = int(df_shift_count['total'].iloc[0])
    except Exception as e:
        total_mp_hadir = 0

    # -----------------------------------------------------------------
    # AMBIL DAFTAR NAMA DARI SCHEDULE SHIFT (DB_SHIFT)
    # -----------------------------------------------------------------
    try:
        df_nama_shift = conn.query("SELECT DISTINCT nama FROM db_shift WHERE nama IS NOT NULL AND nama != '' ORDER BY nama ASC;", ttl="0s")
        list_nama_shift = df_nama_shift['nama'].tolist() if len(df_nama_shift) > 0 else []
    except Exception as e:
        list_nama_shift = []

    # -----------------------------------------------------------------
    # HEADER: HARI/TANGGAL, SHIFT & TOTAL MP
    # -----------------------------------------------------------------
    col_hdr1, col_hdr2 = st.columns(2)
    with col_hdr1:
        tgl_dr = st.date_input("Hari / Tanggal :", value=datetime.now(), key="dr_tgl_input")
    with col_hdr2:
        shift_dr = st.selectbox("Shift :", ["Shift 1", "Shift 2", "Non-Shift"], index=0 if shift_val=="Shift 1" else (1 if shift_val=="Shift 2" else 2), key="dr_shift_sel")

    st.markdown(
        f"""
        <div style='background-color:#d4edda; padding:12px; border-radius:6px; text-align:center; border:1px solid #c3e6cb; margin-top:10px; margin-bottom:15px; width:100%;'>
            <div style='font-size:14px; font-weight:bold; color:#155724; margin-bottom:4px;'>Total MP</div>
            <div style='font-size:20px; font-weight:bold; color:#155724;'>{total_mp_hadir} Orang</div>
        </div>
        """, 
        unsafe_allow_html=True
    )
    st.write("---")

    # -----------------------------------------------------------------
    # FORM INPUT UTAMA DAILY REPORT
    # -----------------------------------------------------------------
    # 1. Dropdown Nama Karyawan (Mengambil dari db_shift)
    if list_nama_shift:
        nama_dr = st.selectbox("Nama :", options=list_nama_shift, key="dr_nama_select")
    else:
        st.warning("⚠️ Data Schedule Shift belum ada. Silakan ketik nama secara manual:")
        nama_dr = st.text_input("Nama :", key="dr_nama_manual")

    # 2. Job / Kategori Pekerjaan
    list_job = [
        "QA", "QC Factory", "Lokal Meja FI", "Lokal Vinyl DDMI", "Lokal Machine", 
        "Engine Bolt", "Sugin", "Q-Gate", "Hardness", "Measurement", 
        "Sortir 100%", "Leader", "Others"
    ]
    job_terpilih = st.multiselect("Job / Kategori Pekerjaan :", options=list_job, key="dr_job_multiselect")
    
    job_others = ""
    if "Others" in job_terpilih:
        job_others = st.text_input("Sebutkan Job Lainnya :", key="dr_job_others")

    # 3. Jam Kerja Regular & OT
    col_j1, col_j2 = st.columns(2)
    with col_j1:
        jam_regular = st.number_input("Jam Kerja Regular (Jam) :", min_value=0.0, step=0.5, key="dr_jam_regular")
    with col_j2:
        jam_ot = st.number_input("Jam Kerja OT (Jam) :", min_value=0.0, step=0.5, key="dr_jam_ot")

    # 4. Jumlah Box Regular & OT
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        box_regular = st.number_input("Jumlah Box Regular :", min_value=0, step=1, key="dr_box_regular")
    with col_b2:
        box_ot = st.number_input("Jumlah Box OT :", min_value=0, step=1, key="dr_box_ot")

    # 5. Total Box / Job
    total_box_job = box_regular + box_ot
    st.markdown(f"**Total Box / Job :**")
    st.markdown(f"<div style='background-color:#e2e3e5; padding:8px; border-radius:4px; text-align:center; font-weight:bold; border:1px solid #d6d8db; color:#383d41; margin-bottom:15px;'>{total_box_job} Box</div>", unsafe_allow_html=True)

    # 6. Keterangan
    keterangan_dr = st.text_area("Keterangan :", placeholder="Tambahkan catatan atau keterangan pekerjaan di sini...", key="dr_keterangan")

    st.write("---")
    col_submit1, col_submit2 = st.columns(2)
    
    with col_submit1:
        if st.button("Submit Daily Report", use_container_width=True, type="primary", key="submit_dr_final"):
            if not nama_dr.strip():
                st.error("Silakan isi Nama terlebih dahulu!")
            elif not job_terpilih:
                st.error("Silakan pilih minimal satu Job!")
            else:
                str_job = ", ".join(job_terpilih)
                if "Others" in job_terpilih and job_others.strip():
                    str_job = str_job.replace("Others", f"Others ({job_others.strip()})")

                str_tgl_dr = tgl_dr.strftime("%Y-%m-%d")
                str_thn_dr = tgl_dr.strftime("%Y")
                str_bln_dr = tgl_dr.strftime("%B")
                
                with conn.engine.begin() as connection:
                    query = text("""
                        INSERT INTO db_daily_report (
                            user_input, tahun, bulan, tanggal, shift, nama, job_kategori, 
                            jam_regular, jam_ot, box_regular, box_ot, total_box_job, keterangan
                        )
                        VALUES (
                            :user_input, :tahun, :bulan, :tanggal, :shift, :nama, :job_kategori, 
                            :jam_regular, :jam_ot, :box_regular, :box_ot, :total_box_job, :keterangan
                        )
                    """)
                    connection.execute(query, {
                        "user_input": st.session_state.user_info.get("nama", ""),
                        "tahun": str_thn_dr,
                        "bulan": str_bln_dr,
                        "tanggal": str_tgl_dr,
                        "shift": shift_dr,
                        "nama": nama_dr,
                        "job_kategori": str_job,
                        "jam_regular": jam_regular,
                        "jam_ot": jam_ot,
                        "box_regular": box_regular,
                        "box_ot": box_ot,
                        "total_box_job": total_box_job,
                        "keterangan": keterangan_dr
                    })

                st.success("Daily Report Berhasil Disimpan ke Database!")
                st.session_state.page = 'select_menu'
                st.rerun()

    with col_submit2:
        if st.button("Kembali ke Menu Utama", use_container_width=True, key="back_dr_final"):
            st.session_state.page = 'select_menu'
            st.rerun()
# =====================================================================
# 6. HALAMAN REKAP DATA 
# =====================================================================
elif st.session_state.page == 'rekap_data':
    st.title("📊 Summary Report")
    st.caption("Rekapitulasi seluruh data laporan PT. Automotive Fasteners Aoyama Indonesia")
    st.write("---")

    # Membuat 3 Tab Laporan
    tab1, tab2, tab3 = st.tabs(["⏰ Schedule Shift", "📋 Attendance", "📝 Daily Report"])

    # --- TAB 1: SCHEDULE SHIFT ---
    with tab1:
        st.subheader("Data Schedule Shift")
        try:
            df_ot = conn.query("SELECT * FROM db_shift ORDER BY id DESC;", ttl="0s")
            if len(df_ot) > 0:
                st.dataframe(df_ot, use_container_width=True)

                col_dl_ot, col_del_ot = st.columns([2, 1])
                with col_dl_ot:
                    buffer = io.BytesIO()
                    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                        df_ot.to_excel(writer, index=False, sheet_name='ScheduleShift')
                    st.download_button(
                        label="📥 Download Excel - Schedule Shift",
                        data=buffer.getvalue(),
                        file_name=f"Rekap_ScheduleShift_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        type="secondary",
                        key="dl_excel_shift"
                    )

                # FITUR DELETE DATA SHIFT
                with col_del_ot:
                    confirm_del_shift = st.checkbox("Konfirmasi hapus seluruh data Schedule Shift", key="chk_del_shift")
                    if st.button("🗑️ Hapus Semua Data ScheduleShift", type="primary", key="btn_del_shift", disabled=not confirm_del_shift):
                        with conn.engine.begin() as connection:
                            connection.execute(text("TRUNCATE TABLE db_shift RESTART IDENTITY;"))
                        st.success("Seluruh data Schedule Shift berhasil dihapus!")
                        st.rerun()
            else:
                st.info("Belum ada data Schedule Shift di database.")
        except Exception as err:
            st.error(f"Gagal membaca data db_shift: {err}")

    # --- TAB 2: DATA ABSENSI ---
    with tab2:
        st.subheader("Data Attendence")
        try:
            df_abs = conn.query("SELECT * FROM db_absensi ORDER BY id DESC;", ttl="0s")
            if len(df_abs) > 0:
                st.dataframe(df_abs, use_container_width=True)

                col_dl_abs, col_del_abs = st.columns([2, 1])
                with col_dl_abs:
                    buffer = io.BytesIO()
                    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                        df_abs.to_excel(writer, index=False, sheet_name='Absensi')
                    st.download_button(
                        label="📥 Download Excel - Attendance",
                        data=buffer.getvalue(),
                        file_name=f"Rekap_Absensi_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        type="secondary",
                        key="dl_excel_abs"
                    )

                # FITUR DELETE DATA ABSENSI
                with col_del_abs:
                    confirm_del_abs = st.checkbox("Konfirmasi hapus seluruh data Attendance", key="chk_del_abs")
                    if st.button("🗑️ Hapus Semua Data Attendence", type="primary", key="btn_del_abs", disabled=not confirm_del_abs):
                        with conn.engine.begin() as connection:
                            connection.execute(text("TRUNCATE TABLE db_absensi RESTART IDENTITY;"))
                        st.success("Seluruh data Attendence berhasil dihapus!")
                        st.rerun()
            else:
                st.info("Belum ada data Attendence di database.")
        except Exception as err:
            st.error(f"Gagal membaca data db_absensi: {err}")

    # --- TAB 3: DAILY REPORT ---
    with tab3:
        st.subheader("Data Daily Report")
        try:
            df_dr = conn.query("SELECT * FROM db_daily_report ORDER BY id DESC;", ttl="0s")
            if len(df_dr) > 0:
                st.dataframe(df_dr, use_container_width=True)

                col_dl_dr, col_del_dr = st.columns([2, 1])
                with col_dl_dr:
                    buffer = io.BytesIO()
                    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                        df_dr.to_excel(writer, index=False, sheet_name='DailyReport')
                    st.download_button(
                        label="📥 Download Excel - Daily Report",
                        data=buffer.getvalue(),
                        file_name=f"Rekap_DailyReport_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        type="secondary",
                        key="dl_excel_dr"
                    )

                # FITUR DELETE DATA DAILY REPORT
                with col_del_dr:
                    confirm_del_dr = st.checkbox("Konfirmasi hapus seluruh data Daily Report", key="chk_del_dr")
                    if st.button("🗑️ Hapus Semua Data Daily Report", type="primary", key="btn_del_dr", disabled=not confirm_del_dr):
                        with conn.engine.begin() as connection:
                            connection.execute(text("TRUNCATE TABLE db_daily_report RESTART IDENTITY;"))
                        st.success("Seluruh data Daily Report berhasil dihapus!")
                        st.rerun()
            else:
                st.info("Belum ada data Daily Report di database.")
        except Exception as err:
            st.error(f"Gagal membaca data db_daily_report: {err}")

    st.write("---")
    if st.button("⬅️ Kembali ke Menu Utama", use_container_width=True, key="back_rekap_main"):
        st.session_state.page = 'select_menu'
        st.rerun()