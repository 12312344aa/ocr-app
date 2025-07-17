import streamlit as st
import requests
import io
from fpdf import FPDF
import pandas as pd
import re

st.set_page_config(page_title="OCR + extraction tableau", layout="centered")
st.title("🔍 OCR et extraction tableau (Référence, Date, Montant)")

uploaded_file = st.file_uploader(
    "📤 Uploade ton PDF scanné ou image (JPG, PNG, PDF)",
    type=["pdf", "png", "jpg", "jpeg"]
)

if uploaded_file is not None:
    api_key = "helloworld"  # Remplace par ta clé API OCR.space si tu en as une

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
        st.text_area("Texte OCR brut", texte, height=300)

        # Parsing du texte pour extraire Référence, Date, Montant
        pattern = re.compile(r"(\d+)\s+(\d{2}/\d{2}/\d{2})\s+([-]?\d+[.,]?\d*)")
        data = []
        for match in pattern.finditer(texte):
            ref = match.group(1)
            date = match.group(2)
            montant = match.group(3).replace(',', '.')
            data.append([ref, date, montant])

        if data:
            df = pd.DataFrame(data, columns=["Référence", "Date", "Montant"])
            st.subheader("Tableau extrait")
            st.dataframe(df)

            if st.button("Générer PDF consultable à partir du tableau"):
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=12)
                # Titre
                pdf.cell(0, 10, "Tableau extrait OCR", ln=True, align='C')
                pdf.ln(10)

                # En-têtes colonnes
                col_widths = [60, 40, 40]
                headers = ["Référence", "Date", "Montant"]
                for i, header in enumerate(headers):
                    pdf.cell(col_widths[i], 10, header, border=1, align='C')
                pdf.ln()

                # Contenu tableau
                for idx, row in df.iterrows():
                    pdf.cell(col_widths[0], 10, str(row["Référence"]), border=1)
                    pdf.cell(col_widths[1], 10, row["Date"], border=1)
                    pdf.cell(col_widths[2], 10, row["Montant"], border=1, align='R')
                    pdf.ln()

                pdf_output = io.BytesIO()
                pdf_bytes = pdf.output(dest='S').encode('latin1')
                pdf_output.write(pdf_bytes)
                pdf_output.seek(0)

                st.download_button(
                    "📥 Télécharger le PDF consultable",
                    data=pdf_output,
                    file_name="tableau_ocr.pdf",
                    mime="application/pdf"
                )
        else:
            st.warning("Aucune donnée structurée n'a été détectée dans le texte OCR.")
