import streamlit as st
import sqlite3
import hashlib

# ==========================================
# PILAR 1 & 3: DATABASE & PEMISAHAN LOGIKA
# ==========================================
DB_FILE = "lost_and_found.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # Tabel laporan
    c.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            jenis TEXT,
            nama TEXT,
            lokasi TEXT,
            kontak TEXT,
            status TEXT
        )
    ''')
    # Tabel user admin
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT,
            role TEXT
        )
    ''')
    # Akun default admin (Username: admin, Password: admin123)
    pwd_hash = hashlib.sha256("admin123".encode()).hexdigest()
    c.execute("INSERT OR IGNORE INTO users VALUES ('admin', ?, 'Admin')", (pwd_hash,))
    conn.commit()
    conn.close()

def get_reports():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, jenis, nama, lokasi, kontak, status FROM reports ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return rows

def add_report(jenis, nama, lokasi, kontak):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO reports (jenis, nama, lokasi, kontak, status) VALUES (?, ?, ?, ?, 'Belum Selesai')",
              (jenis, nama, lokasi, kontak))
    conn.commit()
    conn.close()

def update_status(report_id, status):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE reports SET status = ? WHERE id = ?", (status, report_id))
    conn.commit()
    conn.close()

def delete_report(report_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM reports WHERE id = ?", (report_id,))
    conn.commit()
    conn.close()

def check_login(username, password):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    pwd_hash = hashlib.sha256(password.encode()).hexdigest()
    c.execute("SELECT role FROM users WHERE username = ? AND password = ?", (username, pwd_hash))
    user = c.fetchone()
    conn.close()
    return user[0] if user else None

# Inisialisasi DB
init_db()

# ==========================================
# TAMPILAN UTAMA & OTENTIKASI
# ==========================================
st.set_page_config(page_title="Digital Lost & Found", page_icon="🔍", layout="wide")
st.title("🏫 Digital Lost & Found Sekolah")

if "role" not in st.session_state:
    st.session_state["role"] = "Guest"

# Sidebar untuk Otentikasi / Hak Akses
with st.sidebar:
    st.header("🔐 Akses Sistem")
    if st.session_state["role"] == "Guest":
        st.subheader("Login Petugas / Admin")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            role = check_login(username, password)
            if role:
                st.session_state["role"] = role
                st.success(f"Berhasil login sebagai {role}")
                st.rerun()
            else:
                st.error("Username/Password salah!")
    else:
        st.success(f"Status Login: **{st.session_state['role']}**")
        if st.button("Logout"):
            st.session_state["role"] = "Guest"
            st.rerun()

# Form Pengaduan Barang Hilang/Ditemukan (Public)
st.subheader("📝 Buat Laporan Barang Hilang / Ditemukan")
with st.form("form_laporan", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        jenis = st.selectbox("Jenis Laporan", ["Hilang", "Ditemukan"])
        nama = st.text_input("Nama Barang")
    with col2:
        lokasi = st.text_input("Lokasi Kejadian")
        kontak = st.text_input("Kontak (No. HP/WA)")
    
    submit = st.form_submit_button("Kirim Laporan")

if submit:
    if not nama or not lokasi or not kontak:
        st.warning("Harap isi semua kolom dengan lengkap.")
    else:
        add_report(jenis, nama, lokasi, kontak)
        st.success("Laporan berhasil disimpan ke database!")
        st.rerun()

st.divider()

# Daftar Laporan
st.subheader("📋 Daftar Laporan Barang")
laporan_list = get_reports()

if not laporan_list:
    st.info("Belum ada laporan barang hilang/ditemukan.")
else:
    for item in laporan_list:
        report_id, r_jenis, r_nama, r_lokasi, r_kontak, r_status = item
        
        with st.container(border=True):
            col_a, col_b, col_c = st.columns([2, 3, 2])
            with col_a:
                if r_jenis == "Hilang":
                    st.error("🚨 HILANG")
                else:
                    st.success("🔍 DITEMUKAN")
                st.write(f"**Status:** {r_status}")
            
            with col_b:
                st.markdown(f"### {r_nama}")
                st.write(f"📍 **Lokasi:** {r_lokasi}")
                st.write(f"📞 **Kontak:** {r_kontak}")
            
            with col_c:
                # PILAR KEAMANAN: Hanya Admin/Petugas yang bisa ubah status / hapus
                if st.session_state["role"] == "Admin":
                    if r_status != "Selesai":
                        if st.button("Tandai Selesai", key=f"done_{report_id}"):
                            update_status(report_id, "Selesai")
                            st.rerun()
                    if st.button("Hapus Laporan", key=f"del_{report_id}"):
                        delete_report(report_id)
                        st.rerun()
                else:
                    st.caption("🔒 *Login sebagai Admin untuk mengubah/menghapus laporan.*")
