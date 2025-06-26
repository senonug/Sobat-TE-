
import streamlit as st
import pandas as pd
import numpy as np
import io

# -------------------------------
# Login Section
# -------------------------------
if "login" not in st.session_state:
    st.session_state.login = False

if not st.session_state.login:
    st.title("🔐 Login Dashboard P2TL AMR")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == "admin" and password == "1234":
            st.session_state.login = True
            st.success("Login berhasil!")
        else:
            st.error("Username atau password salah")
    st.stop()

# -------------------------------
# Header Dashboard
# -------------------------------
st.set_page_config(page_title="Dashboard P2TL AMR", layout="wide")
st.markdown("<h1 style='text-align: center; color: navy;'>📊 Dashboard Target Operasi P2TL AMR - Juni 2025</h1>", unsafe_allow_html=True)
st.markdown("---")

# -------------------------------
# Upload OLAP Pascabayar
# -------------------------------
st.sidebar.header("📂 Upload Data Referensi")
uploaded_olap = st.sidebar.file_uploader("Upload Data OLAP Pascabayar (Excel)", type=["xlsx"])
if uploaded_olap:
    df_olap = pd.read_excel(uploaded_olap)
    st.sidebar.success("Data OLAP berhasil diunggah")
else:
    df_olap = pd.DataFrame()

# -------------------------------
# Parameter Setting
# -------------------------------
with st.expander("⚙️ Setting Parameter Deteksi"):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader("Tegangan Drop")
        vdrop_tm = st.number_input("Batas Tegangan Menengah (tm) <", value=56.0)
        vdrop_tr = st.number_input("Batas Tegangan Rendah (tr) <", value=180.0)
        idrop_tm = st.number_input("Batas Arus Besar tm >", value=0.5)
        idrop_tr = st.number_input("Batas Arus Besar tr >", value=0.5)

    with col2:
        st.subheader("Arus Hilang")
        ihilang_tm = st.number_input("Arus Hilang tm >", value=0.02)
        ihilang_tr = st.number_input("Arus Hilang tr >", value=0.02)
        imax = st.number_input("Arus Maksimum >", value=1.0)

    with col3:
        st.subheader("Over Voltage & Current")
        ov_tm = st.number_input("Tegangan Maks tm >", value=62.0)
        ov_tr = st.number_input("Tegangan Maks tr >", value=241.0)
        oc_tm = st.number_input("Arus Maks tm >", value=5.0)
        oc_tr = st.number_input("Arus Maks tr >", value=5.0)

st.markdown("---")
col4, col5 = st.columns(2)
with col4:
    indikator_min = st.number_input("Jumlah Indikator Minimal", value=1)
    bobot_min = st.number_input("Jumlah Bobot Minimal", value=2)
with col5:
    top_n = st.number_input("Jumlah Data Ditampilkan", value=50)

# -------------------------------
# Upload Data AMR
# -------------------------------
st.subheader("📥 Upload Data AMR (Excel)")
uploaded_amr = st.file_uploader("Unggah file Excel (.xlsx) berisi kolom IDPEL, v_drop, arus_hilang, over_voltage, over_current, active_p_lost", type=["xlsx"])

if uploaded_amr:
    df_amr = pd.read_excel(uploaded_amr)
    indikator_cols = ["v_drop", "arus_hilang", "over_voltage", "over_current", "active_p_lost"]
    for col in indikator_cols:
        if col not in df_amr.columns:
            st.error(f"Kolom '{col}' tidak ditemukan di data.")
            st.stop()

    df_amr["Jumlah Indikator"] = df_amr[indikator_cols].sum(axis=1)
    hasil = df_amr[df_amr["Jumlah Indikator"] >= indikator_min].head(int(top_n))

    # Integrasi dengan OLAP jika tersedia
    if not df_olap.empty:
        hasil = hasil.merge(df_olap, on="IDPEL", how="left")

    st.subheader("✅ Hasil Deteksi Target Operasi")
    st.dataframe(hasil, use_container_width=True)

    # Export ke Excel
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        hasil.to_excel(writer, index=False, sheet_name="TO_Results")
        writer.save()
    st.download_button("⬇️ Download Hasil (.xlsx)", data=output.getvalue(), file_name="hasil_TO_AMR.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
else:
    st.info("Silakan unggah file Excel untuk menampilkan hasil deteksi.")
