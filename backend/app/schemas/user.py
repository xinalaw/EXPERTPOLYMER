from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator


class UserRegisterSchema(BaseModel):
    first_name: str = Field(min_length=2, max_length=50)
    last_name: str = Field(min_length=2, max_length=50)
    email: EmailStr
    organization: str | None = Field(default=None, max_length=100)
    password: str = Field(min_length=8, max_length=72)
    password_confirm: str | None = Field(default=None, min_length=8, max_length=72)

    @model_validator(mode="after")
    def validate_password_confirm(self):
        if self.password_confirm is not None and self.password != self.password_confirm:
            raise ValueError("Пароли не совпадают")

        return self


class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)


class UserResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr
    organization: str | None = None
    avatar: str | None = None
    role: str
    director_id: int | None = None


class UserRoleUpdateSchema(BaseModel):
    role: str = Field(pattern="^(admin|director|researcher)$")


class UserDirectorUpdateSchema(BaseModel):
    director_id: int | None = None
