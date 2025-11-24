import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Dict

from fpdf import FPDF

def send_email(response: str, config: Dict[str, Any]):
    """
    Sends an email with the LLM-generated response.
    
    Args:
        response (str): The LLM-generated response to send.
        config (dict): Configuration dictionary containing email settings.
    """
    msg = MIMEMultipart()
    msg['From'] = config["email"]["sender"]
    msg['To'] = ", ".join(config["email"]["recipients"])
    msg['Subject'] = "Job Search Results"

    # Email body includes the LLM-generated response
    body = response
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(config["email"]["smtp_server"], config["email"]["smtp_port"])
        server.starttls()
        smtp_password = os.getenv("SMTP_PASSWORD", config["email"].get("smtp_password", ""))
        if not smtp_password:
            raise ValueError("SMTP password missing. Set SMTP_PASSWORD env var or email.smtp_password in config.")

        server.login(msg['From'], smtp_password)
        server.sendmail(msg['From'], config["email"]["recipients"], msg.as_string())
        server.quit()
        print("Email notification sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")

def create_pdf(response: str, config: Dict[str, Any]):
    """
    Creates a PDF report with the LLM-generated response.
    
    Args:
        response (str): The LLM-generated response to include in the PDF.
        config (dict): Configuration dictionary containing PDF output path.
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)

    # Add the LLM-generated response to the PDF
    for line in response.splitlines():
        pdf.cell(0, 10, txt=line, ln=1)

    # Save the PDF to the specified destination
    destination = config["cloud"]["pdf_destination"]
    os.makedirs(os.path.dirname(destination), exist_ok=True)
    pdf.output(destination)
    print(f"PDF report created successfully at {destination}.")

def notify(response, config):
    """
    Sends notifications via email and creates a PDF report.
    
    Args:
        response (str): The LLM-generated response to notify.
        config (dict): Configuration dictionary containing email and PDF settings.
    """
    # Send email notification
    send_email(response, config)

    # Create PDF report
    create_pdf(response, config)
