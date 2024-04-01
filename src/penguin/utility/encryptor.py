from cryptography.fernet import Fernet


class Encryptor():
    def key_create(self):
        key = Fernet.generate_key()
        return key

    def key_write(self, key, key_name):
        with open(key_name, 'wb') as mykey:
            mykey.write(key)

    def key_load(self, key_name):
        with open(key_name, 'rb') as mykey:
            key = mykey.read()
        return key

    def file_encrypt(self, key, original_file, encrypted_file):

        f = Fernet(key)

        with open(original_file, 'rb') as file:
            original = file.read()

        encrypted = f.encrypt(original)

        with open(encrypted_file, 'wb') as file:
            file.write(encrypted)

    def file_decrypt(self, key, encrypted_file, decrypted_file):
        f = Fernet(key)

        with open(encrypted_file, 'rb') as file:
            encrypted = file.read()

        decrypted = f.decrypt(encrypted)

        with open(decrypted_file, 'wb') as file:
            file.write(decrypted)

    def encrypt(self, key, textdata: str):
        f = Fernet(key)
        encrypt_data = f.encrypt(textdata)
        return encrypt_data

    def decrypt(self, key, encrypt_data: str):
        f = Fernet(key)
        textdata = f.decrypt(encrypt_data)
        return textdata


def unlock():
    enc = Encryptor()

    key = enc.key_load("penguin_lock")
    enc.file_decrypt(key,
                     "src/penguin/utility/xyz.pdf.locked"
                     "src/penguin/utility/xyz.pdf")


def lock():
    enc = Encryptor()

    key = enc.key_load("penguin_lock")
    enc.file_encrypt(key,
                     "src/penguin/utility/xyz.pdf"
                     "src/penguin/utility/xyz.pdf.locked")


def create_key():
    enc = Encryptor()
    key = enc.key_create()
    enc.key_write(key, "penguin_lock")


if __name__ == "__main__":

    enc = Encryptor()
    key = enc.key_load("penguin_lock")
    edata = enc.encrypt(key,
                         "Ashok Sharma")
    print(edata)

