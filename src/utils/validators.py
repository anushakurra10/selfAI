import re

def is_valid_email(email):
    return re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email) is not None

def is_valid_phone(phone):
    return re.match(r"^\+?\d[\d\- ]{7,15}$", phone) is not None

def is_malicious( text):
    return any(bad in text.lower() for bad in ["eval", "exec", "subprocess", "os.system", "rm -rf", "curl", "wget"])


