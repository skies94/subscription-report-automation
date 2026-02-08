import subprocess
import streamlit as st
import tempfile
import os

st.set_page_config(page_title="구독 연장 리포트 자동화", layout="centered")

st.title("📊 구독 연장 리포트 자동 생성기")
st.caption("데일리 리포트 기반 · 근거 강제 · 시니어 기준 자동 요약")

chat_file = st.file_uploader("카카오톡 데일리 리포트(txt)", type=["txt"])
data_file = st.file_uploader("매체 데이터(csv/xlsx)", type=["csv", "xlsx"])

brand = st.text_input("브랜드명")
sku = st.text_input("SKU")
channels = st.multiselect("채널", ["META", "GFA", "KAKAO", "GOOGLE"])
period = st.text_input("운영 기간 (예: 2025.01.01~01.31)")

if st.button("🚀 리포트 생성"):
    if not all([chat_file, data_file, brand, sku, channels, period]):
        st.error("모든 항목을 입력해주세요.")
        st.stop()

    with tempfile.TemporaryDirectory() as tmp:
        chat_path = os.path.join(tmp, "chat.txt")
        data_path = os.path.join(tmp, "data.csv")

        with open(chat_path, "wb") as f:
            f.write(chat_file.read())
        with open(data_path, "wb") as f:
            f.write(data_file.read())

        out_dir = os.path.join(tmp, "output")

        cmd = [
            "python3", "-m", "src.main",
            "--chat", chat_path,
            "--data", data_path,
            "--brand", brand,
            "--sku", sku,
            "--period", period,
            "--channels", *channels,
            "--out", out_dir,
            "--evidence_mode", "OFF"
        ]

        subprocess.run(cmd)

        report_path = os.path.join(out_dir, "report.txt")

        if os.path.exists(report_path):
            with open(report_path, "r") as f:
                st.text_area("📄 생성된 리포트", f.read(), height=400)
        else:
            st.error("리포트 생성 실패")
