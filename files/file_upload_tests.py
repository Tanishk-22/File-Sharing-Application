from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from files.models import UserFile
from files.forms import FileUploadForm
from files.encryption import generate_key, encrypt_file, decrypt_file
import hashlib
import os

class FileUploadTests(TestCase):
    def setUp(self):
        self.upload_url = reverse('file_upload')
        self.user_data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'TestPassword123!',
        }
        self.user = get_user_model().objects.create_user(
            username=self.user_data['username'],
            email=self.user_data['email'],
            password=self.user_data['password']
        )
        self.client = Client()
        self.client.login(username=self.user_data['username'], password=self.user_data['password'])

    def test_file_upload_authenticated_user(self):
        # Create a temporary file for testing
        test_file_content = b'Test file content'
        test_file_path = 'test_file.txt'
        with open(test_file_path, 'wb') as test_file:
            test_file.write(test_file_content)

        with open(test_file_path, 'rb') as file:
            file_hash = hashlib.sha256(file.read()).hexdigest()

        with open(test_file_path, 'rb') as file:
            form_data = {'file': file}
            response = self.client.post(self.upload_url, form_data)

        # Check if the file was uploaded successfully
        self.assertEqual(response.status_code, 302)  # Check for successful file upload

        # Check if the UserFile model was created
        self.assertTrue(UserFile.objects.filter(user=self.user, file_hash=file_hash).exists())

        # Check if the file is encrypted and stored with the correct encryption key
        user_file = UserFile.objects.get(user=self.user, file_hash=file_hash)
        encrypted_file_path = user_file.file.path
        encrypted_key = user_file.encryption_key
        self.assertNotEqual(encrypted_key, None)  # Check if encryption key is generated

        # Decrypt the file to check its content
        decrypt_file(encrypted_file_path, encrypted_key)
        with open(encrypted_file_path, 'rb') as decrypted_file:
            decrypted_content = decrypted_file.read()

        # Check if the decrypted content matches the original content
        self.assertEqual(decrypted_content, test_file_content)

        # Clean up: Delete the temporary file and the UserFile model
        os.remove(test_file_path)
        user_file.delete()
