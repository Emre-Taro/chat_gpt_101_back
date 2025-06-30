from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

hashed = pwd_context.hash("testpassword")
print(pwd_context.verify("testpassword", hashed))  # True になるはず
