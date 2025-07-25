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
                'folder': '/filebrowser/',
                'testfile': 'nonexistent.txt'
            })
            
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8')
            
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
                'folder': '/filebrowser/',
                'testfile': 'existing.txt'
            })
            
            self.assertEqual(response.status_code, 200)
            
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
                'folder': '/filebrowser/',
                'Filedata': uploaded_file
            })
            
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.content.decode(), 'True')
            
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
            self.assertEqual(response.content.decode(), 'True')
    
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
                'folder': '/filebrowser/',
                'Filedata': uploaded_file
            })
            
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.content.decode(), 'True')
            
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
        self.assertEqual(response.content.decode(), 'True')
    
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
                'folder': '/filebrowser/',
                'Filedata': uploaded_file
            })
            
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.content.decode(), 'True')
    
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
                'folder': '/filebrowser/',
                'Filedata': uploaded_file
            })
            
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.content.decode(), 'True')