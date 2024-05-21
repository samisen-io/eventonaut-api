from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_hash(plain):
    return pwd_context.hash(plain)

def verify_hash(plain_text, hashed_text):
    return pwd_context.verify(plain_text, hashed_text)