import streamlit as st
from pdf2image import convert_from_bytes
from PIL import Image
import pytesseract
from fpdf import FPDF
import io

st.set_page_config(page_title="OCR en ligne", layout="centered")

st.title("🔍 Convertisseur OCR en ligne (PDF consultable)")

uploaded_file = st.file_uploader("📤 Uploade ton PDF scanné ou une image (JPG, PNG)", type=["pdf", "png", "jpg", "jpeg"])

if uploaded_file is not None:
    if uploaded_file.name.endswith(".pdf"):
        images = convert_from_bytes(uploaded_file.read())
    else:
        images = [Image.open(uploaded_file)]

    texte_total = ""
    for img in images:
        texte = pytesseract.image_to_string(img, lang='fra')
        texte_total += texte + "\n"

    # Création PDF avec texte
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for line in texte_total.split("\n"):
        pdf.cell(200, 10, txt=line, ln=True)

    # Sauvegarder en mémoire
    pdf_buffer = io.BytesIO()
    pdf.output(pdf_buffer)
    pdf_buffer.seek(0)

    st.success("✅ OCR terminé ! Télécharge ton PDF consultable ci-dessous.")
    st.download_button(label="📥 Télécharger le PDF", data=pdf_buffer, file_name="ocr_result.pdf", mime="application/pdf")
