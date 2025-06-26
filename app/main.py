from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from app.auth import router as auth_router
from app.auth.utils.security import decode_access_token
from app.db import SessionLocal
from app.db.models.user import User

app = FastAPI()
app.include_router(auth_router)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def get_current_user(token: str = Depends(oauth2_scheme), db=Depends(SessionLocal)):
    user_id = decode_access_token(token)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/me")
def read_me(current_user: User = Depends(get_current_user)):
    return {"email": current_user.email}
