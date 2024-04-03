from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm
from files.models import UserFile
from files.forms import FileUploadForm
from files.encryption import encrypt_file, decrypt_file, generate_key
import hashlib


# Using Django authenication for security
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            print(f"User Created")  # Debug
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})


def users_page(request):
    return render(request, 'users_page.html')

#  File upload is now done at dashboard
@login_required
def user_dashboard(request):
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            user_file = form.save(commit=False)
            user_file.user = request.user
            user_file.save()

            # Hashing the file
            file_content = user_file.file.read()
            sha256_hash = hashlib.sha256(file_content).hexdigest()
            user_file.file_hash = sha256_hash  # Store the hash
            user_file.save()

            # Encrypt the file
            key = generate_key()
            print(f"Encryption key at generation: {key}")  # Debug
            # Need to save this key
            user_file.encryption_key = key
            user_file.save()
            print(f"Encryption key at upload: {user_file.encryption_key}")  # Debug

            file_path = user_file.file.path
            encrypt_file(file_path, key)

            return redirect('user_dashboard')
    else:
        form = FileUploadForm()

    user_files = UserFile.objects.filter(user=request.user)  # Retrieve user's files
    shared_files = UserFile.objects.filter(shared_with=request.user)
    return render(request, 'users/user_dashboard.html', {'form': form, 'user_files': user_files,
                                                         'shared_files': shared_files})
