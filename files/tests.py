from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from .forms import CustomUserCreationForm
from .file_download_tests import FileDownloadTests
from .file_upload_tests import FileUploadTests


class UserRegistrationTests(TestCase):
    def setUp(self):
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.user_data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password1': 'TestPassword123!',
            'password2': 'TestPassword123!',
        }

        super().setUp();

    def test_user_registration_view(self):
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/register.html')

    def test_user_registration(self):
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, 302)  # Check for successful registration
        self.assertRedirects(response, self.login_url)

        # Check if the user is created
        self.assertTrue(get_user_model().objects.filter(username='testuser').exists())

    def test_invalid_user_registration(self):
        # Test registration with invalid data
        invalid_user_data = {
            'username': 'testuser',
            'email': 'invalidemail',  # Invalid email format
            'password1': 'TestPassword123!',
            'password2': 'DifferentPassword123!',  # Different password
        }

        response = self.client.post(self.register_url, invalid_user_data)
        self.assertEqual(response.status_code, 200)  # Registration form should be re-rendered
        self.assertFormError(response, 'form', 'email', 'Enter a valid email address.')
        expected_error_message = "The two password fields didn’t match."
        self.assertFormError(response, 'form', 'password2', expected_error_message)

    def test_user_registration_form(self):
        # Test the form itself
        form = CustomUserCreationForm(data=self.user_data)
        self.assertTrue(form.is_valid())

        # Test with invalid data
        invalid_user_data = {
            'username': 'testuser',
            'email': 'invalidemail',  # Invalid email format
            'password1': 'TestPassword123!',
            'password2': 'DifferentPassword123!',  # Different password
        }
        invalid_form = CustomUserCreationForm(data=invalid_user_data)
        self.assertFalse(invalid_form.is_valid())
        self.assertEqual(invalid_form.errors['email'][0], 'Enter a valid email address.')
        expected_error_message = "The two password fields didn’t match."
        self.assertEqual(invalid_form.errors['password2'][0], expected_error_message)

