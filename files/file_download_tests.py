from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from .forms import CustomUserCreationForm
from .models import UserFile
from .encryption import generate_key, encrypt_file, decrypt_file
import hashlib
import os

class FileDownloadTests(TestCase):
    def setUp(self):
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.upload_url = reverse('file_upload')
        self.download_url = reverse('file_download', args=[1])  # Replace 1 with a valid file ID
        self.user_data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password1': 'TestPassword123!',
            'password2': 'TestPassword123!',
        }

        self.user = get_user_model().objects.create_user(
            username=self.user_data['username'],
            email=self.user_data['email'],
            password=self.user_data['password1']
        )

        # Create a temporary file for testing upload and download
        test_file_content = b'Test file content'
        self.test_file = SimpleUploadedFile("test_file.txt", test_file_content)
        self.client = Client()
        self.client.login(username=self.user_data['username'], password=self.user_data['password1'])

    def test_file_download_integrity(self):
        # Upload a file
        response = self.client.post(self.upload_url, {'file': self.test_file})
        self.assertEqual(response.status_code, 302)  # Check for successful file upload

        # Get the UserFile model for the uploaded file
        user_file = UserFile.objects.first()
        file_id = user_file.id

        # Download the file
        response = self.client.get(reverse('file_download', args=[file_id]))

        # Check if the file was downloaded successfully
        self.assertEqual(response.status_code, 200)

        # Check file integrity
        sha256_hash = hashlib.sha256(response.content).hexdigest()
        self.assertEqual(sha256_hash, user_file.file_hash)

    def test_user_can_download_own_file(self):
        # Upload a file
        response = self.client.post(self.upload_url, {'file': self.test_file})
        self.assertEqual(response.status_code, 302)  # Check for successful file upload

        # Get the UserFile model for the uploaded file
        user_file = UserFile.objects.first()
        file_id = user_file.id

        # Log in the user
        self.client.login(username=self.user_data['username'], password=self.user_data['password1'])

        # Download the file
        response = self.client.get(reverse('file_download', args=[file_id]))

        # Check if the file was downloaded successfully
        self.assertEqual(response.status_code, 200)

    def test_unauthorized_user_cannot_download_file(self):
        # Upload a file
        response = self.client.post(self.upload_url, {'file': self.test_file})
        self.assertEqual(response.status_code, 302)  # Check for successful file upload

        # Get the UserFile model for the uploaded file
        user_file = UserFile.objects.first()
        file_id = user_file.id

        # Create a new user who is not the owner of the file
        new_user_data = {
            'username': 'anotheruser',
            'email': 'anotheruser@example.com',
            'password1': 'AnotherPassword123!',
            'password2': 'AnotherPassword123!',
        }
        new_user = get_user_model().objects.create_user(
            username=new_user_data['username'],
            email=new_user_data['email'],
            password=new_user_data['password1']
        )

        # Log in the new user
        self.client.login(username=new_user_data['username'], password=new_user_data['password1'])

        # Attempt to download the file as the new user
        response = self.client.get(reverse('file_download', args=[file_id]))

        # Check if the download is forbidden for an unauthorized user
        self.assertEqual(response.status_code, 404)
