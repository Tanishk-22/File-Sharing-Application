from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseForbidden, Http404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from .models import UserFile
from .forms import FileUploadForm
from .encryption import encrypt_file, decrypt_file, generate_key
from cryptography.fernet import Fernet
import hashlib




#  File_upload is now done at dashboard this section is defunct but kept for modularity if another place can upload.
@login_required
def file_upload(request):
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
            # Need to save this key
            user_file.encryption_key = key
            user_file.save()

            file_path = user_file.file.path
            encrypt_file(file_path, key)

            return redirect('user_dashboard')  # Redirect to Dashboard

        form = FileUploadForm()
    return render(request, 'file_upload.html', {'form': form})


@login_required
def file_download(request, file_id):
    # checking the file if it is owned by the user or if the file is shared with the user
    user_file = get_object_or_404(UserFile,
                                  Q(id=file_id),
                                  Q(user=request.user) | Q(shared_with=request.user))
    file_path = user_file.file.path
    key = user_file.encryption_key
    print(f"Encryption key at download: {key}")  # Debug
    # Decrypt the file temporarily for download
    decrypt_file(file_path, key)

    # Verify file hash
    with open(file_path, 'rb') as file:
        file_content = file.read()
        sha256_hash = hashlib.sha256(file_content).hexdigest()
        if sha256_hash != user_file.file_hash:
            # Re-encrypt the file before raising error
            encrypt_file(file_path, key)
            print(f"Encryption key at Hash: {key}")  # Debug
            # Raise an error or return a forbidden response
            return HttpResponseForbidden("File integrity check failed. Download aborted.")

    with open(file_path, 'rb') as file:
        response = HttpResponse(file.read(), content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{user_file.file.name}"'

    # Re-encrypt the file after download
    print(f"Encryption key after download: {key}")  # Debug
    encrypt_file(file_path, key)

    return response


@login_required
def file_share(request, file_id):
    user_file = get_object_or_404(UserFile, id=file_id, user=request.user)
    users = User.objects.exclude(id=request.user.id)  # Get all users except the current user

    if request.method == 'POST':
        selected_user_ids = request.POST.getlist('users')
        for user_id in selected_user_ids:
            shared_user = User.objects.get(id=user_id)
            user_file.shared_with.add(shared_user)
        return redirect('user_dashboard')  # Redirect after sharing

    return render(request, 'file_share.html', {'users': users, 'file': user_file})


@login_required
def file_delete(request, file_id):
    if request.method == 'POST':
        user_file = get_object_or_404(UserFile, id=file_id, user=request.user)
        user_file.delete()
        print(f"Deleting record only not file on pc for security.")  # Debug
    return redirect('user_dashboard')  # Redirect back to the dashboard
