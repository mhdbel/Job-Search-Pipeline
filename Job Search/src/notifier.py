import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from fpdf import FPDF

def send_email(jobs, config):
    msg = MIMEMultipart()
    msg['From'] = config["email"]["sender"]
    msg['To'] = ", ".join(config["email"]["recipients"])
    msg['Subject'] = "Latest Job Offers"

    body = "\n".join([f"{job['title']} at {job['company']}: {job['link']}" for job in jobs])
    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP(config["email"]["smtp_server"], config["email"]["smtp_port"])
    server.starttls()
    server.login(msg['From'], config["email"]["smtp_password"])
    server.sendmail(msg['From'], config["email"]["recipients"], msg.as_string())
    server.quit()

def create_pdf(jobs, config):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)

    for job in jobs:
        pdf.cell(200, 10, txt=f"{job['title']} at {job['company']}", ln=True)
        pdf.cell(200, 10, txt=f"Link: {job['link']}", ln=True)
        pdf.ln(5)

    pdf.output(config["cloud"]["pdf_destination"])

def notify(jobs, config):
    send_email(jobs, config)
    create_pdf(jobs, config)