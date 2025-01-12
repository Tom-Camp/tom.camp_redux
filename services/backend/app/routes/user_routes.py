from datetime import datetime, timedelta

from app.config import settings
from app.models.users import User, UserCreate
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = settings.secret_key
ALGORITHM = settings.hash_algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = 30


async def authenticate_user(email: str, password: str):
    user = await User.find_one(User.email == email)
    if not user:
        return False
    if not pwd_context.verify(password, user.hashed_password):
        return False
    return user


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        user = await User.find_one(User.username == username)
        if user is None:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception


# Token creation
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@router.post("/users/", response_model=User)
async def create_user(new_user: UserCreate):
    existing_user = await User.find_one(User.username == new_user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    existing_email = await User.find_one(User.email == new_user.email)
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = pwd_context.hash(new_user.password)

    new_user = User(
        username=new_user.username,
        email=new_user.email,
        hashed_password=hashed_password,
    )

    await new_user.insert()

    return new_user


@router.get("/users/{user_id}")
async def get_user(user_id: str):
    user = await User.get(user_id)
    return user


@router.get("/users")
async def list_users():
    users = await User.find_all().to_list()
    return users


@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    user = await user
    access_token = create_access_token(data={"sub": user.username})  # type: ignore[attr-defined]
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
