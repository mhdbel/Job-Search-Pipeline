import unittest
from unittest.mock import patch, MagicMock
from Job_Search.src.notifier import send_email, create_pdf, notify  # Updated imports

# Mock FPDF before it's used by notifier module when notifier is imported
class MockFPDF:
    def __init__(self):
        self.pages = 0
        self.font_set = False
        self.cells = []
        self.lns = []
        self.auto_page_break = False

    def add_page(self):
        self.pages += 1

    def set_font(self, family, style='', size=0):
        self.font_set = True

    def cell(self, w, h=0, txt='', border=0, ln=0, align='', fill=False, link=''):
        self.cells.append({'txt': txt, 'ln': ln})

    def ln(self, h=''):
        self.lns.append(h)

    def output(self, name, dest=''):
        self.output_path = name  # Record the output path for validation

    def set_auto_page_break(self, auto, margin=0):
        self.auto_page_break = auto

# Patch FPDF at the point where it's imported by the notifier module
@patch('Job_Search.src.notifier.FPDF', MockFPDF)
class TestNotifier(unittest.TestCase):

    def setUp(self):
        # Sample LLM-generated response
        self.sample_response = """I found 2 remote Python developer jobs:
1. Python Developer at Company A (Source: https://example.com/job/123 )
2. Data Scientist at Company B (Source: https://example.com/job/456 )"""
        self.sample_config = {
            'email': {
                'sender': 'test@example.com',
                'recipients': ['recipient1@example.com', 'recipient2@example.com'],
                'smtp_server': 'smtp.example.com',
                'smtp_port': 587,
                'smtp_password': 'password'
            },
            'cloud': {
                'pdf_destination': 'output/test_report.pdf'
            }
        }

    @patch('Job_Search.src.notifier.smtplib.SMTP')
    def test_send_email(self, mock_smtp_constructor):
        """Test the send_email function with an LLM-generated response."""
        mock_smtp_instance = MagicMock()  # Mock SMTP instance
        mock_smtp_constructor.return_value = mock_smtp_instance

        send_email(self.sample_response, self.sample_config)

        # Validate SMTP calls
        mock_smtp_constructor.assert_called_once_with(
            self.sample_config['email']['smtp_server'],
            self.sample_config['email']['smtp_port']
        )
        mock_smtp_instance.starttls.assert_called_once()
        mock_smtp_instance.login.assert_called_once_with(
            self.sample_config['email']['sender'],
            self.sample_config['email']['smtp_password']
        )

        # Validate email content
        args, kwargs = mock_smtp_instance.sendmail.call_args
        sent_from = args[0]
        sent_to_list = args[1]
        message_body = args[2]

        self.assertEqual(sent_from, self.sample_config['email']['sender'])
        self.assertEqual(sent_to_list, self.sample_config['email']['recipients'])
        self.assertIn('Subject: Job Search Results', message_body)
        self.assertIn('Python Developer at Company A (Source: https://example.com/job/123 )', message_body)
        self.assertIn('Data Scientist at Company B (Source: https://example.com/job/456 )', message_body)

        mock_smtp_instance.quit.assert_called_once()

    def test_create_pdf(self):
        """Test the create_pdf function with an LLM-generated response."""
        with patch('Job_Search.src.notifier.FPDF', spec=True) as mock_fpdf_constructor:
            mock_pdf_instance = MagicMock()
            mock_fpdf_constructor.return_value = mock_pdf_instance

            create_pdf(self.sample_response, self.sample_config)

            # Validate PDF creation steps
            mock_fpdf_constructor.assert_called_once()
            mock_pdf_instance.add_page.assert_called_once()
            mock_pdf_instance.set_font.assert_called_with("Arial", size=12)

            # Validate cell calls for the LLM-generated response
            self.assertTrue(
                any(call_args[1].get('txt', '').startswith('I found 2 remote Python developer jobs') 
                    for call_args in mock_pdf_instance.cell.call_args_list)
            )
            self.assertTrue(
                any(call_args[1].get('txt', '').startswith('1. Python Developer at Company A') 
                    for call_args in mock_pdf_instance.cell.call_args_list)
            )
            self.assertTrue(
                any(call_args[1].get('txt', '').startswith('2. Data Scientist at Company B') 
                    for call_args in mock_pdf_instance.cell.call_args_list)
            )

            # Validate PDF output path
            mock_pdf_instance.output.assert_called_once_with(self.sample_config['cloud']['pdf_destination'])

    @patch('Job_Search.src.notifier.send_email')
    @patch('Job_Search.src.notifier.create_pdf')
    def test_notify(self, mock_create_pdf, mock_send_email):
        """Test the notify function with an LLM-generated response."""
        notify(self.sample_response, self.sample_config)

        # Validate that both send_email and create_pdf were called with the correct arguments
        mock_send_email.assert_called_once_with(self.sample_response, self.sample_config)
        mock_create_pdf.assert_called_once_with(self.sample_response, self.sample_config)

if __name__ == '__main__':
    unittest.main()
