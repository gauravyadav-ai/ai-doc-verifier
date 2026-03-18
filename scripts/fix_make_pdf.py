import re

with open("scripts/generate_training_data.py", "r") as f:
    content = f.read()

old = '''def make_pdf(content_lines, filename):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=11)
    pdf.set_margins(20, 20, 20)
    for line in content_lines:
        if line.startswith("##"):
            pdf.set_font("Helvetica", style="B", size=13)
            pdf.cell(0, 8, line[2:].strip(), ln=True)
            pdf.set_font("Helvetica", size=11)
        elif line.startswith("#"):
            pdf.set_font("Helvetica", style="B", size=16)
            pdf.cell(0, 10, line[1:].strip(), ln=True)
            pdf.set_font("Helvetica", size=11)
        elif line == "---":
            pdf.ln(3)
            pdf.line(20, pdf.get_y(), 190, pdf.get_y())
            pdf.ln(3)
        elif line == "":
            pdf.ln(4)
        else:
            pdf.multi_cell(0, 6, line)
    pdf.output(str(filename))'''

new = '''def make_pdf(content_lines, filename):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_margins(15, 15, 15)
    pdf.set_auto_page_break(auto=True, margin=15)
    for line in content_lines:
        if line.startswith("##"):
            pdf.set_font("Helvetica", style="B", size=12)
            pdf.cell(0, 8, line[2:].strip(), new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", size=10)
        elif line.startswith("#"):
            pdf.set_font("Helvetica", style="B", size=14)
            pdf.cell(0, 10, line[1:].strip(), new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", size=10)
        elif line == "---":
            pdf.ln(2)
            pdf.line(15, pdf.get_y(), 195, pdf.get_y())
            pdf.ln(2)
        elif line == "":
            pdf.ln(3)
        else:
            pdf.set_font("Helvetica", size=10)
            pdf.multi_cell(0, 5, line)
    pdf.output(str(filename))'''

content = content.replace(old, new)
with open("scripts/generate_training_data.py", "w") as f:
    f.write(content)
print("Fixed!")
