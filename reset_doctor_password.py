from app.database import SessionLocal
from app.models.user import User
from app.auth.password import hash_password

db = SessionLocal()

try:
    doctor = db.query(User).filter(
        User.email == "doctor@hospital.com"
    ).first()

    if doctor is None:
        print("Doctor account not found.")
    else:
        doctor.hashed_password = hash_password("Doctor@12345")
        db.commit()
        print("Doctor password set successfully.")
        print("Email: doctor@hospital.com")
        print("Password: Doctor@12345")

except Exception as e:
    db.rollback()
    print("Error:", e)

finally:
    db.close()