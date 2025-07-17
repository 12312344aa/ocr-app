import streamlit as st
import requests
import io
from fpdf import FPDF

st.set_page_config(page_title="OCR en ligne avec API OCR.space", layout="centered")
st.title("🔍 Convertisseur OCR en ligne (PDF ou image)")

uploaded_file = st.file_uploader("📤 Uploade ton PDF scanné ou image (JPG, PNG, PDF)", type=["pdf", "png", "jpg", "jpeg"])

if uploaded_file is not None:
    api_key = "helloworld"  # clé gratuite de test OCR.space, tu peux créer une clé gratuite sur https://ocr.space/ocrapi

    file_bytes = uploaded_file.read()

    with st.spinner("🕵️‍♂️ OCR en cours, patience..."):
        response = requests.post(
            "https://api.ocr.space/parse/image",
            files={uploaded_file.name: file_bytes},
            data={"apikey": api_key, "language": "fre", "isOverlayRequired": False}
        )

    result = response.json()

    if result.get("IsErroredOnProcessing"):
        st.error("❌ Erreur OCR : " + str(result.get("ErrorMessage", ["Erreur inconnue"])[0]))
    else:
        texte = result["ParsedResults"][0]["ParsedText"]
        st.success("✅ OCR terminé ! Voici le texte extrait :")
        st.text_area("Texte OCR", texte, height=300)

        if st.button("Générer PDF consultable"):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            for line in texte.split("\n"):
                pdf.cell(200, 10, txt=line, ln=True)

            pdf_output = io.BytesIO()
            pdf_bytes = pdf.output(dest='S').encode('latin1')
            pdf_output.write(pdf_bytes)
            pdf_output.seek(0)

            st.download_button(
                "📥 Télécharger le PDF consultable",
                data=pdf_output,
                file_name="ocr_result.pdf",
                mime="application/pdf"
            )
