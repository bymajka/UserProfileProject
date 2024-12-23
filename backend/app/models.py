from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Detailed(BaseModel):
    """Generic model which is used to document error responses"""

    detail: str


class CreateUserModel(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=20,
        pattern=r"^[a-zA-Z0-9_]+$",
        examples=["johndoe2024"],
    )
    password: str = Field(min_length=8, examples=["$3cr3tP@ssw0rd"])
    full_name: Optional[str] = Field(max_length=64, examples=["John Doe"], default=None)


class LoginModel(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=20,
        pattern=r"^[a-zA-Z0-9_]+$",
        examples=["johndoe2024"],
    )
    password: str = Field(examples=["$3cr3tP@ssw0rd"])


class UserModel(BaseModel):
    username: str = Field(examples=["johndoe2024", "Grady_Booch"])
    full_name: Optional[str] = Field(examples=[None, "Grady Booch"])
    posts: int = Field(ge=0, examples=[0, 100, 200], description="Number of posts")


class CreatePostModel(BaseModel):
    content: str = Field(
        min_length=1, max_length=140, examples=["Lorem Ipsum Dolor Sit Amet"]
    )


class PostModel(BaseModel):
    id: str = Field(examples=["deadbeefdeadbeefdeadbeefdeadbeef"])
    author: UserModel = Field(
        examples=[UserModel(username="johndoe2024", full_name="John Doe", posts=1)]
    )
    content: str = Field(examples=["Lorem Ipsum Dolor Sit Amet"])
    likes: int = Field(ge=0, examples=[0, 100, 200], description="Number of likes")
    is_liked: bool
    created_at: datetime


class PaginationParams(BaseModel):
    page: int = Field(gt=0, default=1, examples=[1, 2, 3])
