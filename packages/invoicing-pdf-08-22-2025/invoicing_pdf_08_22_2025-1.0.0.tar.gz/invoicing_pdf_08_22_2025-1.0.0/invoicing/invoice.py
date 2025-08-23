import pandas as pd
import glob
from fpdf import FPDF
from pathlib import Path
import os


def generate(invoicesPath, pdfsPath, imagePath, pID, pName, aPurchased, PPU, tPrice):
    """_summary_

    Args:
        invoicesPath (_type_): _description_
        pdfsPath (_type_): _description_
        imagePath (_type_): _description_
        pID (_type_): _description_
        pName (_type_): _description_
        aPurchased (_type_): _description_
        PPU (_type_): _description_
        tPrice (_type_): _description_
    """
    filepaths = glob.glob(f"{invoicesPath}/*.xlsx")

    for filepath in filepaths:

        pdf = FPDF(orientation="P", unit="mm", format="A4")
        pdf.add_page()

        filename = Path(filepath).stem
        invoice_nr, date = filename.split("-")

        pdf.set_font(family="Times", size=16, style="B")
        pdf.cell(w=50, h=8, txt=f"Invoice nr.{invoice_nr}", ln=1)

        pdf.set_font(family="Times", size=16, style="B")
        pdf.cell(w=50, h=8, txt=f"Date: {date}", ln=1)

        df = pd.read_excel(filepath, sheet_name="Sheet 1")

        # Add a header
        columns = df.columns
        columns = [item.replace("_", " ").title() for item in columns]
        pdf.set_font(family="Times", size=10, style="B")
        pdf.set_text_color(80, 80, 80)
        pdf.cell(w=30, h=8, txt=columns[0], border=1)
        pdf.cell(w=70, h=8, txt=columns[1], border=1)
        pdf.cell(w=30, h=8, txt=columns[2], border=1)
        pdf.cell(w=30, h=8, txt=columns[3], border=1)
        pdf.cell(w=30, h=8, txt=columns[4], border=1, ln=1)

        # Add rows to the table
        for index, row in df.iterrows():
            pdf.set_font(family="Times", size=10)
            pdf.set_text_color(80, 80, 80)
            pdf.cell(w=30, h=8, txt=str(row[pID]), border=1)
            pdf.cell(w=70, h=8, txt=str(row[pName]), border=1)
            pdf.cell(w=30, h=8, txt=str(row[aPurchased]), border=1)
            pdf.cell(w=30, h=8, txt=str(row[PPU]), border=1)
            pdf.cell(w=30, h=8, txt=str(row[tPrice]), border=1, ln=1)

        total_sum = df[tPrice].sum()
        pdf.set_font(family="Times", size=10)
        pdf.set_text_color(80, 80, 80)
        pdf.cell(w=30, h=8, txt="", border=1)
        pdf.cell(w=70, h=8, txt="", border=1)
        pdf.cell(w=30, h=8, txt="", border=1)
        pdf.cell(w=30, h=8, txt="", border=1)
        pdf.cell(w=30, h=8, txt=str(total_sum), border=1, ln=1)

        # Add total sum sentence
        pdf.set_font(family="Times", size=10, style="B")
        pdf.cell(w=30, h=8, txt=f"The total price is {total_sum}", ln=1)

        # Add company name and logo
        pdf.set_font(family="Times", size=14, style="B")
        pdf.cell(w=25, h=8, txt=f"PythonHow")
        pdf.image(imagePath, w=10)

        if not os.path.exists(pdfsPath):
            os.makedirs(pdfsPath)
        pdf.output(f"{pdfsPath}/{filename}.pdf")
