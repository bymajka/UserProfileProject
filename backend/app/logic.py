from datetime import datetime
from typing import Optional
from passlib.hash import argon2

from .db import Post, User, database
from .models import CreateUserModel, PostModel, UserModel, CreatePostModel


def verify_password(username: str, password: str) -> bool:
    user = database.find_user(username.lower())
    return user is not None and argon2.verify(password, user.password_hash)


def is_username_available(username: str) -> bool:
    return username.lower() not in database._storage["users"]


def _find_user(username: str) -> Optional[User]:
    return database.find_user(username.lower())


def find_user(username: str) -> Optional[UserModel]:
    user = _find_user(username)
    if user is None:
        return None
    return UserModel(
        username=user.username,
        full_name=user.full_name,
        posts=len(user.posts),
    )


def create_user(input: CreateUserModel) -> UserModel:
    user = User(
        username=input.username,
        password_hash=argon2.hash(input.password),
        full_name=input.full_name,
        posts=[],
    )
    database.save_user(input.username.lower(), user)
    return UserModel(
        username=user.username,
        full_name=user.full_name,
        posts=len(user.posts),
    )


def list_user_posts(
    username: str, current_username: Optional[str] = None, page: int = 1
) -> list[PostModel]:
    user = _find_user(username)
    assert user is not None
    # Unauthenticated users can only see last 10 posts from user
    if current_username is None:
        page = 1
    return [
        PostModel(
            id=post.id,
            author=UserModel(
                username=user.username,
                full_name=user.full_name,
                posts=len(user.posts),
            ),
            content=post.content,
            likes=len(post.likes),
            is_liked=current_username is not None and username.lower() in post.likes,
            created_at=post.created_at,
        )
        for post in user.posts[(page - 1) * 10 : page * 10]
    ]


def create_post(username: str, input: CreatePostModel) -> PostModel:
    user = _find_user(username)
    assert user is not None
    post = Post(
        id="",
        author=user,
        content=input.content,
        likes=set(),
        created_at=datetime.now(),
    )
    database.save_post(post)
    return PostModel(
        id=post.id,
        author=UserModel(
            username=user.username,
            full_name=user.full_name,
            posts=len(user.posts),
        ),
        content=post.content,
        likes=len(post.likes),
        is_liked=username.lower() in post.likes,
        created_at=post.created_at,
    )


def _find_post(username: str, post_id: str) -> Optional[Post]:
    user = _find_user(username)
    if user is None:
        return None
    for post in user.posts:
        if post.id == post_id.lower():
            return post
    return None


def find_post(
    username: str, post_id: str, current_username: Optional[str] = None
) -> Optional[PostModel]:
    post = _find_post(username, post_id)
    if post is None:
        return None
    return PostModel(
        id=post.id,
        author=UserModel(
            username=post.author.username,
            full_name=post.author.full_name,
            posts=len(post.author.posts),
        ),
        content=post.content,
        likes=len(post.likes),
        is_liked=current_username is not None
        and current_username.lower() in post.likes,
        created_at=post.created_at,
    )


def add_like_to_post(post: PostModel, username: str) -> None:
    user = _find_user(username)
    post_ = _find_post(post.author.username, post.id)
    assert user is not None
    assert post_ is not None

    post_.likes.add(username.lower())


def remove_like_from_post(post: PostModel, username: str) -> None:
    user = _find_user(username)
    post_ = _find_post(post.author.username, post.id)
    assert user is not None
    assert post_ is not None

    post_.likes.remove(username.lower())
