from dataclasses import dataclass, field
from typing import Generic, TypeVar

from fastapi import APIRouter
from sqlalchemy import Engine
from sqlmodel import Relationship

from . import crud, models
from .api.deps import APIDependencies

# Generic type variables for user models
UserT = TypeVar("UserT", bound=models.User)
UserReadT = TypeVar("UserReadT", bound=models.UserRead)
UserCreateT = TypeVar("UserCreateT", bound=models.UserCreate)
UserUpdateT = TypeVar("UserUpdateT", bound=models.UserUpdate)


@dataclass
class AuthComponents(Generic[UserT, UserReadT, UserCreateT, UserUpdateT]):
    """
    A container for the core authentication components: models and the CRUD layer.

    This class takes the base user models, dynamically adds the necessary database
    relationships, and initializes the corresponding CRUD handler for data access.
    """

    user_model: type[UserT] = models.User  # type: ignore[assignment]
    user_read: type[UserReadT] = models.UserRead  # type: ignore[assignment]
    user_create: type[UserCreateT] = models.UserCreate  # type: ignore[assignment]
    user_update: type[UserUpdateT] = models.UserUpdate  # type: ignore[assignment]

    _internal_user_model: type[UserT] = field(init=False)
    _crud_user_instance: crud.CRUDUser[UserT, UserCreateT, UserUpdateT] = field(
        init=False
    )

    def __post_init__(self):
        """
        Initializes the internal models and the CRUD layer after the
        instance has been created.
        """

        class User(self.user_model, table=True):  # type: ignore
            refresh_tokens: list[models.RefreshToken] = Relationship(
                back_populates="authenticates", cascade_delete=True
            )

        self._internal_user_model = User  # type: ignore

        class CrudUser(crud.CRUDUser[self.User, self.UserCreate, self.UserUpdate]):  # type: ignore
            pass

        self._crud_user_instance = CrudUser(self.User)

    @property
    def User(self) -> type[UserT]:
        """Returns the fully configured internal user model."""
        return self._internal_user_model

    @property
    def UserRead(self) -> type[UserReadT]:
        """Returns the user read model."""
        return self.user_read

    @property
    def UserCreate(self) -> type[UserCreateT]:
        """Returns the user create model."""
        return self.user_create

    @property
    def UserUpdate(self) -> type[UserUpdateT]:
        """Returns the user update model."""
        return self.user_update

    @property
    def crud_user(self) -> crud.CRUDUser[UserT, UserCreateT, UserUpdateT]:
        """Returns the initialized CRUD user handler."""
        return self._crud_user_instance


@dataclass
class FastAuth(Generic[UserT, UserReadT, UserCreateT, UserUpdateT]):
    """
    FastAPI Authentication integration class.

    This class orchestrates the authentication flow by taking an engine and a
    pre-configured AuthComponents instance to set up dependency injection and
    API routes.
    """

    engine: Engine
    components: AuthComponents[UserT, UserReadT, UserCreateT, UserUpdateT]

    _deps_instance: APIDependencies = field(init=False)

    def __post_init__(self):
        """
        Initializes the dependency injection layer using the provided components.
        """
        self._deps_instance = APIDependencies(
            crud_user=self.components.crud_user,
            engine=self.engine,
        )

    # --- Properties that proxy to the components instance or initialized handlers ---

    @property
    def User(self) -> type[UserT]:
        """Returns the fully configured internal user model."""
        return self.components.User

    @property
    def UserRead(self) -> type[UserReadT]:
        """Returns the user read model."""
        return self.components.UserRead

    @property
    def UserCreate(self) -> type[UserCreateT]:
        """Returns the user create model."""
        return self.components.UserCreate

    @property
    def UserUpdate(self) -> type[UserUpdateT]:
        """Returns the user update model."""
        return self.components.UserUpdate

    @property
    def crud_user(self) -> crud.CRUDUser[UserT, UserCreateT, UserUpdateT]:
        """Returns the CRUD user handler."""
        return self.components.crud_user

    @property
    def deps(self) -> APIDependencies:
        """Returns the dependency provider for the auth library."""
        return self._deps_instance

    def get_router(self) -> APIRouter:
        """
        Constructs and returns a pre-configured APIRouter with all auth routes.
        """
        from fastapi_myauth.api.v1 import get_login_router, get_user_router

        api_router = APIRouter()

        # All required parts are now neatly available via properties.
        api_router.include_router(
            get_user_router(
                crud_user=self.crud_user,
                deps=self.deps,
                user_model=self.User,
                user_read=self.UserRead,
                user_create=self.UserCreate,
                user_update=self.UserUpdate,
            ),
            prefix="/users",
            tags=["users"],
        )
        api_router.include_router(
            get_login_router(
                crud_user=self.crud_user,
                deps=self.deps,
                user_model=self.User,
                user_read=self.UserRead,
                user_create=self.UserCreate,
                user_update=self.UserUpdate,
            ),
            prefix="/login",
            tags=["login"],
        )

        return api_router
