from cryptography.fernet import Fernet
from dotenv import load_dotenv
import os

load_dotenv()
SECRET_KEY = os.getenv("ENCRYPTION_KEY")

# Encrypt the original number
def encrypt_number(original_number):
    cipher_suite = Fernet(SECRET_KEY.encode())
    encrypted_number = cipher_suite.encrypt(str(original_number).encode())
    return encrypted_number

# Decrypt the unique ID to retrieve the original number
def decrypt_number(unique_id):
    cipher_suite = Fernet(SECRET_KEY.encode())
    decrypted_number = cipher_suite.decrypt(unique_id).decode()
    return int(decrypted_number)


if __name__ == "__main__":
    original_number = int(input("Enter a number: "))
    unique_id = encrypt_number(original_number)
    print(f"Unique ID: {unique_id.decode()}")
    
    encrypted_number = input("Enter the unique ID to retrieve the original number: ").encode()
    original_number_retrieved = decrypt_number(encrypted_number)
    print(f"Original Number Retrieved: {original_number_retrieved}")