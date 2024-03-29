from dotenv import (
    load_dotenv,
)

load_dotenv()
from api.db import (
    db,
    app,
)

from passlib.context import (
    CryptContext,
)
from jose import (
    JWTError,
    jwt,
)
from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials,
)
from fastapi import (
    Depends,
    HTTPException,
    status,
)
from pydantic import (
    Field,
)
from datetime import (
    datetime,
    timedelta,
)
from fastapi.middleware.cors import (
    CORSMiddleware,
)
from fastapi import (
    FastAPI,
    HTTPException,
)
from pydantic import (
    BaseModel,
)
from fastapi import (
    HTTPException,
)
import os
from fastapi import (
    Depends,
    HTTPException,
    status,
)
import tools.log_config as log_config
import os
import logging

current_file_path = os.path.abspath(__file__)
base_dir = os.path.dirname(current_file_path)
logger = logging.getLogger(__name__)


SECRET_KEY = os.environ["API_SECRET_KEY"]
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 365

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)
oauth2_scheme = HTTPBearer()


class TokenData(BaseModel):
    username: str = None


def verify_password(
    plain_password,
    hashed_password,
):
    return pwd_context.verify(
        plain_password,
        hashed_password,
    )


def get_password_hash(
    password,
):
    return pwd_context.hash(password)


def create_access_token(
    data: dict,
    expires_delta: timedelta = None,
):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )
    return encoded_jwt


async def get_current_user(
    token: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token.credentials,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = db.collection("users").document(username).get()
    if user:
        return user.to_dict()
    else:
        raise credentials_exception


tags_metadata = [
    {
        "name": "Auth",
        "description": "Authentication related endpoints",
    },
    {
        "name": "Overview",
        "description": "Overview related endpoints for account",
    },
    {
        "name": "Stats",
        "description": "Stats related endpoints for account",
    },
    {
        "name": "Extrinsics",
        "description": "Extrinsics related endpoints for account",
    },
    {
        "name": "Rewards",
        "description": "Rewards related endpoints for account",
    },
    {
        "name": "Badges",
        "description": "Badges related endpoints for account",
    },
]

from widgets.extrinsics import (
    Extrinsics,
)
from widgets.extrinsics import ExtrinsicsType

EXTRINSICS_CONTEXT = Extrinsics()

from widgets.overview import (
    Overview,
)
from widgets.overview import OverviewType

OVERVIEW_CONTEXT = Overview()

from widgets.rewards import (
    Rewards,
)
from widgets.rewards import RewardsType

REWARDS_CONTEXT = Rewards()

from widgets.stats import (
    Stats,
)
from widgets.stats import StatsType as StatsType

STATS_CONTEXT = Stats()

from widgets.badges import (
    Badges,
    StatsType,
)
from widgets.stats import StatsType

BADGES_CONTEXT = Badges()

app = FastAPI(openapi_tags=tags_metadata)


from api.routers import (
    overview,
    stats,
    extrinsics,
    rewards,
    badges,
)

app.include_router(
    overview.router,
    prefix="/overview",
    tags=[tags_metadata[1]["name"]],
)
app.include_router(
    stats.router,
    prefix="/stats",
    tags=[tags_metadata[2]["name"]],
)
app.include_router(
    extrinsics.router,
    prefix="/extrinsics",
    tags=[tags_metadata[3]["name"]],
)
app.include_router(
    rewards.router,
    prefix="/rewards",
    tags=[tags_metadata[4]["name"]],
)
app.include_router(
    badges.router,
    prefix="/badges",
    tags=[tags_metadata[5]["name"]],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AdminIn(BaseModel):
    admin_username: str = Field(
        ...,
        description="The username of the admin.",
    )
    admin_password: str = Field(
        ...,
        description="The password of the admin.",
    )


class UserIn(BaseModel):
    username: str = Field(
        ...,
        description="The username of the new user.",
    )
    password: str = Field(
        ...,
        description="The password of the new user.",
    )


class UserToken(BaseModel):
    username: str
    access_token: str
    token_type: str


@app.get(
    "/",
    dependencies=[Depends(get_current_user)],
    tags=["Auth"],
)
def read_root():
    return "Welcome to Flowana API!"


async def verify_admin_credentials(
    admin_in: AdminIn,
):
    if not (
        admin_in.admin_username == os.getenv("ADMIN_USERNAME")
        and verify_password(
            admin_in.admin_password,
            get_password_hash(os.getenv("ADMIN_PASSWORD")),
        )
    ):
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions",
        )


class UserOut(BaseModel):
    username: str
    message: str


@app.post(
    "/admin-create-user/",
    response_model=UserOut,
    tags=["Auth"],
)
async def admin_create_user(
    user_in: UserIn,
    admin_in: AdminIn = Depends(verify_admin_credentials),
):
    """
    Create a new user with admin credentials.
    """
    user = db.collection("users").document(user_in.username).get()

    if user.exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )

    hashed_password = get_password_hash(user_in.password)

    db.collection("users").document(user_in.username).set(
        {
            "username": user_in.username,
            "password": hashed_password,
        }
    )

    return UserOut(
        username=user_in.username,
        message="User successfully created",
    )


@app.post(
    "/get-token/",
    response_model=UserToken,
    tags=["Auth"],
)
async def login_for_access_token(
    user_in: UserIn,
):
    user = db.collection("users").document(user_in.username).get().to_dict()
    if user:
        if verify_password(
            user_in.password,
            user.get("password"),
        ):
            access_token_expires = timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
            access_token = create_access_token(
                data={"sub": user_in.username},
                expires_delta=access_token_expires,
            )
            return {
                "username": user_in.username,
                "access_token": access_token,
                "token_type": "bearer",
            }
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )


@app.get(
    "/test-auth",
    dependencies=[Depends(get_current_user)],
    tags=["Auth"],
)
async def test_auth():
    return {"message": "You are authorized!"}
