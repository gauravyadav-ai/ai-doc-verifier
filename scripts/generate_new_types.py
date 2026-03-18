import random
from pathlib import Path
from fpdf import FPDF

OUTPUT_DIR = Path("data/training")

NAMES = ["Rahul Sharma", "Priya Singh", "Amit Kumar", "Sunita Patel",
         "Vikram Mehta", "Anjali Gupta", "Rohan Verma", "Neha Joshi",
         "Arjun Nair", "Kavya Reddy", "Sanjay Patel", "Meera Iyer"]
COMPANIES = ["TechCorp India", "Global Solutions", "Innovate Systems",
             "DataWorks Inc", "CloudBase Tech", "NextGen Software",
             "Alpha Ventures", "Bright Future Ltd"]
UNIVERSITIES = ["University of Delhi", "IIT Bombay", "Anna University",
                "Pune University", "Bangalore University", "BITS Pilani"]
MONTHS = ["January","February","March","April","May","June",
          "July","August","September","October","November","December"]
CITIES = ["New Delhi","Mumbai","Bangalore","Chennai","Hyderabad","Pune","Kolkata"]
PINCODES = ["110001","400001","560001","600001","500001","411001","700001"]
STATES = ["Delhi","Maharashtra","Karnataka","Tamil Nadu","Telangana","West Bengal"]

def rdate():
    return f"{random.randint(1,28)} {random.choice(MONTHS)} {random.randint(2018,2024)}"
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

def gen_passport(i):
    name = random.choice(NAMES)
    write_pdf([
        "TITLE:PASSPORT",
        "Republic of India",
        "---",
        f"Surname: {name.split()[-1].upper()}",
        f"Given Names: {name.split()[0].upper()}",
        f"Nationality: Indian",
        f"Date of Birth: {rdate()}",
        f"Place of Birth: {random.choice(CITIES)}",
        f"Gender: {random.choice(['Male','Female'])}",
        f"Passport Number: {random.choice(['A','B','C','P','R'])}{random.randint(1000000,9999999)}",
        f"Date of Issue: {rdate()}",
        f"Date of Expiry: {rdate()}",
        f"Place of Issue: {random.choice(CITIES)}",
        "---",
        "Issuing Authority: Government of India",
        "Ministry of External Affairs",
        "This passport is valid for all countries.",
    ], OUTPUT_DIR / "passport" / f"passport_{i:03d}.pdf")

def gen_visa(i):
    name = random.choice(NAMES)
    countries = ["United States","United Kingdom","Germany","Australia","Canada","Japan"]
    write_pdf([
        "TITLE:VISA",
        f"Embassy of {random.choice(countries)}",
        "---",
        f"Applicant Name: {name}",
        f"Passport Number: P{random.randint(1000000,9999999)}",
        f"Nationality: Indian",
        f"Date of Birth: {rdate()}",
        f"Visa Type: {random.choice(['Tourist','Student','Work','Business'])}",
        f"Visa Number: {random.randint(10000000,99999999)}",
        f"Valid From: {rdate()}",
        f"Valid Until: {rdate()}",
        f"Number of Entries: {random.choice(['Single','Double','Multiple'])}",
        f"Duration of Stay: {random.randint(30,180)} days",
        "---",
        "Issued by: Consular Officer",
        "This visa does not guarantee entry.",
    ], OUTPUT_DIR / "visa" / f"visa_{i:03d}.pdf")

def gen_driving_licence(i):
    name = random.choice(NAMES)
    write_pdf([
        "TITLE:DRIVING LICENCE",
        "Government of India",
        f"Transport Department - {random.choice(STATES)}",
        "---",
        f"Name: {name}",
        f"Date of Birth: {rdate()}",
        f"Blood Group: {random.choice(['A+','B+','O+','AB+','A-'])}",
        f"Address: {random.choice(CITIES)} - {random.choice(PINCODES)}",
        f"Licence Number: {random.choice(STATES[:2])}{random.randint(10,99)}{random.randint(10000000000,99999999999)}",
        f"Date of Issue: {rdate()}",
        f"Valid Until: {rdate()}",
        f"Vehicle Class: {random.choice(['LMV','MCWG','LMV-TR'])}",
        "---",
        "Issued by: Regional Transport Office",
        "This licence is valid across India.",
    ], OUTPUT_DIR / "driving_licence" / f"driving_{i:03d}.pdf")

def gen_birth_certificate(i):
    name = random.choice(NAMES)
    write_pdf([
        "TITLE:BIRTH CERTIFICATE",
        "Government of India",
        f"Municipal Corporation - {random.choice(CITIES)}",
        "---",
        "HEAD:Certificate of Birth",
        f"This is to certify that {name}",
        f"was born on {rdate()}",
        f"at {random.choice(CITIES)}, {random.choice(STATES)}",
        "",
        f"Father's Name: {random.choice(NAMES)}",
        f"Mother's Name: {random.choice(NAMES)}",
        f"Place of Birth: {random.choice(['Government Hospital','Private Hospital','Home'])}",
        f"Registration Number: {random.randint(100000,999999)}",
        f"Registration Date: {rdate()}",
        "---",
        "Issued by: Registrar of Births and Deaths",
        "This is an official government document.",
    ], OUTPUT_DIR / "birth_certificate" / f"birth_{i:03d}.pdf")

def gen_offer_letter(i):
    name = random.choice(NAMES)
    company = random.choice(COMPANIES)
    role = random.choice(["Software Engineer","Data Analyst","Product Manager",
                          "Business Analyst","DevOps Engineer","ML Engineer"])
    write_pdf([
        "TITLE:OFFER LETTER",
        f"HEAD:{company}",
        f"Date: {rdate()}",
        "---",
        f"Dear {name},",
        "",
        f"We are pleased to offer you the position of {role}",
        f"at {company}.",
        "",
        "HEAD:Terms of Employment",
        f"Position: {role}",
        f"Department: {random.choice(['Engineering','Product','Analytics','Operations'])}",
        f"Date of Joining: {rdate()}",
        f"Work Location: {random.choice(CITIES)}",
        "",
        "HEAD:Compensation",
        f"Annual CTC: {ramt()}",
        f"Basic Salary: {ramt()} per month",
        f"HRA: Rs. {random.randint(5,20)*1000:,} per month",
        "",
        "HEAD:Terms",
        f"Probation Period: {random.randint(3,6)} months",
        f"Notice Period: {random.randint(30,90)} days",
        "",
        "Please sign and return this letter by the given date.",
        "",
        f"Authorized Signatory: HR Manager, {company}",
        f"Contact: hr@company.com | {rphone()}",
    ], OUTPUT_DIR / "offer_letter" / f"offer_{i:03d}.pdf")

def gen_experience_letter(i):
    name = random.choice(NAMES)
    company = random.choice(COMPANIES)
    role = random.choice(["Software Engineer","Senior Developer","Team Lead","Manager"])
    write_pdf([
        "TITLE:EXPERIENCE LETTER",
        f"HEAD:{company}",
        f"Date: {rdate()}",
        "---",
        f"To Whom It May Concern,",
        "",
        f"This is to certify that {name} was employed with",
        f"{company} as {role}",
        f"from {rdate()} to {rdate()}.",
        "",
        f"During the tenure, {name.split()[0]} demonstrated excellent",
        "technical skills and professional conduct.",
        "",
        f"We wish {name.split()[0]} all the best in future endeavors.",
        "",
        f"Issued by: HR Department, {company}",
        f"Email: hr@company.com",
        f"Phone: {rphone()}",
    ], OUTPUT_DIR / "experience_letter" / f"experience_{i:03d}.pdf")

def gen_salary_slip(i):
    name = random.choice(NAMES)
    company = random.choice(COMPANIES)
    basic = random.randint(20,80)*1000
    hra = int(basic*0.4)
    ta = random.randint(1,3)*1000
    pf = int(basic*0.12)
    gross = basic+hra+ta
    net = gross-pf
    write_pdf([
        "TITLE:SALARY SLIP",
        f"HEAD:{company}",
        f"Month: {random.choice(MONTHS)} {random.randint(2022,2024)}",
        "---",
        f"Employee Name: {name}",
        f"Employee ID: EMP{random.randint(1000,9999)}",
        f"Designation: {random.choice(['Engineer','Analyst','Manager','Lead'])}",
        f"Department: {random.choice(['Engineering','HR','Finance','Operations'])}",
        f"Bank Account: XXXX{random.randint(1000,9999)}",
        "---",
        "HEAD:Earnings",
        f"Basic Salary: Rs. {basic:,}",
        f"House Rent Allowance: Rs. {hra:,}",
        f"Transport Allowance: Rs. {ta:,}",
        f"Gross Salary: Rs. {gross:,}",
        "---",
        "HEAD:Deductions",
        f"Provident Fund: Rs. {pf:,}",
        f"Professional Tax: Rs. 200",
        "---",
        f"Net Salary: Rs. {net-200:,}",
        f"Amount in Words: Rupees {net-200:,} only",
    ], OUTPUT_DIR / "salary_slip" / f"salary_{i:03d}.pdf")

def gen_appointment_letter(i):
    name = random.choice(NAMES)
    company = random.choice(COMPANIES)
    write_pdf([
        "TITLE:APPOINTMENT LETTER",
        f"HEAD:{company}",
        f"Date: {rdate()}",
        "---",
        f"Dear {name},",
        "",
        f"We are pleased to appoint you as",
        f"{random.choice(['Senior Engineer','Team Lead','Manager','Director'])}",
        f"effective from {rdate()}.",
        "",
        "HEAD:Terms of Appointment",
        f"This appointment is subject to satisfactory performance.",
        f"You will report to the {random.choice(['CTO','VP Engineering','Director'])}.",
        "",
        "HEAD:Remuneration",
        f"Total Annual CTC: {ramt()}",
        f"Performance Bonus: Up to {random.randint(10,30)}% of annual CTC",
        "",
        "HEAD:Other Benefits",
        "- Health insurance coverage",
        "- Paid annual leave",
        "- Professional development allowance",
        "",
        f"Signed: CEO, {company}",
    ], OUTPUT_DIR / "appointment_letter" / f"appointment_{i:03d}.pdf")

def gen_tax_return(i):
    name = random.choice(NAMES)
    income = random.randint(5,50)*100000
    tax = int(income*0.2)
    write_pdf([
        "TITLE:INCOME TAX RETURN",
        "Government of India - Income Tax Department",
        f"Assessment Year: {random.randint(2020,2024)}-{random.randint(2021,2025)}",
        "---",
        f"Taxpayer Name: {name}",
        f"PAN: {random.choice('ABCDE')}{random.randint(1000,9999)}{random.choice('ABCDE')}",
        f"Aadhaar: {random.randint(100000000000,999999999999)}",
        f"Address: {random.choice(CITIES)} - {random.choice(PINCODES)}",
        "---",
        "HEAD:Income Details",
        f"Salary Income: Rs. {income:,}",
        f"Other Income: Rs. {random.randint(0,50000):,}",
        f"Gross Total Income: Rs. {income:,}",
        "",
        "HEAD:Tax Computation",
        f"Total Tax Payable: Rs. {tax:,}",
        f"TDS Deducted: Rs. {int(tax*0.9):,}",
        f"Tax Payable/Refund: Rs. {int(tax*0.1):,}",
        "---",
        "Filed on: e-Filing portal incometax.gov.in",
        f"Acknowledgement No: {random.randint(100000000000,999999999999)}",
    ], OUTPUT_DIR / "tax_return" / f"tax_{i:03d}.pdf")

def gen_pan_card(i):
    name = random.choice(NAMES)
    write_pdf([
        "TITLE:PERMANENT ACCOUNT NUMBER CARD",
        "Income Tax Department - Government of India",
        "---",
        f"Name: {name.upper()}",
        f"Father's Name: {random.choice(NAMES).upper()}",
        f"Date of Birth: {rdate()}",
        f"PAN: {random.choice('ABCDE')}{random.choice('ABCDE')}{random.choice('ABCDE')}{random.randint(1000,9999)}{random.choice('ABCDE')}",
        "---",
        "Issued by: Income Tax Department",
        "Government of India",
        "This card is valid for lifetime.",
        "PAN is mandatory for financial transactions.",
    ], OUTPUT_DIR / "pan_card" / f"pan_{i:03d}.pdf")

def gen_aadhar_card(i):
    name = random.choice(NAMES)
    write_pdf([
        "TITLE:AADHAAR CARD",
        "Unique Identification Authority of India",
        "Government of India",
        "---",
        f"Name: {name}",
        f"Date of Birth: {rdate()}",
        f"Gender: {random.choice(['Male','Female'])}",
        f"Address: {random.choice(CITIES)}, {random.choice(STATES)} - {random.choice(PINCODES)}",
        f"Aadhaar Number: {random.randint(1000,9999)} {random.randint(1000,9999)} {random.randint(1000,9999)}",
        "---",
        "Issued by: UIDAI",
        "This is a valid proof of identity and address.",
        "For verification: uidai.gov.in",
    ], OUTPUT_DIR / "aadhar_card" / f"aadhar_{i:03d}.pdf")

def gen_loan_agreement(i):
    name = random.choice(NAMES)
    bank = random.choice(COMPANIES) + " Bank"
    amount = random.randint(1,50)*100000
    write_pdf([
        "TITLE:LOAN AGREEMENT",
        f"HEAD:{bank}",
        f"Date: {rdate()}",
        "---",
        f"Borrower: {name}",
        f"Address: {random.choice(CITIES)} - {random.choice(PINCODES)}",
        f"PAN: {random.choice('ABCDE')}{random.randint(1000,9999)}{random.choice('ABCDE')}",
        "---",
        "HEAD:Loan Details",
        f"Loan Type: {random.choice(['Home Loan','Personal Loan','Car Loan','Education Loan'])}",
        f"Loan Amount: Rs. {amount:,}",
        f"Interest Rate: {random.uniform(7,18):.2f}% per annum",
        f"Tenure: {random.randint(12,240)} months",
        f"EMI: Rs. {int(amount/random.randint(12,60)):,}",
        f"Loan Account Number: {random.randint(10000000000,99999999999)}",
        "---",
        "HEAD:Terms",
        "The borrower agrees to repay the loan as per schedule.",
        "Default will attract penal interest and legal action.",
        "",
        f"Borrower Signature: _________",
        f"Bank Authorized Officer: _________",
    ], OUTPUT_DIR / "loan_agreement" / f"loan_{i:03d}.pdf")

def gen_insurance_policy(i):
    name = random.choice(NAMES)
    write_pdf([
        "TITLE:INSURANCE POLICY",
        f"HEAD:{random.choice(COMPANIES)} Insurance",
        f"Policy Number: POL{random.randint(100000,999999)}",
        "---",
        f"Policyholder: {name}",
        f"Date of Birth: {rdate()}",
        f"Address: {random.choice(CITIES)} - {random.choice(PINCODES)}",
        "---",
        "HEAD:Policy Details",
        f"Policy Type: {random.choice(['Life Insurance','Health Insurance','Vehicle Insurance','Term Plan'])}",
        f"Sum Assured: Rs. {random.randint(5,100)*100000:,}",
        f"Premium: Rs. {random.randint(5,50)*1000:,} per annum",
        f"Policy Start Date: {rdate()}",
        f"Policy End Date: {rdate()}",
        f"Nominee: {random.choice(NAMES)}",
        "---",
        "Claims: claims@insurance.com",
        f"Helpline: {rphone()}",
    ], OUTPUT_DIR / "insurance_policy" / f"insurance_{i:03d}.pdf")

def gen_certificate(i):
    name = random.choice(NAMES)
    cert_types = ["Completion","Participation","Achievement","Excellence","Merit"]
    write_pdf([
        f"TITLE:CERTIFICATE OF {random.choice(cert_types).upper()}",
        f"HEAD:{random.choice(UNIVERSITIES + COMPANIES)}",
        "---",
        "This is to certify that",
        "",
        f"{name}",
        "",
        f"has successfully completed the course in",
        f"{random.choice(['Python Programming','Data Science','Web Development','AI/ML','Cloud Computing'])}",
        "",
        f"Duration: {random.randint(1,12)} months",
        f"Grade: {random.choice(['A','A+','B+','Distinction','Pass with Merit'])}",
        f"Date of Completion: {rdate()}",
        "---",
        "Director / Principal",
        f"Date: {rdate()}",
    ], OUTPUT_DIR / "certificate" / f"certificate_{i:03d}.pdf")

def gen_marksheet(i):
    name = random.choice(NAMES)
    board = random.choice(["CBSE","ICSE","State Board","NIOS"])
    subjects = random.sample(["English","Mathematics","Science","Social Science",
                               "Hindi","Physics","Chemistry","Biology","Computer Science"], 5)
    marks = [(s, random.randint(55,99)) for s in subjects]
    total = sum(m for _,m in marks)
    lines = [
        f"TITLE:{board} MARKSHEET",
        f"HEAD:{random.choice(UNIVERSITIES)}",
        f"Class: {random.choice(['10','12','Semester 1','Semester 2'])}",
        "---",
        f"Student Name: {name}",
        f"Roll Number: {random.randint(1000000,9999999)}",
        f"Date of Birth: {rdate()}",
        f"Examination Year: {random.randint(2018,2024)}",
        "---",
        "HEAD:Subject-wise Marks",
    ]
    for s,m in marks:
        lines.append(f"{s}: {m}/100")
    lines += [
        "---",
        f"Total: {total}/{len(marks)*100}",
        f"Percentage: {total/(len(marks)*100)*100:.1f}%",
        f"Division: {'First' if total>len(marks)*60 else 'Second'}",
        f"Result: PASS",
    ]
    write_pdf(lines, OUTPUT_DIR / "marksheet" / f"marksheet_{i:03d}.pdf")

def gen_admission_letter(i):
    name = random.choice(NAMES)
    uni = random.choice(UNIVERSITIES)
    write_pdf([
        "TITLE:ADMISSION LETTER",
        f"HEAD:{uni}",
        f"Date: {rdate()}",
        "---",
        f"Dear {name},",
        "",
        f"We are pleased to offer you admission to",
        f"{random.choice(['B.Tech','M.Tech','MBA','MCA','PhD'])} in",
        f"{random.choice(['Computer Science','Data Science','Electronics','Management'])}",
        f"for the academic year {random.randint(2022,2024)}-{random.randint(2023,2025)}.",
        "",
        "HEAD:Admission Details",
        f"Student ID: {random.randint(100000,999999)}",
        f"Course Duration: {random.randint(2,4)} years",
        f"Reporting Date: {rdate()}",
        "",
        "HEAD:Fee Details",
        f"Tuition Fee: {ramt()} per semester",
        f"Hostel Fee: {ramt()} per year",
        "",
        "Please complete admission formalities by the given date.",
        f"Admissions Office: {uni}",
    ], OUTPUT_DIR / "admission_letter" / f"admission_{i:03d}.pdf")

def gen_scholarship_letter(i):
    name = random.choice(NAMES)
    write_pdf([
        "TITLE:SCHOLARSHIP AWARD LETTER",
        f"HEAD:{random.choice(UNIVERSITIES)}",
        f"Date: {rdate()}",
        "---",
        f"Dear {name},",
        "",
        "We are pleased to inform you that you have been",
        f"selected for the {random.choice(['Merit','Need-based','Sports','National'])} Scholarship.",
        "",
        "HEAD:Scholarship Details",
        f"Scholarship Amount: {ramt()} per year",
        f"Duration: {random.randint(1,4)} years",
        f"Award Date: {rdate()}",
        f"Scholarship ID: SCH{random.randint(10000,99999)}",
        "",
        "HEAD:Conditions",
        f"Minimum CGPA: {random.uniform(7,9):.1f}",
        "Regular attendance required",
        "No active backlogs",
        "",
        "Congratulations on this achievement.",
        "Scholarship Committee",
    ], OUTPUT_DIR / "scholarship_letter" / f"scholarship_{i:03d}.pdf")

def gen_rent_agreement(i):
    tenant = random.choice(NAMES)
    landlord = random.choice(NAMES)
    rent = random.randint(5,50)*1000
    write_pdf([
        "TITLE:RENTAL AGREEMENT",
        f"Date: {rdate()}",
        "---",
        "HEAD:Parties",
        f"Landlord: {landlord}",
        f"Tenant: {tenant}",
        f"Property Address: {random.choice(CITIES)} - {random.choice(PINCODES)}",
        "---",
        "HEAD:Rent Details",
        f"Monthly Rent: Rs. {rent:,}",
        f"Security Deposit: Rs. {rent*2:,}",
        f"Lease Start: {rdate()}",
        f"Lease End: {rdate()}",
        f"Lock-in Period: {random.randint(6,12)} months",
        "",
        "HEAD:Terms",
        "Rent payable by 5th of every month.",
        "Tenant shall not sublet the premises.",
        f"Notice Period: {random.randint(1,3)} months",
        "",
        "HEAD:Signatures",
        f"Landlord: _________ Date: {rdate()}",
        f"Tenant: _________ Date: {rdate()}",
        "Witness: _________",
    ], OUTPUT_DIR / "rent_agreement" / f"rent_{i:03d}.pdf")

def gen_utility_bill(i):
    name = random.choice(NAMES)
    bill_type = random.choice(["Electricity","Water","Gas","Internet"])
    write_pdf([
        f"TITLE:{bill_type.upper()} BILL",
        f"HEAD:{random.choice(CITIES)} {bill_type} Board",
        "---",
        f"Consumer Name: {name}",
        f"Consumer Number: {random.randint(100000000,999999999)}",
        f"Address: {random.choice(CITIES)} - {random.choice(PINCODES)}",
        f"Bill Number: {random.randint(100000,999999)}",
        f"Bill Date: {rdate()}",
        f"Due Date: {rdate()}",
        "---",
        "HEAD:Usage Details",
        f"Previous Reading: {random.randint(1000,9000)}",
        f"Current Reading: {random.randint(9001,15000)}",
        f"Units Consumed: {random.randint(100,500)}",
        "---",
        "HEAD:Amount",
        f"Current Charges: Rs. {random.randint(500,5000):,}",
        f"Arrears: Rs. {random.randint(0,1000):,}",
        f"Total Amount Due: Rs. {random.randint(500,6000):,}",
        "---",
        "Pay online at: www.utility.gov.in",
        f"Helpline: {rphone()}",
    ], OUTPUT_DIR / "utility_bill" / f"utility_{i:03d}.pdf")

def gen_property_document(i):
    name = random.choice(NAMES)
    write_pdf([
        "TITLE:PROPERTY DOCUMENT",
        "Sub-Registrar Office",
        f"{random.choice(CITIES)}, {random.choice(STATES)}",
        "---",
        "HEAD:Sale Deed",
        f"Seller: {random.choice(NAMES)}",
        f"Buyer: {name}",
        f"Date of Registration: {rdate()}",
        "---",
        "HEAD:Property Details",
        f"Survey Number: {random.randint(100,999)}/{random.randint(1,99)}",
        f"Area: {random.randint(500,5000)} sq.ft",
        f"Location: {random.choice(CITIES)} - {random.choice(PINCODES)}",
        f"Property Type: {random.choice(['Residential','Commercial','Agricultural'])}",
        "",
        "HEAD:Transaction",
        f"Sale Consideration: Rs. {random.randint(10,500)*100000:,}",
        f"Stamp Duty Paid: Rs. {random.randint(1,10)*10000:,}",
        f"Registration Number: {random.randint(1000,9999)}/{random.randint(2020,2024)}",
        "---",
        "Registered by: Sub-Registrar",
        "This document is legally valid.",
    ], OUTPUT_DIR / "property_document" / f"property_{i:03d}.pdf")

def gen_noc_letter(i):
    name = random.choice(NAMES)
    write_pdf([
        "TITLE:NO OBJECTION CERTIFICATE",
        f"HEAD:{random.choice(COMPANIES)}",
        f"Date: {rdate()}",
        "---",
        "To Whom It May Concern,",
        "",
        f"This is to certify that {name}",
        f"Employee ID: EMP{random.randint(1000,9999)}",
        f"Designation: {random.choice(['Engineer','Manager','Analyst','Developer'])}",
        "",
        f"has been employed with us since {rdate()}.",
        "",
        "We have no objection to this employee:",
        f"- {random.choice(['Applying for higher education','Obtaining a visa','Taking up part-time work','Travelling abroad'])}",
        "",
        "This NOC is issued for official purposes only.",
        "",
        f"Authorized Signatory",
        f"HR Manager",
        f"Contact: hr@company.com | {rphone()}",
    ], OUTPUT_DIR / "noc_letter" / f"noc_{i:03d}.pdf")

def gen_medical_certificate(i):
    name = random.choice(NAMES)
    doctor = random.choice(NAMES)
    write_pdf([
        "TITLE:MEDICAL FITNESS CERTIFICATE",
        f"HEAD:Dr. {doctor}",
        f"MBBS, MD - {random.choice(['General Medicine','Surgery','Orthopedics'])}",
        f"Reg. No: MCI-{random.randint(10000,99999)}",
        "---",
        f"Patient Name: {name}",
        f"Age: {random.randint(18,60)} years",
        f"Date of Examination: {rdate()}",
        "---",
        "HEAD:Certificate",
        f"This is to certify that {name} was examined by me",
        f"on {rdate()} and found to be",
        f"{random.choice(['medically fit','physically fit for employment','fit for duty'])}.",
        "",
        f"Height: {random.randint(150,190)} cm",
        f"Weight: {random.randint(50,90)} kg",
        f"Blood Pressure: {random.randint(110,130)}/{random.randint(70,90)} mmHg",
        f"Blood Group: {random.choice(['A+','B+','O+','AB+'])}",
        "---",
        f"Dr. {doctor}",
        f"Hospital: {random.choice(CITIES)} Medical Center",
        f"Date: {rdate()}",
    ], OUTPUT_DIR / "medical_certificate" / f"medcert_{i:03d}.pdf")

def gen_lab_report(i):
    name = random.choice(NAMES)
    write_pdf([
        "TITLE:LABORATORY TEST REPORT",
        f"HEAD:{random.choice(CITIES)} Diagnostics",
        f"NABL Accredited Laboratory",
        "---",
        f"Patient Name: {name}",
        f"Age: {random.randint(18,70)} / {random.choice(['M','F'])}",
        f"Ref. Doctor: Dr. {random.choice(NAMES)}",
        f"Sample Collected: {rdate()}",
        f"Report Date: {rdate()}",
        f"Lab ID: LAB{random.randint(10000,99999)}",
        "---",
        "HEAD:Test Results",
        f"Haemoglobin: {random.uniform(10,16):.1f} g/dL (Normal: 12-17)",
        f"WBC Count: {random.randint(4000,10000)} cells/uL (Normal: 4000-11000)",
        f"Platelet Count: {random.randint(150,400)*1000} /uL (Normal: 150000-400000)",
        f"Blood Sugar (Fasting): {random.randint(70,120)} mg/dL (Normal: 70-100)",
        f"Cholesterol (Total): {random.randint(150,250)} mg/dL (Normal: <200)",
        "---",
        "Pathologist: Dr. " + random.choice(NAMES),
        f"Contact: {rphone()}",
    ], OUTPUT_DIR / "lab_report" / f"lab_{i:03d}.pdf")

def gen_discharge_summary(i):
    name = random.choice(NAMES)
    write_pdf([
        "TITLE:HOSPITAL DISCHARGE SUMMARY",
        f"HEAD:{random.choice(CITIES)} General Hospital",
        "---",
        f"Patient Name: {name}",
        f"Age: {random.randint(18,80)} years",
        f"IP Number: IP{random.randint(100000,999999)}",
        f"Date of Admission: {rdate()}",
        f"Date of Discharge: {rdate()}",
        f"Ward: {random.choice(['General','ICU','Surgical','Medical'])}",
        "---",
        "HEAD:Diagnosis",
        f"Primary: {random.choice(['Pneumonia','Appendicitis','Fracture','Dengue Fever'])}",
        "",
        "HEAD:Treatment",
        "Patient was admitted and treated with appropriate medications.",
        f"Surgery performed: {random.choice(['Yes','No'])}",
        f"Condition at discharge: {random.choice(['Stable','Improved','Recovered'])}",
        "---",
        "HEAD:Discharge Advice",
        "- Take prescribed medications regularly",
        f"- Follow up after {random.randint(7,30)} days",
        "- Avoid strenuous activity",
        "",
        f"Treating Doctor: Dr. {random.choice(NAMES)}",
    ], OUTPUT_DIR / "discharge_summary" / f"discharge_{i:03d}.pdf")

def gen_business_registration(i):
    company = random.choice(COMPANIES)
    write_pdf([
        "TITLE:CERTIFICATE OF INCORPORATION",
        "Ministry of Corporate Affairs",
        "Government of India",
        "---",
        f"Company Name: {company} Private Limited",
        f"CIN: U{random.randint(10000,99999)}{random.choice(STATES[:2]).upper()}{random.randint(2010,2023)}PTC{random.randint(100000,999999)}",
        f"Date of Incorporation: {rdate()}",
        f"Registered Office: {random.choice(CITIES)} - {random.choice(PINCODES)}",
        f"Type: {random.choice(['Private Limited','Public Limited','LLP','OPC'])}",
        f"Authorized Capital: Rs. {random.randint(1,100)*100000:,}",
        f"Paid-up Capital: Rs. {random.randint(1,50)*100000:,}",
        "---",
        "Issued by: Registrar of Companies",
        "This certificate is valid until cancelled.",
    ], OUTPUT_DIR / "business_registration" / f"business_{i:03d}.pdf")

def gen_gst_certificate(i):
    company = random.choice(COMPANIES)
    write_pdf([
        "TITLE:GST REGISTRATION CERTIFICATE",
        "Goods and Services Tax Network",
        "Government of India",
        "---",
        f"Legal Name: {company}",
        f"GSTIN: {random.randint(10,35)}{random.choice('ABCDE')}{random.choice('ABCDE')}{random.choice('ABCDE')}{random.randint(1000,9999)}{random.choice('ABCDE')}{random.randint(1,9)}Z{random.choice('ABCDE')}",
        f"Trade Name: {company}",
        f"Registration Date: {rdate()}",
        f"State: {random.choice(STATES)}",
        f"Business Type: {random.choice(['Regular','Composition','SEZ'])}",
        "",
        "HEAD:Principal Place of Business",
        f"Address: {random.choice(CITIES)} - {random.choice(PINCODES)}",
        "---",
        "This certificate is valid as long as registration is active.",
        "Verify at: www.gst.gov.in",
    ], OUTPUT_DIR / "gst_certificate" / f"gst_{i:03d}.pdf")

def gen_trade_licence(i):
    company = random.choice(COMPANIES)
    write_pdf([
        "TITLE:TRADE LICENCE",
        f"Municipal Corporation of {random.choice(CITIES)}",
        "---",
        f"Business Name: {company}",
        f"Owner: {random.choice(NAMES)}",
        f"Business Type: {random.choice(['Retail Shop','Restaurant','IT Services','Manufacturing'])}",
        f"Address: {random.choice(CITIES)} - {random.choice(PINCODES)}",
        f"Licence Number: TL{random.randint(100000,999999)}",
        f"Date of Issue: {rdate()}",
        f"Valid Until: {rdate()}",
        f"Fee Paid: Rs. {random.randint(1,10)*1000:,}",
        "---",
        "Issued by: Municipal Commissioner",
        "This licence must be displayed at the premises.",
        "Renewal required annually.",
    ], OUTPUT_DIR / "trade_licence" / f"trade_{i:03d}.pdf")

def gen_quotation(i):
    company = random.choice(COMPANIES)
    client = random.choice(COMPANIES)
    write_pdf([
        "TITLE:QUOTATION",
        f"HEAD:{company}",
        f"Quotation No: QT{random.randint(1000,9999)}",
        f"Date: {rdate()}",
        f"Valid Until: {rdate()}",
        "---",
        f"To: {client}",
        f"Attention: {random.choice(NAMES)}",
        "---",
        "HEAD:Items",
        f"1. {random.choice(['Software Development','IT Consulting','Hardware Supply','Training'])}",
        f"   Quantity: {random.randint(1,10)} | Unit Price: {ramt()} | Total: {ramt()}",
        f"2. {random.choice(['Support & Maintenance','Installation','Testing','Documentation'])}",
        f"   Quantity: {random.randint(1,5)} | Unit Price: {ramt()} | Total: {ramt()}",
        "---",
        f"Subtotal: {ramt()}",
        f"GST 18%: Rs. {random.randint(1,5)*10000:,}",
        f"Grand Total: {ramt()}",
        "",
        "HEAD:Terms",
        "Payment: 50% advance, 50% on delivery",
        f"Delivery: {random.randint(7,30)} working days",
        "",
        f"Authorized by: {random.choice(NAMES)}, {company}",
    ], OUTPUT_DIR / "quotation" / f"quotation_{i:03d}.pdf")

GENERATORS = {
    "passport": gen_passport,
    "visa": gen_visa,
    "driving_licence": gen_driving_licence,
    "birth_certificate": gen_birth_certificate,
    "offer_letter": gen_offer_letter,
    "experience_letter": gen_experience_letter,
    "salary_slip": gen_salary_slip,
    "appointment_letter": gen_appointment_letter,
    "tax_return": gen_tax_return,
    "pan_card": gen_pan_card,
    "aadhar_card": gen_aadhar_card,
    "loan_agreement": gen_loan_agreement,
    "insurance_policy": gen_insurance_policy,
    "certificate": gen_certificate,
    "marksheet": gen_marksheet,
    "admission_letter": gen_admission_letter,
    "scholarship_letter": gen_scholarship_letter,
    "rent_agreement": gen_rent_agreement,
    "utility_bill": gen_utility_bill,
    "property_document": gen_property_document,
    "noc_letter": gen_noc_letter,
    "medical_certificate": gen_medical_certificate,
    "lab_report": gen_lab_report,
    "discharge_summary": gen_discharge_summary,
    "business_registration": gen_business_registration,
    "gst_certificate": gen_gst_certificate,
    "trade_licence": gen_trade_licence,
    "quotation": gen_quotation,
}

if __name__ == "__main__":
    count = 25
    print(f"Generating {count} PDFs x {len(GENERATORS)} types = {count*len(GENERATORS)} total\n")
    for name, fn in GENERATORS.items():
        print(f"  {name}...")
        for i in range(1, count+1):
            fn(i)
        print(f"  Done - {count} PDFs")
    print(f"\nAll done! {count*len(GENERATORS)} PDFs generated.")
    print("Now run: docker compose exec api python scripts/train_with_real_data.py")
