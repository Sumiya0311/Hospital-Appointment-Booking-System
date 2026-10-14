from getpass import getpass

from app.database import SessionLocal
from app.models.user import User
from app.auth.password import hash_password


def create_admin():
    db = SessionLocal()

    try:
        email = input("Enter admin email: ").strip().lower()

        existing = db.query(User).filter(
            User.email == email
        ).first()

        if existing:
            print("This email is already registered.")
            print("Existing role:", existing.role)
            return

        name = input("Enter admin name: ").strip()
        phone = input("Enter admin phone: ").strip()
        password = getpass("Enter admin password (8-72 characters): ")

        if len(name) < 2:
            print("Name must contain at least 2 characters.")
            return

        if len(phone) < 10 or len(phone) > 15:
            print("Phone must contain 10-15 characters.")
            return

        if len(password) < 8 or len(password) > 72:
            print("Password must contain 8-72 characters.")
            return

        admin = User(
            name=name,
            email=email,
            phone=phone,
            hashed_password=hash_password(password),
            role="Admin",
            is_active=True,
        )

        db.add(admin)
        db.commit()

        print("Admin account created successfully.")

    except Exception as error:
        db.rollback()
        print("Could not create admin:", error)

    finally:
        db.close()


if __name__ == "__main__":
    create_admin()