import streamlit as st
import json
import os

FILE = "data.json"

def baca_data():
    if os.path.exists(FILE):
        with open(FILE) as f:
            return json.load(f)
    return []

def simpan_data(data):
    with open(FILE, "w") as f:
        json.dump(data, f)

st.title("Digital Lost & Found")
data = baca_data()

with st.form("form_laporan"):
    jenis = st.radio("Jenis", ["Hilang", "Ditemukan"])
    nama = st.text_input("Nama barang")
    lokasi = st.text_input("Lokasi")
    kontak = st.text_input("Kontak")
    kirim = st.form_submit_button("Kirim")

if kirim:
    if nama == "":
        st.warning("Nama barang wajib diisi")
    else:
        laporan = {
            "jenis": jenis,
            "nama": nama,
            "lokasi": lokasi,
            "kontak": kontak,
            "status": "Belum selesai"
        }
        data.append(laporan)
        simpan_data(data)
        st.success("Laporan tersimpan!")

st.subheader("Daftar Laporan")
for i, item in enumerate(data):
    with st.container(border=True):
        if item["jenis"] == "Hilang":
            st.error("HILANG")
        else:
            st.success("DITEMUKAN")
        st.subheader(item["nama"])
        st.write("Lokasi:", item["lokasi"])
        st.write("Kontak:", item["kontak"])
        st.write("Status:", item["status"])

        if st.button("Tandai Selesai", key=f"s{i}"):
            data[i]["status"] = "Selesai"
            simpan_data(data)
            st.rerun()

        if st.button("Hapus", key=f"h{i}"):
            data.pop(i)
            simpan_data(data)
            st.rerun()