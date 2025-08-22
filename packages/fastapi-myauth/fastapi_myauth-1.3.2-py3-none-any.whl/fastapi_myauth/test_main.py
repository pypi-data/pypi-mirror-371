from fastapi import FastAPI
from sqlmodel import Session, SQLModel, create_engine

from fastapi_myauth import auth, models
from fastapi_myauth.config import settings

from .auth import FastAuth

app = FastAPI()


class UserC(models.UserCreate):
    language: str | None = None


class UserR(models.UserRead):
    language: str


class UserM(models.User):
    language: str = "en"


sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=True)

auth_components = auth.AuthComponents(
    user_model=UserM,
    user_read=UserR,
    user_create=UserC,
    user_update=models.UserUpdate,
)

fast_auth = FastAuth(
    engine=engine,
    components=auth_components,
)

crud_user = fast_auth.crud_user


def init_db(session: Session) -> None:
    user = crud_user.get_by_email(session, email=settings.FIRST_SUPERUSER)
    if not user:
        # Create user auth
        user_in = UserC(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        user = crud_user.create(session, obj_in=user_in)


SQLModel.metadata.create_all(engine)


app.include_router(fast_auth.get_router())
