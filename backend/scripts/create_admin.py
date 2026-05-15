import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.auth import create_user

def create_admin():
    email = "haytameelatraoui@gmail.com"
    password = "Haytame123@"
    first_name = "Haytame"
    last_name = "Admin"
    role = "admin"
    
    success, error = create_user(role, first_name, last_name, email, password)
    if success:
        print(f"Compte ADMIN créé avec succès : {email}")
    else:
        print(f"Erreur lors de la création : {error}")

if __name__ == "__main__":
    create_admin()
