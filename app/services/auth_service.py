import bcrypt

def hash_password(password: str) -> str:
    #  FIX: ensure max 72 bytes (bcrypt limit)
    password_bytes = password.encode("utf-8")[:72]

    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)

    return hashed.decode("utf-8")

def verify_password(password: str, hashed_password: str) -> bool:
    password_bytes = password.encode("utf-8")[:72]
    return bcrypt.checkpw(password_bytes, hashed_password.encode("utf-8"))