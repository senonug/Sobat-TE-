
import streamlit as st
import pandas as pd
import numpy as np
import io

st.set_page_config(page_title="Dashboard P2TL AMR", layout="wide")

st.title("Dashboard Target Operasi P2TL AMR Periode June 2025")

with st.expander("Setting Parameter"):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader("Tegangan Drop")
        vdrop_tm = st.number_input("Set Batas Atas Tegangan Menengah (tm)", value=56.0)
        vdrop_tr = st.number_input("Set Batas Atas Tegangan Rendah (tr)", value=180.0)
        idrop_tm = st.number_input("Set Batas Bawah Arus Besar tm", value=0.5)
        idrop_tr = st.number_input("Set Batas Bawah Arus Besar tr", value=0.5)

    with col2:
        st.subheader("Arus Hilang")
        ihilang_tm = st.number_input("Set Batas Atas Arus Hilang tm", value=0.02)
        ihilang_tr = st.number_input("Set Batas Atas Arus Hilang tr", value=0.02)
        imax = st.number_input("Set Batas Bawah Arus Maksimum", value=1.0)

    with col3:
        st.subheader("Over Current & Over Voltage")
        oc_tm = st.number_input("Set Batas bawah Arus Maks tm", value=5.0)
        oc_tr = st.number_input("Set Batas bawah Arus Maks tr", value=5.0)
        ov_tm = st.number_input("Set Tegangan Maksimum (tm)", value=62.0)
        ov_tr = st.number_input("Set Tegangan Maksimum (tr)", value=241.0)

st.markdown("---")
st.subheader("Kriteria TO")
col4, col5 = st.columns(2)
with col4:
    indikator_min = st.number_input("Jumlah Indikator Minimal", value=1)
    bobot_min = st.number_input("Jumlah Bobot Minimal", value=2)
with col5:
    top_n = st.number_input("Banyak Data Ditampilkan", value=50)

st.markdown("---")
st.subheader("📂 Upload Data AMR (CSV)")
uploaded_file = st.file_uploader("Unggah file data AMR (.csv) dengan kolom IDPEL, v_drop, arus_hilang, over_voltage, over_current, active_p_lost", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    indikator_cols = ["v_drop", "arus_hilang", "over_voltage", "over_current", "active_p_lost"]
    for col in indikator_cols:
        if col not in df.columns:
            st.error(f"Kolom '{col}' tidak ditemukan di data.")
            st.stop()
    df["Jumlah Indikator"] = df[indikator_cols].sum(axis=1)
    hasil = df[df["Jumlah Indikator"] >= indikator_min].head(int(top_n))

    st.subheader("🔍 Hasil Deteksi Target Operasi")
    st.dataframe(hasil, use_container_width=True)

    # Export hasil ke Excel
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        hasil.to_excel(writer, index=False, sheet_name='TO_Results')
        writer.save()
    st.download_button("📥 Download Hasil (Excel)", data=output.getvalue(), file_name="hasil_TO_AMR.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
else:
    st.info("Silakan unggah file CSV untuk menampilkan hasil deteksi.")
