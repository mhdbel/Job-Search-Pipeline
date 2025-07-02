import os
import sys

# Add src to path to allow direct import if running script from Job_Search directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from notifier import notify, create_pdf, send_email
from scraper import load_config # To load the actual config
from logger import setup_logger

if __name__ == '__main__':
    logger = setup_logger()
    logger.info("Starting manual notification test...")

    # 1. Load the actual configuration
    config = load_config()
    if not config:
        logger.error("Failed to load config.yaml. Ensure it's correctly set up in Job Search/config/")
        exit()

    # 2. Prepare sample job data
    sample_jobs_data = [
        {'title': 'Manual Test Job 1', 'company': 'Test Corp', 'link': 'http://example.com/testjob1', 'applicants': 3},
        {'title': 'Manual Test Job 2', 'company': 'Another Test Inc', 'link': 'http://example.com/testjob2', 'applicants': 12},
        {'title': 'Interesting Manual Job', 'company': 'Special Co', 'link': 'http://example.com/testjob_interesting', 'applicants': 1},
    ]
    
    # Ensure output directory exists for PDF
    # Use a default if not specified, and ensure it's within Job_Search/output
    pdf_relative_path = config.get('cloud', {}).get('pdf_destination', 'output/default_manual_report.pdf')
    pdf_absolute_path = os.path.abspath(os.path.join(os.path.dirname(__file__), pdf_relative_path))
    output_dir = os.path.dirname(pdf_absolute_path)

    if not os.path.exists(output_dir):
        logger.info(f"Creating output directory: {output_dir}")
        os.makedirs(output_dir)

    # 3. Test PDF creation
    logger.info(f"Attempting to create PDF at: {pdf_absolute_path}")
    try:
        # create_pdf expects config to have cloud.pdf_destination as a relative path from project root
        # but the function itself doesn't know the project root, so it will write relative to CWD.
        # For this test script, if pdf_destination is 'output/file.pdf', it will try to save to 'Job_Search/output/file.pdf'
        # if the script is run from 'Job_Search'.
        # The create_pdf function in notifier.py uses `pdf.output(config["cloud"]["pdf_destination"])`
        # This path should ideally be relative to the project root or made absolute.
        # For this test, we will assume config["cloud"]["pdf_destination"] is like "output/report.pdf"
        # and the test script is run from "Job Search/"
        create_pdf(sample_jobs_data, config) 
        logger.info(f"PDF creation called. Check for '{pdf_relative_path}'.")
        if os.path.exists(pdf_absolute_path):
            logger.info(f"SUCCESS: PDF file found at {pdf_absolute_path}")
        else:
            logger.error(f"FAILURE: PDF file NOT found at {pdf_absolute_path}. CWD: {os.getcwd()}")

    except Exception as e:
        logger.error(f"Error during create_pdf: {e}", exc_info=True)

    # 4. Test Email Sending (Optional - Requires real SMTP config)
    send_real_email = False # <<<< SET TO True AND CONFIGURE config.yaml TO TEST ACTUAL EMAIL SENDING
    if send_real_email:
        email_config = config.get('email', {})
        if not email_config.get('smtp_password') or \
           email_config.get('smtp_password') == 'your-email-password' or \
           not email_config.get('sender') or \
           not email_config.get('recipients'):
            logger.warning("Email sender, recipients, or SMTP password is not set or is default in config.yaml. Skipping actual email send test.")
        else:
            logger.info(f"Attempting to send a real email from {email_config.get('sender')} to {email_config.get('recipients')}...")
            try:
                send_email(sample_jobs_data, config)
                logger.info("Email sending function called. Check recipient inbox(es).")
            except Exception as e:
                logger.error(f"Error during send_email: {e}", exc_info=True)
    else:
        logger.info("Skipping real email sending test as 'send_real_email' is False.")
        
    logger.info("Manual notification test finished. Please check generated files/emails and report back.")
