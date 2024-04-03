from cryptography.fernet import Fernet


def generate_key():
    return Fernet.generate_key()


def encrypt_file(file_path, key):
    fernet = Fernet(key)
    with open(file_path, 'rb') as file:
        original_file_data = file.read()
    encrypted_data = fernet.encrypt(original_file_data)
    with open(file_path, 'wb') as encrypted_file:
        encrypted_file.write(encrypted_data)


def decrypt_file(file_path, key):
    fernet = Fernet(key)
    with open(file_path, 'rb') as encrypted_file:
        encrypted_data = encrypted_file.read()
    decrypted_data = fernet.decrypt(encrypted_data)
    with open(file_path, 'wb') as decrypted_file:
        decrypted_file.write(decrypted_data)
