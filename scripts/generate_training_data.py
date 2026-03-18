import random
from pathlib import Path
from fpdf import FPDF

OUTPUT_DIR = Path("data/training")

NAMES = ["Rahul Sharma", "Priya Singh", "Amit Kumar", "Sunita Patel",
         "Vikram Mehta", "Anjali Gupta", "Rohan Verma", "Neha Joshi"]
COMPANIES = ["TechCorp India", "Global Solutions", "Innovate Systems",
             "DataWorks Inc", "CloudBase Tech", "NextGen Software"]
UNIVERSITIES = ["University of Delhi", "IIT Bombay", "Anna University",
                "Pune University", "Bangalore University"]
MONTHS = ["January","February","March","April","May","June",
          "July","August","September","October","November","December"]
CITIES = ["New Delhi","Mumbai","Bangalore","Chennai","Hyderabad","Pune"]
PINCODES = ["110001","400001","560001","600001","500001","411001"]

def rdate():
    return f"{random.randint(1,28)} {random.choice(MONTHS)} {random.randint(2020,2024)}"
def ramt():
    return f"Rs. {random.randint(1,99)*10000:,}"
def rphone():
    return f"+91 9{random.randint(100000000,999999999)}"
def remail(name):
    p = name.lower().split()
    return f"{p[0]}{p[-1]}@gmail.com"

def write_pdf(lines, path):
    pdf = FPDF()
    pdf.set_margins(20, 20, 20)
    pdf.set_auto_page_break(True, 20)
    pdf.add_page()
    for line in lines:
        if line == "---":
            pdf.set_font("Helvetica", size=10)
            pdf.ln(2)
        elif line.startswith("TITLE:"):
            pdf.set_font("Helvetica", "B", 15)
            pdf.cell(0, 10, line[6:], new_x="LMARGIN", new_y="NEXT")
        elif line.startswith("HEAD:"):
            pdf.set_font("Helvetica", "B", 12)
            pdf.cell(0, 8, line[5:], new_x="LMARGIN", new_y="NEXT")
        elif line == "":
            pdf.ln(3)
        else:
            pdf.set_font("Helvetica", size=10)
            safe = line.encode("latin-1", "replace").decode("latin-1")
            pdf.multi_cell(170, 5, safe)
    pdf.output(str(path))

def gen_invoice(i):
    name = random.choice(NAMES)
    amt = random.randint(5,50)*10000
    tax = int(amt*0.18)
    write_pdf([
        "TITLE:INVOICE",
        f"Invoice No: INV-{random.randint(1000,9999)}",
        f"Date: {rdate()}",
        f"Due Date: {rdate()}",
        "---",
        "HEAD:Bill To",
        name, random.choice(COMPANIES),
        f"Email: {remail(name)}",
        f"Phone: {rphone()}",
        "---",
        "HEAD:Items",
        f"Software Development Service - Rs.{amt:,}",
        f"Consulting Fee - Rs.{random.randint(1,5)*5000:,}",
        "---",
        f"Subtotal: Rs.{amt:,}",
        f"GST 18 percent: Rs.{tax:,}",
        f"Total Amount Due: Rs.{amt+tax:,}",
        f"Payment Terms: Net 30 days",
        f"Bank Account: {random.randint(10000000000,99999999999)}",
        f"IFSC: HDFC{random.randint(1000,9999)}",
    ], OUTPUT_DIR / "invoice" / f"invoice_{i:03d}.pdf")

def gen_resume(i):
    name = random.choice(NAMES)
    skills = random.sample(["Python","Java","JavaScript","React","SQL",
                            "Machine Learning","Docker","AWS","Django"], 5)
    write_pdf([
        f"TITLE:{name.upper()}",
        f"{random.choice(CITIES)} | {remail(name)} | {rphone()}",
        "---",
        "HEAD:OBJECTIVE",
        f"Seeking opportunities in {skills[0]} and {skills[1]}.",
        "",
        "HEAD:WORK EXPERIENCE",
        f"{random.choice(COMPANIES)} | {rdate()} - Present",
        "Software Engineer",
        f"Developed applications using {skills[0]} and {skills[2]}",
        f"Improved performance by 40 percent through optimization",
        "",
        f"{random.choice(COMPANIES)} | {rdate()} - {rdate()}",
        "Junior Developer",
        f"Built REST APIs using {skills[1]}",
        "",
        "HEAD:EDUCATION",
        f"{random.choice(UNIVERSITIES)}",
        f"B.Tech Computer Science | CGPA: {random.uniform(7,9.5):.2f}",
        "",
        "HEAD:SKILLS",
        ", ".join(skills),
        "",
        "HEAD:CERTIFICATIONS",
        f"AWS Certified Developer | {rdate()}",
    ], OUTPUT_DIR / "resume" / f"resume_{i:03d}.pdf")

def gen_internship(i):
    write_pdf([
        "TITLE:INTERNSHIP OPPORTUNITY",
        f"HEAD:{random.choice(UNIVERSITIES)}",
        f"Department of {random.choice(['Computer Science','Data Science','IT'])}",
        "---",
        f"{random.choice(COMPANIES)} offers internship for students.",
        f"Duration: {random.randint(2,6)} months starting {rdate()}",
        "",
        "HEAD:Eligibility",
        "B.Tech or M.Tech students",
        f"Minimum CGPA: {random.uniform(6.5,8.0):.1f}",
        "",
        "HEAD:Stipend",
        f"Monthly: {ramt()}",
        "",
        "HEAD:How to Apply",
        f"Email: internship@company.ac.in",
        f"Apply at: https://careers.company.com/intern",
        f"Last Date: {rdate()}",
        f"Contact: placement@university.ac.in",
        f"Phone: {rphone()}",
        f"Address: {random.choice(CITIES)} - {random.choice(PINCODES)}",
    ], OUTPUT_DIR / "internship_notice" / f"internship_{i:03d}.pdf")

def gen_academic(i):
    name = random.choice(NAMES)
    subjects = random.sample(["Mathematics","Physics","Computer Science",
                               "Data Structures","Algorithms","Networks"], 5)
    marks = [(s, random.randint(55,98)) for s in subjects]
    total = sum(m for _,m in marks)
    lines = [
        "TITLE:EXAMINATION RESULT",
        f"HEAD:{random.choice(UNIVERSITIES)}",
        f"Academic Year: {random.randint(2020,2024)}",
        "---",
        f"Student Name: {name}",
        f"Roll Number: {random.randint(10000,99999)}",
        f"Course: B.Tech Computer Science",
        f"Semester: {random.randint(1,8)}",
        f"Date: {rdate()}",
        "---",
        "HEAD:Marks",
    ]
    for s,m in marks:
        lines.append(f"{s}: {m} / 100")
    lines += [
        "---",
        f"Total: {total} / {len(marks)*100}",
        f"Percentage: {total/(len(marks)*100)*100:.1f} percent",
        f"Result: PASS",
        f"Controller of Examinations | {rdate()}",
    ]
    write_pdf(lines, OUTPUT_DIR / "academic" / f"academic_{i:03d}.pdf")

def gen_medical(i):
    patient = random.choice(NAMES)
    doctor = random.choice(NAMES)
    meds = [f"Tab. {m} {d}" for m,d in zip(
        random.sample(["Paracetamol","Amoxicillin","Metformin","Omeprazole"],3),
        ["500mg","250mg","10mg"])]
    write_pdf([
        "TITLE:MEDICAL PRESCRIPTION",
        f"HEAD:Dr. {doctor}",
        f"MBBS MD - {random.choice(['General Medicine','Cardiology'])}",
        f"Reg No: MCI-{random.randint(10000,99999)}",
        "---",
        f"Patient: {patient}",
        f"Age: {random.randint(18,75)} years",
        f"Date: {rdate()}",
        f"Diagnosis: {random.choice(['Viral Fever','Hypertension','Diabetes'])}",
        "---",
        "HEAD:Prescription Rx",
        meds[0] + " - twice daily for 5 days",
        meds[1] + " - once daily for 7 days",
        meds[2] + " - thrice daily for 3 days",
        "---",
        "Take medicines after meals",
        f"Follow-up: {rdate()}",
        f"Hospital: {random.choice(CITIES)} Medical Center",
        f"Contact: {rphone()}",
    ], OUTPUT_DIR / "medical" / f"medical_{i:03d}.pdf")

def gen_bank(i):
    name = random.choice(NAMES)
    txns = []
    bal = random.randint(10000,200000)
    for _ in range(random.randint(6,12)):
        t = random.choice(["CR","DR"])
        amt = random.randint(500,30000)
        bal = bal+amt if t=="CR" else max(0,bal-amt)
        txns.append(f"{rdate()} | {random.choice(['UPI','NEFT','ATM','Salary'])} | {t} | Rs.{amt:,} | Rs.{bal:,}")
    lines = [
        "TITLE:BANK STATEMENT",
        f"HEAD:{random.choice(COMPANIES)} Bank",
        "---",
        f"Account Holder: {name}",
        f"Account: XXXX{random.randint(1000,9999)}",
        f"Type: Savings Account",
        f"IFSC: HDFC{random.randint(1000,9999)}",
        f"Period: {rdate()} to {rdate()}",
        "---",
        "HEAD:Transactions",
    ] + txns + [
        "---",
        f"Closing Balance: Rs.{bal:,}",
    ]
    write_pdf(lines, OUTPUT_DIR / "bank_statement" / f"bank_{i:03d}.pdf")

def gen_legal(i):
    p1, p2 = random.sample(COMPANIES, 2)
    write_pdf([
        "TITLE:SERVICE AGREEMENT",
        f"Date: {rdate()}",
        "---",
        "HEAD:PARTIES",
        f"This Agreement is between {p1} and {p2}.",
        "",
        "HEAD:WHEREAS",
        "The parties agree to the following terms and conditions.",
        "",
        "HEAD:1. SCOPE OF SERVICES",
        "Software development and maintenance",
        "Technical consultation and support",
        "",
        "HEAD:2. PAYMENT TERMS",
        f"Total Value: {ramt()}",
        "Payment: Monthly installments",
        "Late Penalty: 2 percent per month",
        "",
        "HEAD:3. TERMINATION",
        f"Duration: {random.randint(6,24)} months",
        f"Notice: {random.randint(15,60)} days written notice required",
        "",
        "HEAD:4. CONFIDENTIALITY",
        "Both parties agree to maintain strict confidentiality.",
        "",
        "HEAD:5. GOVERNING LAW",
        f"Governed by laws of India. Disputes in {random.choice(CITIES)}.",
        "",
        "HEAD:6. INDEMNIFICATION",
        "Each party shall indemnify the other from claims.",
        "",
        "HEAD:SIGNATURES",
        f"For {p1}: _________ Date: {rdate()}",
        f"For {p2}: _________ Date: {rdate()}",
        "Witness: _________ Notary: _________",
    ], OUTPUT_DIR / "legal" / f"legal_{i:03d}.pdf")

def gen_id_card(i):
    name = random.choice(NAMES)
    write_pdf([
        "TITLE:IDENTITY CARD",
        f"HEAD:{random.choice(UNIVERSITIES + COMPANIES)}",
        "---",
        f"Name: {name}",
        f"ID Number: {random.randint(100000,999999)}",
        f"Date of Birth: {rdate()}",
        f"Gender: {random.choice(['Male','Female'])}",
        f"Blood Group: {random.choice(['A+','B+','O+','AB+'])}",
        f"Address: {random.choice(CITIES)} - {random.choice(PINCODES)}",
        f"Phone: {rphone()}",
        f"Email: {remail(name)}",
        "---",
        f"Issue Date: {rdate()}",
        f"Valid Until: {rdate()}",
        "Nationality: Indian",
        "This is a computer generated identity document.",
    ], OUTPUT_DIR / "id_card" / f"id_card_{i:03d}.pdf")

GENERATORS = {
    "invoice": gen_invoice,
    "resume": gen_resume,
    "internship_notice": gen_internship,
    "academic": gen_academic,
    "medical": gen_medical,
    "bank_statement": gen_bank,
    "legal": gen_legal,
    "id_card": gen_id_card,
}

if __name__ == "__main__":
    count = 25
    print(f"Generating {count} PDFs per class ({count*len(GENERATORS)} total)...\n")
    for name, fn in GENERATORS.items():
        print(f"  {name}...")
        for i in range(1, count+1):
            fn(i)
        print(f"  Done - {count} PDFs")
    print(f"\nAll done! Run: docker compose exec api python scripts/train_with_real_data.py")
