import os
import tempfile
import shutil
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test.utils import override_settings
from django.conf import settings
import json


class UploadEndpointsTest(TestCase):
    """
    Unit tests for filebrowser upload endpoints to verify Django 4/5 compatibility.
    Tests both _upload_file and _check_file endpoints.
    """
    
    def setUp(self):
        """Set up test environment with temp media directory and admin user."""
        # Create temporary media directory
        self.temp_media_dir = tempfile.mkdtemp()
        self.temp_filebrowser_dir = os.path.join(self.temp_media_dir, 'filebrowser')
        os.makedirs(self.temp_filebrowser_dir, exist_ok=True)
        
        # Create admin user for staff_member_required decorator
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='admin123',
            is_staff=True,
            is_superuser=True
        )
        
        # Create test client
        self.client = Client()
        self.client.login(username='admin', password='admin123')
        
        # Test file content
        self.test_file_content = b'Test file content for upload testing'
        
    def tearDown(self):
        """Clean up temporary media directory."""
        if os.path.exists(self.temp_media_dir):
            shutil.rmtree(self.temp_media_dir)
    
    @override_settings(MEDIA_ROOT=None)  # Will be set dynamically
    def test_check_file_endpoint_post_nonexistent_file(self):
        """Test _check_file endpoint with non-existent file."""
        with self.settings(
            MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_DIRECTORY=''
        ):
            response = self.client.post(reverse('fb_check'), {
                'folder': '',
                'testfile': 'nonexistent.txt'
            })
            
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response['Content-Type'], 'application/json')
            
            # Parse JSON response
            response_data = json.loads(response.content.decode())
            self.assertEqual(response_data, {})
    
    @override_settings(MEDIA_ROOT=None)  # Will be set dynamically
    def test_check_file_endpoint_post_existing_file(self):
        """Test _check_file endpoint with existing file."""
        with self.settings(
            MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_DIRECTORY=''
        ):
            # Create a test file first
            test_file_path = os.path.join(self.temp_media_dir, 'existing.txt')
            with open(test_file_path, 'w') as f:
                f.write('existing file content')
            
            response = self.client.post(reverse('fb_check'), {
                'folder': '',
                'testfile': 'existing.txt'
            })
            
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response['Content-Type'], 'application/json')
            
            # Parse JSON response - should return the existing file name
            response_data = json.loads(response.content.decode())
            self.assertEqual(response_data, {'testfile': 'existing.txt'})
    
    @override_settings(MEDIA_ROOT=None)  # Will be set dynamically
    def test_upload_file_endpoint_successful_upload(self):
        """Test _upload_file endpoint with successful file upload."""
        with self.settings(
            MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_DIRECTORY=''
        ):
            # Create uploaded file
            uploaded_file = SimpleUploadedFile(
                "test_upload.txt",
                self.test_file_content,
                content_type="text/plain"
            )
            
            response = self.client.post(reverse('fb_do_upload'), {
                'folder': '',
                'Filedata': uploaded_file
            })
            
            self.assertEqual(response.status_code, 200)
            # Can be JSON or 'True' for backward compatibility
            response_text = response.content.decode()
            if response_text.startswith('{'):
                response_data = json.loads(response_text)
                self.assertTrue(response_data.get('success', False))
            else:
                self.assertEqual(response_text, 'True')


class FileOverrideTest(TestCase):
    """
    Unit tests for file override functionality.
    Tests the new override parameter and error handling.
    """
    
    def setUp(self):
        """Set up test environment with temp media directory and admin user."""
        # Create temporary media directory
        self.temp_media_dir = tempfile.mkdtemp()
        self.temp_filebrowser_dir = os.path.join(self.temp_media_dir, 'filebrowser')
        os.makedirs(self.temp_filebrowser_dir, exist_ok=True)
        
        # Create admin user for staff_member_required decorator
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='admin123',
            is_staff=True,
            is_superuser=True
        )
        
        # Create test client
        self.client = Client()
        self.client.login(username='admin', password='admin123')
        
        # Test file content
        self.test_file_content = b'Test file content for upload testing'
        self.new_file_content = b'New file content for override testing'
        
    def tearDown(self):
        """Clean up temporary media directory."""
        if os.path.exists(self.temp_media_dir):
            shutil.rmtree(self.temp_media_dir)
    
    @override_settings(MEDIA_ROOT=None)
    def test_upload_file_without_override_returns_error(self):
        """Test upload file when file exists and override is not set."""
        with self.settings(
            MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_DIRECTORY=''
        ):
            # Create existing file
            existing_file_path = os.path.join(self.temp_media_dir, 'existing.txt')
            with open(existing_file_path, 'wb') as f:
                f.write(self.test_file_content)
            
            # Upload new file with same name without override
            uploaded_file = SimpleUploadedFile(
                "existing.txt",
                self.new_file_content,
                content_type="text/plain"
            )
            
            response = self.client.post(reverse('fb_do_upload'), {
                'folder': '',
                'override': 'false',
                'Filedata': uploaded_file
            })
            
            # Should return 400 error
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response['Content-Type'], 'application/json')
            
            # Parse JSON error response
            response_data = json.loads(response.content.decode())
            self.assertEqual(response_data['error'], 'FILE_EXISTS')
            self.assertEqual(response_data['filename'], 'existing.txt')
            self.assertIn('message', response_data)
            
            # Verify file was NOT replaced
            with open(existing_file_path, 'rb') as f:
                self.assertEqual(f.read(), self.test_file_content)
    
    @override_settings(MEDIA_ROOT=None)
    def test_upload_file_with_override_replaces_file(self):
        """Test upload file when file exists and override is set."""
        with self.settings(
            MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_DIRECTORY=''
        ):
            # Create existing file
            existing_file_path = os.path.join(self.temp_media_dir, 'existing.txt')
            with open(existing_file_path, 'wb') as f:
                f.write(self.test_file_content)
            
            # Upload new file with same name with override
            uploaded_file = SimpleUploadedFile(
                "existing.txt",
                self.new_file_content,
                content_type="text/plain"
            )
            
            response = self.client.post(reverse('fb_do_upload'), {
                'folder': '',
                'override': 'true',
                'Filedata': uploaded_file
            })
            
            # Should return success
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response['Content-Type'], 'application/json')
            
            # Parse JSON success response
            response_data = json.loads(response.content.decode())
            self.assertTrue(response_data['success'])
            self.assertEqual(response_data['filename'], 'existing.txt')
            
            # Verify file content was replaced
            with open(existing_file_path, 'rb') as f:
                self.assertEqual(f.read(), self.new_file_content)
    
    @override_settings(MEDIA_ROOT=None)
    def test_upload_file_new_file_no_override_needed(self):
        """Test upload new file (doesn't exist) without override parameter."""
        with self.settings(
            MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_DIRECTORY=''
        ):
            # Upload new file
            uploaded_file = SimpleUploadedFile(
                "new_file.txt",
                self.test_file_content,
                content_type="text/plain"
            )
            
            response = self.client.post(reverse('fb_do_upload'), {
                'folder': '',
                'Filedata': uploaded_file
            })
            
            # Should return success
            self.assertEqual(response.status_code, 200)
            
            # Verify file was created
            uploaded_file_path = os.path.join(self.temp_media_dir, 'new_file.txt')
            self.assertTrue(os.path.exists(uploaded_file_path))
            
            # Verify file content
            with open(uploaded_file_path, 'rb') as f:
                self.assertEqual(f.read(), self.test_file_content)
    
    @override_settings(MEDIA_ROOT=None)
    def test_upload_file_error_response_format(self):
        """Test error response format is valid JSON."""
        with self.settings(
            MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_DIRECTORY=''
        ):
            # Create existing file
            existing_file_path = os.path.join(self.temp_media_dir, 'test.txt')
            with open(existing_file_path, 'wb') as f:
                f.write(b'existing')
            
            # Upload without override
            uploaded_file = SimpleUploadedFile(
                "test.txt",
                b'new',
                content_type="text/plain"
            )
            
            response = self.client.post(reverse('fb_do_upload'), {
                'folder': '',
                'Filedata': uploaded_file
            })
            
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response['Content-Type'], 'application/json')
            
            # Verify response is valid JSON
            response_data = json.loads(response.content.decode())
            self.assertIn('error', response_data)
            self.assertIn('filename', response_data)
            self.assertEqual(response_data['error'], 'FILE_EXISTS')
    
    @override_settings(MEDIA_ROOT=None)
    def test_upload_file_success_response_format(self):
        """Test success response format is valid JSON."""
        with self.settings(
            MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_DIRECTORY=''
        ):
            # Upload new file
            uploaded_file = SimpleUploadedFile(
                "success_test.txt",
                self.test_file_content,
                content_type="text/plain"
            )
            
            response = self.client.post(reverse('fb_do_upload'), {
                'folder': '',
                'Filedata': uploaded_file
            })
            
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response['Content-Type'], 'application/json')
            
            # Verify response is valid JSON
            response_data = json.loads(response.content.decode())
            self.assertIn('success', response_data)
            self.assertIn('filename', response_data)
            self.assertTrue(response_data['success'])
    
    @override_settings(MEDIA_ROOT=None)
    def test_upload_file_override_with_different_content(self):
        """Test override with different content."""
        with self.settings(
            MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_DIRECTORY=''
        ):
            # Create existing file with specific content
            existing_file_path = os.path.join(self.temp_media_dir, 'content_test.txt')
            original_content = b'original content line 1\noriginal content line 2'
            with open(existing_file_path, 'wb') as f:
                f.write(original_content)
            
            # Upload new file with different content and override
            new_content = b'new content line 1\nnew content line 2\nnew content line 3'
            uploaded_file = SimpleUploadedFile(
                "content_test.txt",
                new_content,
                content_type="text/plain"
            )
            
            response = self.client.post(reverse('fb_do_upload'), {
                'folder': '',
                'override': 'true',
                'Filedata': uploaded_file
            })
            
            self.assertEqual(response.status_code, 200)
            
            # Verify new content replaced old content
            with open(existing_file_path, 'rb') as f:
                file_content = f.read()
                self.assertEqual(file_content, new_content)
                self.assertNotEqual(file_content, original_content)
    
    @override_settings(MEDIA_ROOT=None)
    def test_upload_file_override_with_special_characters(self):
        """Test override with filenames containing special characters."""
        with self.settings(
            MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_DIRECTORY=''
        ):
            # Create existing file with special characters in name
            filename = "test file with spaces & special chars!.txt"
            # Note: convert_filename will convert this
            converted_name = filename.replace(' ', '_').lower()
            existing_file_path = os.path.join(self.temp_media_dir, converted_name)
            with open(existing_file_path, 'wb') as f:
                f.write(b'original')
            
            # Upload with override
            uploaded_file = SimpleUploadedFile(
                filename,
                b'new content',
                content_type="text/plain"
            )
            
            response = self.client.post(reverse('fb_do_upload'), {
                'folder': '',
                'override': 'true',
                'Filedata': uploaded_file
            })
            
            self.assertEqual(response.status_code, 200)
            
            # Verify file was replaced (filename will be converted)
            self.assertTrue(os.path.exists(existing_file_path))
            with open(existing_file_path, 'rb') as f:
                self.assertEqual(f.read(), b'new content')
    
    @override_settings(MEDIA_ROOT=None)
    def test_upload_file_override_various_override_values(self):
        """Test that various override parameter values work."""
        with self.settings(
            MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_DIRECTORY=''
        ):
            # Create existing file
            existing_file_path = os.path.join(self.temp_media_dir, 'override_test.txt')
            with open(existing_file_path, 'wb') as f:
                f.write(b'original')
            
            # Test various override values that should be treated as True
            for override_value in ['true', 'True', 'TRUE', '1', 'yes', 'Yes', 'YES', 'on', 'On', 'ON']:
                uploaded_file = SimpleUploadedFile(
                    "override_test.txt",
                    b'new content',
                    content_type="text/plain"
                )
                
                response = self.client.post(reverse('fb_do_upload'), {
                    'folder': '',
                    'override': override_value,
                    'Filedata': uploaded_file
                })
                
                self.assertEqual(response.status_code, 200, 
                               "Override value '%s' should be treated as True" % override_value)
                
                # Reset file for next iteration
                with open(existing_file_path, 'wb') as f:
                    f.write(b'original')
            
            # Test override values that should be treated as False
            for override_value in ['false', 'False', 'FALSE', '0', 'no', 'No', 'NO', 'off', 'Off', 'OFF', '']:
                uploaded_file = SimpleUploadedFile(
                    "override_test.txt",
                    b'should not replace',
                    content_type="text/plain"
                )
                
                response = self.client.post(reverse('fb_do_upload'), {
                    'folder': '',
                    'override': override_value,
                    'Filedata': uploaded_file
                })
                
                self.assertEqual(response.status_code, 400,
                               "Override value '%s' should be treated as False" % override_value)
            
            # Verify file was actually uploaded
            uploaded_file_path = os.path.join(self.temp_media_dir, 'test_upload.txt')
            self.assertTrue(os.path.exists(uploaded_file_path))
            
            # Verify file content
            with open(uploaded_file_path, 'rb') as f:
                self.assertEqual(f.read(), self.test_file_content)
    
    @override_settings(MEDIA_ROOT=None)  # Will be set dynamically
    def test_upload_file_endpoint_no_file_data(self):
        """Test _upload_file endpoint with no file data."""
        with self.settings(
            MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_DIRECTORY=''
        ):
            response = self.client.post(reverse('fb_do_upload'), {
                'folder': '/filebrowser/'
            })
            
            self.assertEqual(response.status_code, 200)
            # Can be JSON or 'True' for backward compatibility
            response_text = response.content.decode()
            if response_text.startswith('{'):
                response_data = json.loads(response_text)
                self.assertTrue(response_data.get('success', False))
            else:
                self.assertEqual(response_text, 'True')


class FileOverrideTest(TestCase):
    """
    Unit tests for file override functionality.
    Tests the new override parameter and error handling.
    """
    
    def setUp(self):
        """Set up test environment with temp media directory and admin user."""
        # Create temporary media directory
        self.temp_media_dir = tempfile.mkdtemp()
        self.temp_filebrowser_dir = os.path.join(self.temp_media_dir, 'filebrowser')
        os.makedirs(self.temp_filebrowser_dir, exist_ok=True)
        
        # Create admin user for staff_member_required decorator
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='admin123',
            is_staff=True,
            is_superuser=True
        )
        
        # Create test client
        self.client = Client()
        self.client.login(username='admin', password='admin123')
        
        # Test file content
        self.test_file_content = b'Test file content for upload testing'
        self.new_file_content = b'New file content for override testing'
        
    def tearDown(self):
        """Clean up temporary media directory."""
        if os.path.exists(self.temp_media_dir):
            shutil.rmtree(self.temp_media_dir)
    
    @override_settings(MEDIA_ROOT=None)
    def test_upload_file_without_override_returns_error(self):
        """Test upload file when file exists and override is not set."""
        with self.settings(
            MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_DIRECTORY=''
        ):
            # Create existing file
            existing_file_path = os.path.join(self.temp_media_dir, 'existing.txt')
            with open(existing_file_path, 'wb') as f:
                f.write(self.test_file_content)
            
            # Upload new file with same name without override
            uploaded_file = SimpleUploadedFile(
                "existing.txt",
                self.new_file_content,
                content_type="text/plain"
            )
            
            response = self.client.post(reverse('fb_do_upload'), {
                'folder': '',
                'override': 'false',
                'Filedata': uploaded_file
            })
            
            # Should return 400 error
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response['Content-Type'], 'application/json')
            
            # Parse JSON error response
            response_data = json.loads(response.content.decode())
            self.assertEqual(response_data['error'], 'FILE_EXISTS')
            self.assertEqual(response_data['filename'], 'existing.txt')
            self.assertIn('message', response_data)
            
            # Verify file was NOT replaced
            with open(existing_file_path, 'rb') as f:
                self.assertEqual(f.read(), self.test_file_content)
    
    @override_settings(MEDIA_ROOT=None)
    def test_upload_file_with_override_replaces_file(self):
        """Test upload file when file exists and override is set."""
        with self.settings(
            MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_DIRECTORY=''
        ):
            # Create existing file
            existing_file_path = os.path.join(self.temp_media_dir, 'existing.txt')
            with open(existing_file_path, 'wb') as f:
                f.write(self.test_file_content)
            
            # Upload new file with same name with override
            uploaded_file = SimpleUploadedFile(
                "existing.txt",
                self.new_file_content,
                content_type="text/plain"
            )
            
            response = self.client.post(reverse('fb_do_upload'), {
                'folder': '',
                'override': 'true',
                'Filedata': uploaded_file
            })
            
            # Should return success
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response['Content-Type'], 'application/json')
            
            # Parse JSON success response
            response_data = json.loads(response.content.decode())
            self.assertTrue(response_data['success'])
            self.assertEqual(response_data['filename'], 'existing.txt')
            
            # Verify file content was replaced
            with open(existing_file_path, 'rb') as f:
                self.assertEqual(f.read(), self.new_file_content)
    
    @override_settings(MEDIA_ROOT=None)
    def test_upload_file_new_file_no_override_needed(self):
        """Test upload new file (doesn't exist) without override parameter."""
        with self.settings(
            MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_DIRECTORY=''
        ):
            # Upload new file
            uploaded_file = SimpleUploadedFile(
                "new_file.txt",
                self.test_file_content,
                content_type="text/plain"
            )
            
            response = self.client.post(reverse('fb_do_upload'), {
                'folder': '',
                'Filedata': uploaded_file
            })
            
            # Should return success
            self.assertEqual(response.status_code, 200)
            
            # Verify file was created
            uploaded_file_path = os.path.join(self.temp_media_dir, 'new_file.txt')
            self.assertTrue(os.path.exists(uploaded_file_path))
            
            # Verify file content
            with open(uploaded_file_path, 'rb') as f:
                self.assertEqual(f.read(), self.test_file_content)
    
    @override_settings(MEDIA_ROOT=None)
    def test_upload_file_error_response_format(self):
        """Test error response format is valid JSON."""
        with self.settings(
            MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_DIRECTORY=''
        ):
            # Create existing file
            existing_file_path = os.path.join(self.temp_media_dir, 'test.txt')
            with open(existing_file_path, 'wb') as f:
                f.write(b'existing')
            
            # Upload without override
            uploaded_file = SimpleUploadedFile(
                "test.txt",
                b'new',
                content_type="text/plain"
            )
            
            response = self.client.post(reverse('fb_do_upload'), {
                'folder': '',
                'Filedata': uploaded_file
            })
            
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response['Content-Type'], 'application/json')
            
            # Verify response is valid JSON
            response_data = json.loads(response.content.decode())
            self.assertIn('error', response_data)
            self.assertIn('filename', response_data)
            self.assertEqual(response_data['error'], 'FILE_EXISTS')
    
    @override_settings(MEDIA_ROOT=None)
    def test_upload_file_success_response_format(self):
        """Test success response format is valid JSON."""
        with self.settings(
            MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_DIRECTORY=''
        ):
            # Upload new file
            uploaded_file = SimpleUploadedFile(
                "success_test.txt",
                self.test_file_content,
                content_type="text/plain"
            )
            
            response = self.client.post(reverse('fb_do_upload'), {
                'folder': '',
                'Filedata': uploaded_file
            })
            
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response['Content-Type'], 'application/json')
            
            # Verify response is valid JSON
            response_data = json.loads(response.content.decode())
            self.assertIn('success', response_data)
            self.assertIn('filename', response_data)
            self.assertTrue(response_data['success'])
    
    @override_settings(MEDIA_ROOT=None)
    def test_upload_file_override_with_different_content(self):
        """Test override with different content."""
        with self.settings(
            MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_DIRECTORY=''
        ):
            # Create existing file with specific content
            existing_file_path = os.path.join(self.temp_media_dir, 'content_test.txt')
            original_content = b'original content line 1\noriginal content line 2'
            with open(existing_file_path, 'wb') as f:
                f.write(original_content)
            
            # Upload new file with different content and override
            new_content = b'new content line 1\nnew content line 2\nnew content line 3'
            uploaded_file = SimpleUploadedFile(
                "content_test.txt",
                new_content,
                content_type="text/plain"
            )
            
            response = self.client.post(reverse('fb_do_upload'), {
                'folder': '',
                'override': 'true',
                'Filedata': uploaded_file
            })
            
            self.assertEqual(response.status_code, 200)
            
            # Verify new content replaced old content
            with open(existing_file_path, 'rb') as f:
                file_content = f.read()
                self.assertEqual(file_content, new_content)
                self.assertNotEqual(file_content, original_content)
    
    @override_settings(MEDIA_ROOT=None)
    def test_upload_file_override_with_special_characters(self):
        """Test override with filenames containing special characters."""
        with self.settings(
            MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_DIRECTORY=''
        ):
            # Create existing file with special characters in name
            filename = "test file with spaces & special chars!.txt"
            # Note: convert_filename will convert this
            converted_name = filename.replace(' ', '_').lower()
            existing_file_path = os.path.join(self.temp_media_dir, converted_name)
            with open(existing_file_path, 'wb') as f:
                f.write(b'original')
            
            # Upload with override
            uploaded_file = SimpleUploadedFile(
                filename,
                b'new content',
                content_type="text/plain"
            )
            
            response = self.client.post(reverse('fb_do_upload'), {
                'folder': '',
                'override': 'true',
                'Filedata': uploaded_file
            })
            
            self.assertEqual(response.status_code, 200)
            
            # Verify file was replaced (filename will be converted)
            self.assertTrue(os.path.exists(existing_file_path))
            with open(existing_file_path, 'rb') as f:
                self.assertEqual(f.read(), b'new content')
    
    @override_settings(MEDIA_ROOT=None)
    def test_upload_file_override_various_override_values(self):
        """Test that various override parameter values work."""
        with self.settings(
            MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_DIRECTORY=''
        ):
            # Create existing file
            existing_file_path = os.path.join(self.temp_media_dir, 'override_test.txt')
            with open(existing_file_path, 'wb') as f:
                f.write(b'original')
            
            # Test various override values that should be treated as True
            for override_value in ['true', 'True', 'TRUE', '1', 'yes', 'Yes', 'YES', 'on', 'On', 'ON']:
                uploaded_file = SimpleUploadedFile(
                    "override_test.txt",
                    b'new content',
                    content_type="text/plain"
                )
                
                response = self.client.post(reverse('fb_do_upload'), {
                    'folder': '',
                    'override': override_value,
                    'Filedata': uploaded_file
                })
                
                self.assertEqual(response.status_code, 200, 
                               "Override value '%s' should be treated as True" % override_value)
                
                # Reset file for next iteration
                with open(existing_file_path, 'wb') as f:
                    f.write(b'original')
            
            # Test override values that should be treated as False
            for override_value in ['false', 'False', 'FALSE', '0', 'no', 'No', 'NO', 'off', 'Off', 'OFF', '']:
                uploaded_file = SimpleUploadedFile(
                    "override_test.txt",
                    b'should not replace',
                    content_type="text/plain"
                )
                
                response = self.client.post(reverse('fb_do_upload'), {
                    'folder': '',
                    'override': override_value,
                    'Filedata': uploaded_file
                })
                
                self.assertEqual(response.status_code, 400,
                               "Override value '%s' should be treated as False" % override_value)
    
    @override_settings(MEDIA_ROOT=None)  # Will be set dynamically
    def test_upload_file_endpoint_replace_existing(self):
        """Test _upload_file endpoint replacing existing file."""
        with self.settings(
            MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_DIRECTORY=''
        ):
            # Create existing file
            existing_file_path = os.path.join(self.temp_media_dir, 'replace_me.txt')
            with open(existing_file_path, 'w') as f:
                f.write('original content')
            
            # Upload new file with same name
            uploaded_file = SimpleUploadedFile(
                "replace_me.txt",
                b'new content',
                content_type="text/plain"
            )
            
            response = self.client.post(reverse('fb_do_upload'), {
                'folder': '',
                'Filedata': uploaded_file
            })
            
            self.assertEqual(response.status_code, 200)
            # Can be JSON or 'True' for backward compatibility
            response_text = response.content.decode()
            if response_text.startswith('{'):
                response_data = json.loads(response_text)
                self.assertTrue(response_data.get('success', False))
            else:
                self.assertEqual(response_text, 'True')


class FileOverrideTest(TestCase):
    """
    Unit tests for file override functionality.
    Tests the new override parameter and error handling.
    """
    
    def setUp(self):
        """Set up test environment with temp media directory and admin user."""
        # Create temporary media directory
        self.temp_media_dir = tempfile.mkdtemp()
        self.temp_filebrowser_dir = os.path.join(self.temp_media_dir, 'filebrowser')
        os.makedirs(self.temp_filebrowser_dir, exist_ok=True)
        
        # Create admin user for staff_member_required decorator
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='admin123',
            is_staff=True,
            is_superuser=True
        )
        
        # Create test client
        self.client = Client()
        self.client.login(username='admin', password='admin123')
        
        # Test file content
        self.test_file_content = b'Test file content for upload testing'
        self.new_file_content = b'New file content for override testing'
        
    def tearDown(self):
        """Clean up temporary media directory."""
        if os.path.exists(self.temp_media_dir):
            shutil.rmtree(self.temp_media_dir)
    
    @override_settings(MEDIA_ROOT=None)
    def test_upload_file_without_override_returns_error(self):
        """Test upload file when file exists and override is not set."""
        with self.settings(
            MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_DIRECTORY=''
        ):
            # Create existing file
            existing_file_path = os.path.join(self.temp_media_dir, 'existing.txt')
            with open(existing_file_path, 'wb') as f:
                f.write(self.test_file_content)
            
            # Upload new file with same name without override
            uploaded_file = SimpleUploadedFile(
                "existing.txt",
                self.new_file_content,
                content_type="text/plain"
            )
            
            response = self.client.post(reverse('fb_do_upload'), {
                'folder': '',
                'override': 'false',
                'Filedata': uploaded_file
            })
            
            # Should return 400 error
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response['Content-Type'], 'application/json')
            
            # Parse JSON error response
            response_data = json.loads(response.content.decode())
            self.assertEqual(response_data['error'], 'FILE_EXISTS')
            self.assertEqual(response_data['filename'], 'existing.txt')
            self.assertIn('message', response_data)
            
            # Verify file was NOT replaced
            with open(existing_file_path, 'rb') as f:
                self.assertEqual(f.read(), self.test_file_content)
    
    @override_settings(MEDIA_ROOT=None)
    def test_upload_file_with_override_replaces_file(self):
        """Test upload file when file exists and override is set."""
        with self.settings(
            MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_DIRECTORY=''
        ):
            # Create existing file
            existing_file_path = os.path.join(self.temp_media_dir, 'existing.txt')
            with open(existing_file_path, 'wb') as f:
                f.write(self.test_file_content)
            
            # Upload new file with same name with override
            uploaded_file = SimpleUploadedFile(
                "existing.txt",
                self.new_file_content,
                content_type="text/plain"
            )
            
            response = self.client.post(reverse('fb_do_upload'), {
                'folder': '',
                'override': 'true',
                'Filedata': uploaded_file
            })
            
            # Should return success
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response['Content-Type'], 'application/json')
            
            # Parse JSON success response
            response_data = json.loads(response.content.decode())
            self.assertTrue(response_data['success'])
            self.assertEqual(response_data['filename'], 'existing.txt')
            
            # Verify file content was replaced
            with open(existing_file_path, 'rb') as f:
                self.assertEqual(f.read(), self.new_file_content)
    
    @override_settings(MEDIA_ROOT=None)
    def test_upload_file_new_file_no_override_needed(self):
        """Test upload new file (doesn't exist) without override parameter."""
        with self.settings(
            MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_DIRECTORY=''
        ):
            # Upload new file
            uploaded_file = SimpleUploadedFile(
                "new_file.txt",
                self.test_file_content,
                content_type="text/plain"
            )
            
            response = self.client.post(reverse('fb_do_upload'), {
                'folder': '',
                'Filedata': uploaded_file
            })
            
            # Should return success
            self.assertEqual(response.status_code, 200)
            
            # Verify file was created
            uploaded_file_path = os.path.join(self.temp_media_dir, 'new_file.txt')
            self.assertTrue(os.path.exists(uploaded_file_path))
            
            # Verify file content
            with open(uploaded_file_path, 'rb') as f:
                self.assertEqual(f.read(), self.test_file_content)
    
    @override_settings(MEDIA_ROOT=None)
    def test_upload_file_error_response_format(self):
        """Test error response format is valid JSON."""
        with self.settings(
            MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_DIRECTORY=''
        ):
            # Create existing file
            existing_file_path = os.path.join(self.temp_media_dir, 'test.txt')
            with open(existing_file_path, 'wb') as f:
                f.write(b'existing')
            
            # Upload without override
            uploaded_file = SimpleUploadedFile(
                "test.txt",
                b'new',
                content_type="text/plain"
            )
            
            response = self.client.post(reverse('fb_do_upload'), {
                'folder': '',
                'Filedata': uploaded_file
            })
            
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response['Content-Type'], 'application/json')
            
            # Verify response is valid JSON
            response_data = json.loads(response.content.decode())
            self.assertIn('error', response_data)
            self.assertIn('filename', response_data)
            self.assertEqual(response_data['error'], 'FILE_EXISTS')
    
    @override_settings(MEDIA_ROOT=None)
    def test_upload_file_success_response_format(self):
        """Test success response format is valid JSON."""
        with self.settings(
            MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_DIRECTORY=''
        ):
            # Upload new file
            uploaded_file = SimpleUploadedFile(
                "success_test.txt",
                self.test_file_content,
                content_type="text/plain"
            )
            
            response = self.client.post(reverse('fb_do_upload'), {
                'folder': '',
                'Filedata': uploaded_file
            })
            
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response['Content-Type'], 'application/json')
            
            # Verify response is valid JSON
            response_data = json.loads(response.content.decode())
            self.assertIn('success', response_data)
            self.assertIn('filename', response_data)
            self.assertTrue(response_data['success'])
    
    @override_settings(MEDIA_ROOT=None)
    def test_upload_file_override_with_different_content(self):
        """Test override with different content."""
        with self.settings(
            MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_DIRECTORY=''
        ):
            # Create existing file with specific content
            existing_file_path = os.path.join(self.temp_media_dir, 'content_test.txt')
            original_content = b'original content line 1\noriginal content line 2'
            with open(existing_file_path, 'wb') as f:
                f.write(original_content)
            
            # Upload new file with different content and override
            new_content = b'new content line 1\nnew content line 2\nnew content line 3'
            uploaded_file = SimpleUploadedFile(
                "content_test.txt",
                new_content,
                content_type="text/plain"
            )
            
            response = self.client.post(reverse('fb_do_upload'), {
                'folder': '',
                'override': 'true',
                'Filedata': uploaded_file
            })
            
            self.assertEqual(response.status_code, 200)
            
            # Verify new content replaced old content
            with open(existing_file_path, 'rb') as f:
                file_content = f.read()
                self.assertEqual(file_content, new_content)
                self.assertNotEqual(file_content, original_content)
    
    @override_settings(MEDIA_ROOT=None)
    def test_upload_file_override_with_special_characters(self):
        """Test override with filenames containing special characters."""
        with self.settings(
            MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_DIRECTORY=''
        ):
            # Create existing file with special characters in name
            filename = "test file with spaces & special chars!.txt"
            # Note: convert_filename will convert this
            converted_name = filename.replace(' ', '_').lower()
            existing_file_path = os.path.join(self.temp_media_dir, converted_name)
            with open(existing_file_path, 'wb') as f:
                f.write(b'original')
            
            # Upload with override
            uploaded_file = SimpleUploadedFile(
                filename,
                b'new content',
                content_type="text/plain"
            )
            
            response = self.client.post(reverse('fb_do_upload'), {
                'folder': '',
                'override': 'true',
                'Filedata': uploaded_file
            })
            
            self.assertEqual(response.status_code, 200)
            
            # Verify file was replaced (filename will be converted)
            self.assertTrue(os.path.exists(existing_file_path))
            with open(existing_file_path, 'rb') as f:
                self.assertEqual(f.read(), b'new content')
    
    @override_settings(MEDIA_ROOT=None)
    def test_upload_file_override_various_override_values(self):
        """Test that various override parameter values work."""
        with self.settings(
            MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_DIRECTORY=''
        ):
            # Create existing file
            existing_file_path = os.path.join(self.temp_media_dir, 'override_test.txt')
            with open(existing_file_path, 'wb') as f:
                f.write(b'original')
            
            # Test various override values that should be treated as True
            for override_value in ['true', 'True', 'TRUE', '1', 'yes', 'Yes', 'YES', 'on', 'On', 'ON']:
                uploaded_file = SimpleUploadedFile(
                    "override_test.txt",
                    b'new content',
                    content_type="text/plain"
                )
                
                response = self.client.post(reverse('fb_do_upload'), {
                    'folder': '',
                    'override': override_value,
                    'Filedata': uploaded_file
                })
                
                self.assertEqual(response.status_code, 200, 
                               "Override value '%s' should be treated as True" % override_value)
                
                # Reset file for next iteration
                with open(existing_file_path, 'wb') as f:
                    f.write(b'original')
            
            # Test override values that should be treated as False
            for override_value in ['false', 'False', 'FALSE', '0', 'no', 'No', 'NO', 'off', 'Off', 'OFF', '']:
                uploaded_file = SimpleUploadedFile(
                    "override_test.txt",
                    b'should not replace',
                    content_type="text/plain"
                )
                
                response = self.client.post(reverse('fb_do_upload'), {
                    'folder': '',
                    'override': override_value,
                    'Filedata': uploaded_file
                })
                
                self.assertEqual(response.status_code, 400,
                               "Override value '%s' should be treated as False" % override_value)
            
            # Verify file content was replaced
            with open(existing_file_path, 'rb') as f:
                self.assertEqual(f.read(), b'new content')
    
    def test_check_file_endpoint_get_method(self):
        """Test _check_file endpoint with GET method (should still work)."""
        response = self.client.get(reverse('fb_check'))
        self.assertEqual(response.status_code, 200)
        
        # Should return empty JSON for GET requests
        response_data = json.loads(response.content.decode())
        self.assertEqual(response_data, {})
    
    def test_upload_file_endpoint_get_method(self):
        """Test _upload_file endpoint with GET method."""
        response = self.client.get(reverse('fb_do_upload'))
        self.assertEqual(response.status_code, 200)
        # Can be JSON or 'True' for backward compatibility
        response_text = response.content.decode()
        if response_text.startswith('{'):
            response_data = json.loads(response_text)
            self.assertTrue(response_data.get('success', False))
        else:
            self.assertEqual(response_text, 'True')
    
    def test_upload_endpoints_require_staff_permission(self):
        """Test that upload endpoints require staff permissions."""
        # Create regular user (non-staff)
        regular_user = User.objects.create_user(
            username='regular',
            email='regular@test.com',
            password='regular123',
            is_staff=False
        )
        
        # Test with regular user
        client = Client()
        client.login(username='regular', password='regular123')
        
        # Both endpoints should redirect to login (302) or return 403
        check_response = client.post(reverse('fb_check'))
        upload_response = client.post(reverse('fb_do_upload'))
        
        # Should redirect to login or return forbidden
        self.assertIn(check_response.status_code, [302, 403])
        self.assertIn(upload_response.status_code, [302, 403])
    
    def test_upload_endpoints_anonymous_user(self):
        """Test that upload endpoints require authentication."""
        # Test with anonymous user
        client = Client()
        
        # Both endpoints should redirect to login
        check_response = client.post(reverse('fb_check'))
        upload_response = client.post(reverse('fb_do_upload'))
        
        # Should redirect to login
        self.assertIn(check_response.status_code, [302, 403])
        self.assertIn(upload_response.status_code, [302, 403])


class UploadFilenameSanitizationTest(TestCase):
    """Test filename sanitization for Django 4/5 compatibility."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_media_dir = tempfile.mkdtemp()
        
        # Create admin user
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='admin123',
            is_staff=True,
            is_superuser=True
        )
        
        self.client = Client()
        self.client.login(username='admin', password='admin123')
    
    def tearDown(self):
        """Clean up temporary media directory."""
        if os.path.exists(self.temp_media_dir):
            shutil.rmtree(self.temp_media_dir)
    
    @override_settings(MEDIA_ROOT=None)
    def test_upload_file_with_special_characters(self):
        """Test uploading files with special characters in filename."""
        with self.settings(
            MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_DIRECTORY=''
        ):
            # Test file with special characters
            uploaded_file = SimpleUploadedFile(
                "test file with spaces & special chars!.txt",
                b'test content',
                content_type="text/plain"
            )
            
            response = self.client.post(reverse('fb_do_upload'), {
                'folder': '',
                'Filedata': uploaded_file
            })
            
            self.assertEqual(response.status_code, 200)
            # Can be JSON or 'True' for backward compatibility
            response_text = response.content.decode()
            if response_text.startswith('{'):
                response_data = json.loads(response_text)
                self.assertTrue(response_data.get('success', False))
            else:
                self.assertEqual(response_text, 'True')
    
    @override_settings(MEDIA_ROOT=None)
    def test_upload_file_with_unicode_characters(self):
        """Test uploading files with unicode characters in filename."""
        with self.settings(
            MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_DIRECTORY=''
        ):
            # Test file with unicode characters
            uploaded_file = SimpleUploadedFile(
                "test_файл_测试.txt",
                b'unicode test content',
                content_type="text/plain"
            )
            
            response = self.client.post(reverse('fb_do_upload'), {
                'folder': '',
                'Filedata': uploaded_file
            })
            
            self.assertEqual(response.status_code, 200)
            # Can be JSON or 'True' for backward compatibility
            response_text = response.content.decode()
            if response_text.startswith('{'):
                response_data = json.loads(response_text)
                self.assertTrue(response_data.get('success', False))
            else:
                self.assertEqual(response_text, 'True')


class FileOverrideTest(TestCase):
    """
    Unit tests for file override functionality.
    Tests the new override parameter and error handling.
    """
    
    def setUp(self):
        """Set up test environment with temp media directory and admin user."""
        # Create temporary media directory
        self.temp_media_dir = tempfile.mkdtemp()
        self.temp_filebrowser_dir = os.path.join(self.temp_media_dir, 'filebrowser')
        os.makedirs(self.temp_filebrowser_dir, exist_ok=True)
        
        # Create admin user for staff_member_required decorator
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='admin123',
            is_staff=True,
            is_superuser=True
        )
        
        # Create test client
        self.client = Client()
        self.client.login(username='admin', password='admin123')
        
        # Test file content
        self.test_file_content = b'Test file content for upload testing'
        self.new_file_content = b'New file content for override testing'
        
    def tearDown(self):
        """Clean up temporary media directory."""
        if os.path.exists(self.temp_media_dir):
            shutil.rmtree(self.temp_media_dir)
    
    @override_settings(MEDIA_ROOT=None)
    def test_upload_file_without_override_returns_error(self):
        """Test upload file when file exists and override is not set."""
        with self.settings(
            MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_DIRECTORY=''
        ):
            # Create existing file
            existing_file_path = os.path.join(self.temp_media_dir, 'existing.txt')
            with open(existing_file_path, 'wb') as f:
                f.write(self.test_file_content)
            
            # Upload new file with same name without override
            uploaded_file = SimpleUploadedFile(
                "existing.txt",
                self.new_file_content,
                content_type="text/plain"
            )
            
            response = self.client.post(reverse('fb_do_upload'), {
                'folder': '',
                'override': 'false',
                'Filedata': uploaded_file
            })
            
            # Should return 400 error
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response['Content-Type'], 'application/json')
            
            # Parse JSON error response
            response_data = json.loads(response.content.decode())
            self.assertEqual(response_data['error'], 'FILE_EXISTS')
            self.assertEqual(response_data['filename'], 'existing.txt')
            self.assertIn('message', response_data)
            
            # Verify file was NOT replaced
            with open(existing_file_path, 'rb') as f:
                self.assertEqual(f.read(), self.test_file_content)
    
    @override_settings(MEDIA_ROOT=None)
    def test_upload_file_with_override_replaces_file(self):
        """Test upload file when file exists and override is set."""
        with self.settings(
            MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_DIRECTORY=''
        ):
            # Create existing file
            existing_file_path = os.path.join(self.temp_media_dir, 'existing.txt')
            with open(existing_file_path, 'wb') as f:
                f.write(self.test_file_content)
            
            # Upload new file with same name with override
            uploaded_file = SimpleUploadedFile(
                "existing.txt",
                self.new_file_content,
                content_type="text/plain"
            )
            
            response = self.client.post(reverse('fb_do_upload'), {
                'folder': '',
                'override': 'true',
                'Filedata': uploaded_file
            })
            
            # Should return success
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response['Content-Type'], 'application/json')
            
            # Parse JSON success response
            response_data = json.loads(response.content.decode())
            self.assertTrue(response_data['success'])
            self.assertEqual(response_data['filename'], 'existing.txt')
            
            # Verify file content was replaced
            with open(existing_file_path, 'rb') as f:
                self.assertEqual(f.read(), self.new_file_content)
    
    @override_settings(MEDIA_ROOT=None)
    def test_upload_file_new_file_no_override_needed(self):
        """Test upload new file (doesn't exist) without override parameter."""
        with self.settings(
            MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_DIRECTORY=''
        ):
            # Upload new file
            uploaded_file = SimpleUploadedFile(
                "new_file.txt",
                self.test_file_content,
                content_type="text/plain"
            )
            
            response = self.client.post(reverse('fb_do_upload'), {
                'folder': '',
                'Filedata': uploaded_file
            })
            
            # Should return success
            self.assertEqual(response.status_code, 200)
            
            # Verify file was created
            uploaded_file_path = os.path.join(self.temp_media_dir, 'new_file.txt')
            self.assertTrue(os.path.exists(uploaded_file_path))
            
            # Verify file content
            with open(uploaded_file_path, 'rb') as f:
                self.assertEqual(f.read(), self.test_file_content)
    
    @override_settings(MEDIA_ROOT=None)
    def test_upload_file_error_response_format(self):
        """Test error response format is valid JSON."""
        with self.settings(
            MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_DIRECTORY=''
        ):
            # Create existing file
            existing_file_path = os.path.join(self.temp_media_dir, 'test.txt')
            with open(existing_file_path, 'wb') as f:
                f.write(b'existing')
            
            # Upload without override
            uploaded_file = SimpleUploadedFile(
                "test.txt",
                b'new',
                content_type="text/plain"
            )
            
            response = self.client.post(reverse('fb_do_upload'), {
                'folder': '',
                'Filedata': uploaded_file
            })
            
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response['Content-Type'], 'application/json')
            
            # Verify response is valid JSON
            response_data = json.loads(response.content.decode())
            self.assertIn('error', response_data)
            self.assertIn('filename', response_data)
            self.assertEqual(response_data['error'], 'FILE_EXISTS')
    
    @override_settings(MEDIA_ROOT=None)
    def test_upload_file_success_response_format(self):
        """Test success response format is valid JSON."""
        with self.settings(
            MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_DIRECTORY=''
        ):
            # Upload new file
            uploaded_file = SimpleUploadedFile(
                "success_test.txt",
                self.test_file_content,
                content_type="text/plain"
            )
            
            response = self.client.post(reverse('fb_do_upload'), {
                'folder': '',
                'Filedata': uploaded_file
            })
            
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response['Content-Type'], 'application/json')
            
            # Verify response is valid JSON
            response_data = json.loads(response.content.decode())
            self.assertIn('success', response_data)
            self.assertIn('filename', response_data)
            self.assertTrue(response_data['success'])
    
    @override_settings(MEDIA_ROOT=None)
    def test_upload_file_override_with_different_content(self):
        """Test override with different content."""
        with self.settings(
            MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_DIRECTORY=''
        ):
            # Create existing file with specific content
            existing_file_path = os.path.join(self.temp_media_dir, 'content_test.txt')
            original_content = b'original content line 1\noriginal content line 2'
            with open(existing_file_path, 'wb') as f:
                f.write(original_content)
            
            # Upload new file with different content and override
            new_content = b'new content line 1\nnew content line 2\nnew content line 3'
            uploaded_file = SimpleUploadedFile(
                "content_test.txt",
                new_content,
                content_type="text/plain"
            )
            
            response = self.client.post(reverse('fb_do_upload'), {
                'folder': '',
                'override': 'true',
                'Filedata': uploaded_file
            })
            
            self.assertEqual(response.status_code, 200)
            
            # Verify new content replaced old content
            with open(existing_file_path, 'rb') as f:
                file_content = f.read()
                self.assertEqual(file_content, new_content)
                self.assertNotEqual(file_content, original_content)
    
    @override_settings(MEDIA_ROOT=None)
    def test_upload_file_override_with_special_characters(self):
        """Test override with filenames containing special characters."""
        with self.settings(
            MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_DIRECTORY=''
        ):
            # Create existing file with special characters in name
            filename = "test file with spaces & special chars!.txt"
            # Note: convert_filename will convert this
            converted_name = filename.replace(' ', '_').lower()
            existing_file_path = os.path.join(self.temp_media_dir, converted_name)
            with open(existing_file_path, 'wb') as f:
                f.write(b'original')
            
            # Upload with override
            uploaded_file = SimpleUploadedFile(
                filename,
                b'new content',
                content_type="text/plain"
            )
            
            response = self.client.post(reverse('fb_do_upload'), {
                'folder': '',
                'override': 'true',
                'Filedata': uploaded_file
            })
            
            self.assertEqual(response.status_code, 200)
            
            # Verify file was replaced (filename will be converted)
            self.assertTrue(os.path.exists(existing_file_path))
            with open(existing_file_path, 'rb') as f:
                self.assertEqual(f.read(), b'new content')
    
    @override_settings(MEDIA_ROOT=None)
    def test_upload_file_override_various_override_values(self):
        """Test that various override parameter values work."""
        with self.settings(
            MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_DIRECTORY=''
        ):
            # Create existing file
            existing_file_path = os.path.join(self.temp_media_dir, 'override_test.txt')
            with open(existing_file_path, 'wb') as f:
                f.write(b'original')
            
            # Test various override values that should be treated as True
            for override_value in ['true', 'True', 'TRUE', '1', 'yes', 'Yes', 'YES', 'on', 'On', 'ON']:
                uploaded_file = SimpleUploadedFile(
                    "override_test.txt",
                    b'new content',
                    content_type="text/plain"
                )
                
                response = self.client.post(reverse('fb_do_upload'), {
                    'folder': '',
                    'override': override_value,
                    'Filedata': uploaded_file
                })
                
                self.assertEqual(response.status_code, 200, 
                               "Override value '%s' should be treated as True" % override_value)
                
                # Reset file for next iteration
                with open(existing_file_path, 'wb') as f:
                    f.write(b'original')
            
            # Test override values that should be treated as False
            for override_value in ['false', 'False', 'FALSE', '0', 'no', 'No', 'NO', 'off', 'Off', 'OFF', '']:
                uploaded_file = SimpleUploadedFile(
                    "override_test.txt",
                    b'should not replace',
                    content_type="text/plain"
                )
                
                response = self.client.post(reverse('fb_do_upload'), {
                    'folder': '',
                    'override': override_value,
                    'Filedata': uploaded_file
                })
                
                self.assertEqual(response.status_code, 400,
                               "Override value '%s' should be treated as False" % override_value)