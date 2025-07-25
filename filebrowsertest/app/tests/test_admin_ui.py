import os
import tempfile
import shutil
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test.utils import override_settings
from django.conf import settings


class AdminUITest(TestCase):
    """
    Tests for admin UI functionality to verify Django 4/5 compatibility.
    These tests verify that the filebrowser admin interface works correctly.
    """
    
    def setUp(self):
        """Set up test environment with temp media directory and admin user."""
        # Create temporary media directory
        self.temp_media_dir = tempfile.mkdtemp()
        self.temp_filebrowser_dir = os.path.join(self.temp_media_dir, 'filebrowser')
        os.makedirs(self.temp_filebrowser_dir, exist_ok=True)
        
        # Create some test files for browsing
        self.create_test_files()
        
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
        
    def create_test_files(self):
        """Create some test files for testing browse functionality."""
        # Create a test image file (stub)
        test_image_path = os.path.join(self.temp_media_dir, 'test_image.jpg')
        with open(test_image_path, 'wb') as f:
            f.write(b'fake image data')
        
        # Create a test text file
        test_text_path = os.path.join(self.temp_media_dir, 'test_document.txt')
        with open(test_text_path, 'w') as f:
            f.write('test document content')
        
        # Create a subdirectory with files
        subdir_path = os.path.join(self.temp_media_dir, 'subdirectory')
        os.makedirs(subdir_path, exist_ok=True)
        
        sub_file_path = os.path.join(subdir_path, 'sub_file.txt')
        with open(sub_file_path, 'w') as f:
            f.write('subdirectory file content')
        
    def tearDown(self):
        """Clean up temporary media directory."""
        if os.path.exists(self.temp_media_dir):
            shutil.rmtree(self.temp_media_dir)
    
    @override_settings(MEDIA_ROOT=None)
    def test_browse_view_renders(self):
        """Test that the main browse view renders without errors."""
        with self.settings(
            MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_DIRECTORY=''
        ):
            response = self.client.get(reverse('fb_browse'))
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, 'FileBrowser')
            
            # Check that test files appear in the listing
            self.assertContains(response, 'test_image.jpg')
            self.assertContains(response, 'test_document.txt')
            self.assertContains(response, 'subdirectory')
    
    @override_settings(MEDIA_ROOT=None)
    def test_browse_view_with_subdirectory(self):
        """Test browsing into a subdirectory."""
        with self.settings(
            MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_DIRECTORY=''
        ):
            response = self.client.get(reverse('fb_browse'), {'dir': 'subdirectory'})
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, 'sub_file.txt')
    
    @override_settings(MEDIA_ROOT=None)
    def test_browse_view_nonexistent_directory(self):
        """Test browsing to a non-existent directory."""
        with self.settings(
            MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_DIRECTORY=''
        ):
            response = self.client.get(reverse('fb_browse'), {'dir': 'nonexistent'})
            # Should redirect back to root with error message
            self.assertEqual(response.status_code, 302)
    
    @override_settings(MEDIA_ROOT=None)
    def test_upload_view_renders(self):
        """Test that the upload view renders without errors."""
        with self.settings(
            MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_DIRECTORY=''
        ):
            response = self.client.get(reverse('fb_upload'))
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, 'Select files to upload')
    
    @override_settings(MEDIA_ROOT=None)
    def test_mkdir_view_get(self):
        """Test that the mkdir view renders the form."""
        with self.settings(
            MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_DIRECTORY=''
        ):
            response = self.client.get(reverse('fb_mkdir'))
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, 'New Folder')
    
    @override_settings(MEDIA_ROOT=None)
    def test_mkdir_view_post_valid(self):
        """Test creating a new directory."""
        with self.settings(
            MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_DIRECTORY=''
        ):
            response = self.client.post(reverse('fb_mkdir'), {
                'dir_name': 'new_test_folder'
            })
            
            # Should redirect after successful creation
            self.assertEqual(response.status_code, 302)
            
            # Verify directory was created
            new_dir_path = os.path.join(self.temp_media_dir, 'new_test_folder')
            self.assertTrue(os.path.exists(new_dir_path))
            self.assertTrue(os.path.isdir(new_dir_path))
    
    @override_settings(MEDIA_ROOT=None)
    def test_mkdir_view_post_invalid_name(self):
        """Test creating directory with invalid name."""
        with self.settings(
            MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_DIRECTORY=''
        ):
            # Try to create directory with invalid name (e.g., containing ..)
            response = self.client.post(reverse('fb_mkdir'), {
                'dir_name': '../escape_attempt'
            })
            
            # Should return form with errors
            self.assertEqual(response.status_code, 200)
    
    @override_settings(MEDIA_ROOT=None)
    def test_rename_view_get(self):
        """Test that the rename view renders the form."""
        with self.settings(
            MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_DIRECTORY=''
        ):
            response = self.client.get(reverse('fb_rename'), {
                'filename': 'test_document.txt'
            })
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, 'Rename')
    
    @override_settings(MEDIA_ROOT=None)
    def test_rename_view_post_valid(self):
        """Test renaming a file."""
        with self.settings(
            MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_DIRECTORY=''
        ):
            response = self.client.post(reverse('fb_rename'), {
                'filename': 'test_document.txt',
                'name': 'renamed_document'
            })
            
            # Should redirect after successful rename
            self.assertEqual(response.status_code, 302)
            
            # Verify file was renamed
            old_path = os.path.join(self.temp_media_dir, 'test_document.txt')
            new_path = os.path.join(self.temp_media_dir, 'renamed_document.txt')
            
            self.assertFalse(os.path.exists(old_path))
            self.assertTrue(os.path.exists(new_path))
    
    @override_settings(MEDIA_ROOT=None)
    def test_delete_view_file(self):
        """Test deleting a file."""
        with self.settings(
            MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_DIRECTORY=''
        ):
            # Verify file exists first
            file_path = os.path.join(self.temp_media_dir, 'test_document.txt')
            self.assertTrue(os.path.exists(file_path))
            
            response = self.client.get(reverse('fb_delete'), {
                'filename': 'test_document.txt',
                'filetype': 'Document'
            })
            
            # Should redirect after successful deletion
            self.assertEqual(response.status_code, 302)
            
            # Verify file was deleted
            self.assertFalse(os.path.exists(file_path))
    
    @override_settings(MEDIA_ROOT=None)
    def test_delete_view_empty_folder(self):
        """Test deleting an empty folder."""
        with self.settings(
            MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_DIRECTORY=''
        ):
            # Create empty folder
            empty_folder_path = os.path.join(self.temp_media_dir, 'empty_folder')
            os.makedirs(empty_folder_path)
            
            response = self.client.get(reverse('fb_delete'), {
                'filename': 'empty_folder',
                'filetype': 'Folder'
            })
            
            # Should redirect after successful deletion
            self.assertEqual(response.status_code, 302)
            
            # Verify folder was deleted
            self.assertFalse(os.path.exists(empty_folder_path))
    
    @override_settings(MEDIA_ROOT=None)
    def test_versions_view(self):
        """Test the versions view for an image."""
        with self.settings(
            MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_DIRECTORY=''
        ):
            response = self.client.get(reverse('fb_versions'), {
                'filename': 'test_image.jpg'
            })
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, 'Versions for')
    
    def test_admin_ui_requires_staff_permission(self):
        """Test that admin UI views require staff permissions."""
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
        
        # All admin views should redirect to login or return 403
        views_to_test = ['fb_browse', 'fb_upload', 'fb_mkdir', 'fb_rename', 'fb_delete', 'fb_versions']
        
        for view_name in views_to_test:
            response = client.get(reverse(view_name))
            self.assertIn(response.status_code, [302, 403], 
                         f"View {view_name} should require staff permission")
    
    def test_admin_ui_anonymous_user(self):
        """Test that admin UI views require authentication."""
        # Test with anonymous user
        client = Client()
        
        # All admin views should redirect to login
        views_to_test = ['fb_browse', 'fb_upload', 'fb_mkdir', 'fb_rename', 'fb_delete', 'fb_versions']
        
        for view_name in views_to_test:
            response = client.get(reverse(view_name))
            self.assertIn(response.status_code, [302, 403], 
                         f"View {view_name} should require authentication")
    
    @override_settings(MEDIA_ROOT=None)
    def test_browse_view_filtering(self):
        """Test file filtering functionality in browse view."""
        with self.settings(
            MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_DIRECTORY=''
        ):
            # Test filtering by file type
            response = self.client.get(reverse('fb_browse'), {
                'filter_type': 'Document'
            })
            self.assertEqual(response.status_code, 200)
            
            # Test search functionality
            response = self.client.get(reverse('fb_browse'), {
                'q': 'test'
            })
            self.assertEqual(response.status_code, 200)
    
    @override_settings(MEDIA_ROOT=None)
    def test_browse_view_sorting(self):
        """Test file sorting functionality in browse view."""
        with self.settings(
            MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_DIRECTORY=''
        ):
            # Test sorting by name
            response = self.client.get(reverse('fb_browse'), {
                'o': 'filename',
                'ot': 'asc'
            })
            self.assertEqual(response.status_code, 200)
            
            # Test sorting by date
            response = self.client.get(reverse('fb_browse'), {
                'o': 'date',
                'ot': 'desc'
            })
            self.assertEqual(response.status_code, 200)
    
    @override_settings(MEDIA_ROOT=None)
    def test_browse_view_pagination(self):
        """Test pagination in browse view."""
        with self.settings(
            MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_MEDIA_ROOT=self.temp_media_dir,
            FILEBROWSER_DIRECTORY='',
            LIST_PER_PAGE=1  # Force pagination
        ):
            # Create additional test files to trigger pagination
            for i in range(5):
                test_file_path = os.path.join(self.temp_media_dir, f'paginate_test_{i}.txt')
                with open(test_file_path, 'w') as f:
                    f.write(f'pagination test file {i}')
            
            # Test first page
            response = self.client.get(reverse('fb_browse'), {'p': '1'})
            self.assertEqual(response.status_code, 200)
            
            # Test second page
            response = self.client.get(reverse('fb_browse'), {'p': '2'})
            self.assertEqual(response.status_code, 200)