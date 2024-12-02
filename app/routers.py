import math
from typing import Annotated, NamedTuple, Optional
from fastapi import APIRouter, Body, Depends, HTTPException, Query, Response
from fastapi import status as status
from starlette.status import HTTP_409_CONFLICT

from .dependencies import authenticated_username
from .models import (
    CreatePostModel,
    CreateUserModel,
    Detailed,
    PostsParams,
    UserModel,
    LoginModel,
    PostModel,
)
from .logic import (
    verify_password,
    is_username_available,
    create_user,
    find_user,
    list_user_posts,
    create_post,
    find_post,
    add_like_to_post,
    remove_like_from_post,
)

api = APIRouter()


class _Link(NamedTuple):
    url: str
    rel: str


def _links(links: list[_Link]) -> str:
    return ",".join([f'<{link.url}>; rel="{link.rel}"' for link in links])


@api.post(
    "/register",
    tags=["users"],
    status_code=status.HTTP_201_CREATED,
    description="Register new user. Forbidden for logged in users",
    responses={
        status.HTTP_403_FORBIDDEN: {
            "description": "User already logged in",
            "model": Detailed,
        },
        status.HTTP_409_CONFLICT: {"description": "Username already taken", "model": Detailed},
    },
)
async def register(
    auth_username: Annotated[Optional[str], Depends(authenticated_username)],
    input: Annotated[CreateUserModel, Body()],
    response: Response,
) -> UserModel:
    if auth_username is not None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    if not is_username_available(input.username):
        raise HTTPException(
            status_code=status.CONFLICT, detail="Username already taken"
        )
    user = create_user(input)
    response.headers["Link"] = _links(
        [
            _Link("/login", "login"),
            _Link(f"/api/users/{user.username}", "self"),
        ]
    )
    return user


@api.post(
    "/login",
    tags=["users"],
    description="Does not perform anything, but checks if provided credentials are valid",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Invalid username or password",
            "model": Detailed,
        }
    },
    status_code=status.HTTP_204_NO_CONTENT,
)
async def login(input: Annotated[LoginModel, Body()]) -> None:
    if not verify_password(input.username, input.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return None


@api.get(
    "/me",
    tags=["users"],
    description="Returns the currently logged in user",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Not logged in", "model": Detailed}
    },
)
async def me(
    auth_username: Annotated[Optional[str], Depends(authenticated_username)],
    response: Response,
) -> UserModel:
    if auth_username is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    user = find_user(auth_username)
    assert user is not None
    response.headers["Link"] = _links(
        [
            _Link(f"/api/users/{user.username}/posts", "posts"),
        ]
    )
    return user


@api.get(
    "/users/{username}",
    tags=["users"],
    responses={status.HTTP_404_NOT_FOUND: {"description": "User not found", "model": Detailed}},
)
async def get_user(username: str, response: Response) -> UserModel:
    user = find_user(username)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    response.headers["Link"] = _links(
        [
            _Link(f"/api/users/{user.username}/posts", "posts"),
        ]
    )
    return user


@api.get(
    "/users/{username}/posts",
    tags=["posts"],
    responses={status.HTTP_404_NOT_FOUND: {"description": "User not found", "model": Detailed}},
)
async def get_user_posts(
    auth_username: Annotated[Optional[str], Depends(authenticated_username)],
    username: str,
    query: Annotated[PostsParams, Query()],
    response: Response,
) -> list[PostModel]:
    user = find_user(username)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    posts = list_user_posts(
        username=username, current_username=auth_username, page=query.page
    )
    if auth_username is not None:
        links = []
        if user.posts:
            links.append(_Link(f"/api/users/{user.username}/posts?page=1", "first"))
            links.append(
                _Link(
                    f"/api/users/{user.username}/posts?page={max(1, math.ceil(user.posts / 10))}",
                    "last",
                )
            )
        if query.page > 1:
            links.append(
                _Link(f"/api/users/{user.username}/posts?page={query.page - 1}", "prev")
            )
        if query.page < math.ceil(user.posts / 10):
            links.append(
                _Link(f"/api/users/{user.username}/posts?page={query.page + 1}", "next")
            )
        response.headers["Link"] = _links(links)
    return posts


@api.post(
    "/users/{username}/posts",
    tags=["posts"],
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "User not found", "model": Detailed},
        status.HTTP_403_FORBIDDEN: {
            "description": "User is not allowed to create post",
            "model": Detailed,
        },
    },
)
async def publish_post(
    auth_username: Annotated[Optional[str], Depends(authenticated_username)],
    username: str,
    response: Response,
    input: Annotated[CreatePostModel, Body()],
) -> PostModel:
    if auth_username is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    if auth_username.lower() != username.lower():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to create posts for other users",
        )
    post = create_post(username, input)
    response.headers["Link"] = _links(
        [
            _Link(f"/api/users/{post.author.username}/posts", "posts"),
            _Link(f"/api/users/{post.author.username}/posts/{post.id}", "self"),
        ]
    )
    return post


@api.get(
    "/users/{username}/posts/{post_id}",
    tags=["posts"],
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Post or user not found", "model": Detailed}
    },
)
async def read_post(
    auth_username: Annotated[Optional[str], Depends(authenticated_username)],
    username: str,
    post_id: str,
    response: Response,
) -> PostModel:
    post = find_post(username, post_id, current_username=auth_username)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    response.headers["Link"] = _links(
        [
            _Link(f"/api/users/{post.author.username}/posts", "posts"),
            _Link(f"/api/users/{post.author.username}/posts/{post.id}/like", "like"),
        ]
    )
    return post


@api.put(
    "/users/{username}/posts/{post_id}",
    tags=["posts"],
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "User not logged in", "model": Detailed},
        status.HTTP_404_NOT_FOUND: {"description": "Post not found", "model": Detailed},
    },
)
async def like_post(
    auth_username: Annotated[Optional[str], Depends(authenticated_username)],
    username: str,
    post_id: str,
    response: Response,
) -> None:
    if auth_username is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    post = find_post(username, post_id, current_username=auth_username)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    add_like_to_post(post, auth_username)
    response.headers["Link"] = _links(
        [
            _Link(f"/api/users/{post.author.username}/posts", "posts"),
            _Link(f"/api/users/{post.author.username}/posts/{post.id}", "self"),
        ]
    )


@api.delete(
    "/users/{username}/posts/{post_id}",
    tags=["posts"],
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "User not logged in", "model": Detailed},
        status.HTTP_404_NOT_FOUND: {"description": "Post not found", "model": Detailed},
    },
)
async def unlike_post(
    auth_username: Annotated[Optional[str], Depends(authenticated_username)],
    username: str,
    post_id: str,
    response: Response,
) -> None:
    if auth_username is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    post = find_post(username, post_id, current_username=auth_username)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    remove_like_from_post(post, auth_username)
    response.headers["Link"] = _links(
        [
            _Link(f"/api/users/{post.author.username}/posts", "posts"),
            _Link(f"/api/users/{post.author.username}/posts/{post.id}", "self"),
        ]
    )
