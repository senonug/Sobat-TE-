
import streamlit as st
import pandas as pd
import numpy as np
import io

# Login sederhana
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

st.set_page_config(page_title="Dashboard P2TL AMR", layout="wide")
st.markdown("<h1 style='text-align: center; color: navy;'>📊 Dashboard Target Operasi P2TL AMR - Juni 2025</h1>", unsafe_allow_html=True)

# Sidebar - Upload Referensi
st.sidebar.header("📂 Upload Referensi")
dil_file = st.sidebar.file_uploader("Upload Data DIL (Excel, dengan kolom IDPEL dan DAYA)", type=["xlsx"])

if dil_file:
    df_dil = pd.read_excel(dil_file)
    df_dil.columns = df_dil.columns.str.upper()
    df_dil = df_dil.rename(columns={"IDPEL": "LOCATION_CODE", "DAYA": "DAYA_DIL"})
else:
    df_dil = pd.DataFrame()

# Parameter Setting
with st.expander("⚙️ Setting Parameter Deteksi"):
    col1, col2, col3 = st.columns(3)
    with col1:
        vdrop_tm = st.number_input("Batas Tegangan Menengah (tm) <", value=56.0)
        vdrop_tr = st.number_input("Batas Tegangan Rendah (tr) <", value=180.0)
        idrop_tm = st.number_input("Batas Arus Besar tm >", value=0.5)
        idrop_tr = st.number_input("Batas Arus Besar tr >", value=0.5)

    with col2:
        ihilang_tm = st.number_input("Arus Hilang tm >", value=0.02)
        ihilang_tr = st.number_input("Arus Hilang tr >", value=0.02)
        imax = st.number_input("Arus Maksimum >", value=1.0)

    with col3:
        ov_tm = st.number_input("Tegangan Maks tm >", value=62.0)
        ov_tr = st.number_input("Tegangan Maks tr >", value=241.0)
        oc_tm = st.number_input("Arus Maks tm >", value=5.0)
        oc_tr = st.number_input("Arus Maks tr >", value=5.0)

col4, col5 = st.columns(2)
with col4:
    indikator_min = st.number_input("Jumlah Indikator Minimal", value=1)
    bobot_min = st.number_input("Jumlah Bobot Minimal", value=2)
with col5:
    top_n = st.number_input("Jumlah Data Ditampilkan", value=50)

st.markdown("---")
st.subheader("📥 Upload Data AMR (Excel)")
uploaded_amr = st.file_uploader("Upload data AMR (Excel)", type=["xlsx"])

if uploaded_amr:
    df_amr = pd.read_excel(uploaded_amr)
    df_amr.columns = df_amr.columns.str.upper()
    df_amr = df_amr[df_amr["LOCATION_TYPE"] == "Customer"]  # filter hanya customer
    df_amr["IDPEL"] = df_amr["LOCATION_CODE"]

    # Deteksi pelanggan 1 Phase
    daya_1p = [450, 900, 1300, 2200, 3500, 4400, 5500, 7700, 11000]
    df_amr["PHASE"] = np.where(df_amr["POWER"].isin(daya_1p), "1P", "3P")

    # Hitung indikator dummy (sementara)
    df_amr["v_drop"] = df_amr["VOLTAGE_L1"] < vdrop_tr
    df_amr["arus_hilang"] = df_amr["CURRENT_L1"] < ihilang_tr
    df_amr["over_voltage"] = df_amr["VOLTAGE_L1"] > ov_tr
    df_amr["over_current"] = df_amr["CURRENT_L1"] > oc_tr
    df_amr["active_p_lost"] = df_amr["ACTIVE_POWER_TOTAL"] == 0

    indikator_cols = ["v_drop", "arus_hilang", "over_voltage", "over_current", "active_p_lost"]
    df_amr["Jumlah Indikator"] = df_amr[indikator_cols].sum(axis=1)

    hasil = df_amr[df_amr["Jumlah Indikator"] >= indikator_min].head(int(top_n))

    # Integrasi DIL
    if not df_dil.empty:
        hasil = hasil.merge(df_dil[["LOCATION_CODE", "DAYA_DIL"]], on="LOCATION_CODE", how="left")
        hasil["VERIFIKASI_DAYA"] = np.where(hasil["POWER"] == hasil["DAYA_DIL"], "Sesuai", "Tidak Sesuai")

    st.subheader("✅ Hasil Deteksi Target Operasi")
    st.dataframe(hasil[["IDPEL", "PHASE", *indikator_cols, "Jumlah Indikator"] + (["DAYA_DIL", "VERIFIKASI_DAYA"] if not df_dil.empty else [])], use_container_width=True)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        hasil.to_excel(writer, index=False, sheet_name="TO_Results")
        writer.save()

    st.download_button("⬇️ Download Hasil (.xlsx)", data=output.getvalue(), file_name="hasil_TO_AMR.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
else:
    st.info("Silakan unggah file AMR untuk mulai analisis.")
