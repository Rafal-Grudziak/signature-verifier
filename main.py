import os
import tkinter as tk
import random
from tkinter import messagebox, filedialog
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from trng import generate_random_bits_from_images

# Ścieżki do plików z kluczami
private_key_path = 'private_key.pem'
public_key_path = 'public_key.pem'

image_folder = "photo_dump"
num_needed = 3000


# Funkcja generująca parę kluczy RSA i zapisująca je w plikach
def generate_and_save_rsa_keypair(private_key_path, public_key_path):
    random_bits = generate_random_bits_from_images(image_folder, num_needed)
    random_seed = int("".join(map(str, random_bits)), 2)
    random.seed(random_seed)

    key = RSA.generate(2048)
    private_key = key.export_key()
    public_key = key.publickey().export_key()

    with open(private_key_path, 'wb') as priv_file:
        priv_file.write(private_key)

    with open(public_key_path, 'wb') as pub_file:
        pub_file.write(public_key)


# Funkcja wczytująca klucz z pliku
def load_key(file_path):
    with open(file_path, 'rb') as file:
        key = file.read()
    return key


# Funkcja podpisująca zawartość pliku
def sign_file(file_path, private_key):
    with open(file_path, 'rb') as file:
        data = file.read()
        key = RSA.import_key(private_key)
        h = SHA256.new(data)
        signature = pkcs1_15.new(key).sign(h)

    # Zapisanie podpisu w tym samym katalogu z tą samą nazwą i różnym rozszerzeniem
    signature_file_path = f"{os.path.splitext(file_path)[0]}.sig"
    with open(signature_file_path, 'wb') as sig_file:
        sig_file.write(signature)

    return signature_file_path


# Funkcja weryfikująca podpis pliku
def verify_file_signature(file_path, public_key, signature_file_path):
    with open(file_path, 'rb') as file:
        data = file.read()
        key = RSA.import_key(public_key)
        h = SHA256.new(data)

    if not os.path.exists(signature_file_path):
        return False

    with open(signature_file_path, 'rb') as sig_file:
        signature = sig_file.read()

    try:
        pkcs1_15.new(key).verify(h, signature)
        return True
    except (ValueError, TypeError):
        return False


# Sprawdzanie, czy klucze już istnieją
if not os.path.exists(private_key_path) or not os.path.exists(public_key_path):
    generate_and_save_rsa_keypair(private_key_path, public_key_path)
    print("Generated new RSA key pair and saved to files.")
else:
    print("RSA key pair already exists. Using existing keys.")

# Wczytywanie kluczy
private_key = load_key(private_key_path)
public_key = load_key(public_key_path)


# GUI
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("RSA Digital Signature")
        self.root.geometry('525x450')
        self.create_widgets()

    def create_widgets(self):
        self.frame = tk.Frame(self.root, padx=10, pady=10)
        self.frame.pack(expand=True, fill=tk.BOTH, padx=0, pady=0, ipadx=10)


        self.title_label = tk.Label(self.frame, text="RSA Digital Signature Tool", font=('Helvetica', 16, 'bold'))
        self.title_label.grid(row=0, column=0, columnspan=3, pady=20)

        # Inputy do podpisywania pliku
        self.sign_file_label = tk.Label(self.frame, text="File to Sign:", font=('Helvetica', 12))
        self.sign_file_label.grid(row=1, column=0, pady=10)

        self.sign_file_entry = tk.Entry(self.frame, width=50)
        self.sign_file_entry.grid(row=1, column=1, pady=10)

        self.browse_sign_file_button = tk.Button(self.frame, text="Browse", command=self.browse_sign_file, width=10)
        self.browse_sign_file_button.grid(row=1, column=2, pady=10)

        self.sign_button = tk.Button(self.frame, text="Sign File", command=self.sign_file, width=20)
        self.sign_button.grid(row=2, column=0, columnspan=3, padx=10, pady=10)

        # Pionowa linia oddzielająca sekcje
        self.separator = tk.Frame(self.frame, height=2, bd=1, relief=tk.SUNKEN)
        self.separator.grid(row=3, columnspan=3, sticky='ew', padx=10, pady=10)

        # Inputy do weryfikacji pliku
        self.verify_file_label = tk.Label(self.frame, text="File to Verify:", font=('Helvetica', 12))
        self.verify_file_label.grid(row=4, column=0, pady=10)

        self.verify_file_entry = tk.Entry(self.frame, width=50)
        self.verify_file_entry.grid(row=4, column=1, pady=10)

        self.browse_verify_file_button = tk.Button(self.frame, text="Browse", command=self.browse_verify_file, width=10)
        self.browse_verify_file_button.grid(row=4, column=2, pady=10)

        self.signature_file_label = tk.Label(self.frame, text="Signature File:", font=('Helvetica', 12))
        self.signature_file_label.grid(row=5, column=0, pady=10)

        self.signature_file_entry = tk.Entry(self.frame, width=50)
        self.signature_file_entry.grid(row=5, column=1, pady=10)

        self.browse_signature_file_button = tk.Button(self.frame, text="Browse", command=self.browse_signature_file, width=10)
        self.browse_signature_file_button.grid(row=5, column=2, pady=10)

        self.public_key_label = tk.Label(self.frame, text="Public Key File:", font=('Helvetica', 12))
        self.public_key_label.grid(row=6, column=0, pady=10)

        self.public_key_entry = tk.Entry(self.frame, width=50)
        self.public_key_entry.grid(row=6, column=1, pady=10)

        self.browse_public_key_button = tk.Button(self.frame, text="Browse", command=self.browse_public_key, width=10)
        self.browse_public_key_button.grid(row=6, column=2, pady=10)

        self.verify_button = tk.Button(self.frame, text="Verify Signature", command=self.verify_signature, width=20)
        self.verify_button.grid(row=7, column=0, columnspan=3, padx=10, pady=10)

        self.exit_button = tk.Button(self.frame, text="Exit", command=self.root.quit, width=40)
        self.exit_button.grid(row=8, column=0, columnspan=3, pady=20)

    def browse_sign_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.sign_file_entry.delete(0, tk.END)
            self.sign_file_entry.insert(0, file_path)

    def browse_verify_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.verify_file_entry.delete(0, tk.END)
            self.verify_file_entry.insert(0, file_path)

    def browse_signature_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.signature_file_entry.delete(0, tk.END)
            self.signature_file_entry.insert(0, file_path)

    def browse_public_key(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.public_key_entry.delete(0, tk.END)
            self.public_key_entry.insert(0, file_path)

    def sign_file(self):
        file_path = self.sign_file_entry.get()
        if file_path:
            signature_file_path = sign_file(file_path, private_key)
            messagebox.showinfo("Success", f"File signed successfully. Signature saved as {signature_file_path}.")

    def verify_signature(self):
        public_key_path = self.public_key_entry.get()
        if not public_key_path:
            messagebox.showerror("Error", "Please select the public key file.")
            return

        signature_file_path = self.signature_file_entry.get()
        if not signature_file_path:
            messagebox.showerror("Error", "Please select the signature file.")
            return

        file_path = self.verify_file_entry.get()
        if not file_path:
            messagebox.showerror("Error", "Please select the file to verify.")
            return

        public_key = load_key(public_key_path)
        is_valid = verify_file_signature(file_path, public_key, signature_file_path)
        if is_valid:
            messagebox.showinfo("Result", "The file is valid.")
        else:
            messagebox.showerror("Result", "The file is not valid.")



# Uruchomienie aplikacji
root = tk.Tk()
app = App(root)
root.mainloop()
