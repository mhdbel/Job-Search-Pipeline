import unittest
from unittest.mock import patch, MagicMock, mock_open
import os
from Job_Search.src.notifier import send_email, create_pdf, notify # Assuming notifier.py is in src

# Mock FPDF before it's used by notifier module when notifier is imported
# This is a common pattern for mocking classes that are instantiated within a module.
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
        self.output_path = name
        # In a real test, you might check if 'name' is as expected.
        # For simplicity, we just record it was called.
        pass 
    
    def set_auto_page_break(self, auto, margin=0):
        self.auto_page_break = auto

# Patch FPDF at the point where it's imported by the notifier module
# This assumes 'from fpdf import FPDF' is in notifier.py
@patch('Job_Search.src.notifier.FPDF', MockFPDF) 
class TestNotifier(unittest.TestCase):

    def setUp(self):
        self.sample_jobs = [
            {'title': 'Software Engineer', 'company': 'TestCo', 'link': 'http://example.com/job1'},
            {'title': 'Data Analyst', 'company': 'AnotherCo', 'link': 'http://example.com/job2'}
        ]
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

    @patch('Job_Search.src.notifier.smtplib.SMTP') # Mock the SMTP object
    def test_send_email(self, mock_smtp_constructor, mock_fpdf_class_ref_ignored_here):
        """Test the send_email function."""
        # mock_fpdf_class_ref_ignored_here is the @patch from the class decorator, not used in this specific method
        mock_smtp_instance = MagicMock() # This is the object returned by SMTP()
        mock_smtp_constructor.return_value = mock_smtp_instance # SMTP(...) will return our mock

        send_email(self.sample_jobs, self.sample_config)

        mock_smtp_constructor.assert_called_once_with(self.sample_config['email']['smtp_server'], 
                                                      self.sample_config['email']['smtp_port'])
        mock_smtp_instance.starttls.assert_called_once()
        mock_smtp_instance.login.assert_called_once_with(self.sample_config['email']['sender'], 
                                                        self.sample_config['email']['smtp_password'])
        
        # Check email content (somewhat)
        # The actual message string is msg.as_string(). We can check parts of it.
        args, kwargs = mock_smtp_instance.sendmail.call_args
        sent_from = args[0]
        sent_to_list = args[1]
        message_body = args[2]

        self.assertEqual(sent_from, self.sample_config['email']['sender'])
        self.assertEqual(sent_to_list, self.sample_config['email']['recipients'])
        self.assertIn('Subject: Latest Job Offers', message_body)
        self.assertIn('Software Engineer at TestCo: http://example.com/job1', message_body)
        self.assertIn('Data Analyst at AnotherCo: http://example.com/job2', message_body)
        
        mock_smtp_instance.quit.assert_called_once()

    # No need to patch FPDF here again, it's done at class level
    def test_create_pdf(self, mock_fpdf_class_ref):
        """Test the create_pdf function."""
        # mock_fpdf_class_ref is the @patch from the class decorator
        # When create_pdf calls FPDF(), it gets an instance of MockFPDF
        
        # Reset mock instance for this test (if MockFPDF was stateful across calls)
        # For this MockFPDF, a new one is made each time FPDF() is called in create_pdf
        # so we access the globally patched one or its instances as needed.
        # In this case, the mock_fpdf_class_ref *is* MockFPDF.
        # We want to inspect the instance *created by* create_pdf.
        # So, we'll rely on the fact that MockFPDF is instantiated once inside create_pdf
        # and then its methods are called.

        # To inspect the instance, we can make MockFPDF store its last instance
        # or make the class patch return a MagicMock that *then* returns MockFPDF instances.
        # For simplicity with current MockFPDF, we'll assume it's used correctly.
        # A more robust way: 
        # mock_fpdf_instance = MagicMock(spec=FPDF) # spec helps with autospeccing
        # mock_fpdf_class_ref.return_value = mock_fpdf_instance
        # create_pdf(self.sample_jobs, self.sample_config)
        # mock_fpdf_instance.add_page.assert_called()
        
        # Using the simpler MockFPDF, we can't directly get THE instance easily here
        # unless we modify MockFPDF or how it's patched for the class.
        # Let's assume for now that if FPDF() is called, our MockFPDF is used.
        # We will rely on the single instance of MockFPDF being created by the create_pdf function
        # and then its methods being called.

        # To actually test what create_pdf does with FPDF, we might need to refine the mock.
        # For now, let's assume the MockFPDF is correctly instantiated by create_pdf.
        # We can't directly assert on the instance from here without more complex mock setup.
        # This test will be more of a placeholder to ensure create_pdf runs without error with the mock.
        
        # A better way for the class-level patch if we need to inspect instances:
        # @patch('Job_Search.src.notifier.FPDF', return_value=MagicMock(spec=FPDF)) 
        # This would make FPDF() return a MagicMock we can inspect.
        # For now, the test is limited by the current MockFPDF design.

        # Let's try to make the mock accessible for inspection
        # Re-patching inside the method for finer control, or using a side_effect on the class mock.
        with patch('Job_Search.src.notifier.FPDF', spec=True) as mock_fpdf_constructor:
            mock_pdf_instance = MagicMock()
            mock_fpdf_constructor.return_value = mock_pdf_instance
            
            create_pdf(self.sample_jobs, self.sample_config)

            mock_fpdf_constructor.assert_called_once()
            mock_pdf_instance.add_page.assert_called_once()
            mock_pdf_instance.set_font.assert_called_with("Arial", size=12)
            
            # Check if cell was called for each job title and link
            # This count assumes two calls per job (title, link)
            self.assertEqual(mock_pdf_instance.cell.call_count, len(self.sample_jobs) * 2)
            self.assertTrue(any(call_args[1].get('txt', '').startswith('Software Engineer at TestCo') for call_args in mock_pdf_instance.cell.call_args_list))
            self.assertTrue(any(call_args[1].get('txt', '').startswith('Link: http://example.com/job1') for call_args in mock_pdf_instance.cell.call_args_list))

            mock_pdf_instance.output.assert_called_once_with(self.sample_config['cloud']['pdf_destination'])

    @patch('Job_Search.src.notifier.send_email')
    @patch('Job_Search.src.notifier.create_pdf')
    def test_notify(self, mock_create_pdf, mock_send_email, mock_fpdf_class_ref_ignored_here):
        """Test the main notify function."""
        notify(self.sample_jobs, self.sample_config)
        mock_send_email.assert_called_once_with(self.sample_jobs, self.sample_config)
        mock_create_pdf.assert_called_once_with(self.sample_jobs, self.sample_config)

if __name__ == '__main__':
    unittest.main()
