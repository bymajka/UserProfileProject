import math
from typing import Annotated, NamedTuple, Optional
from fastapi import APIRouter, Body, Depends, HTTPException, Query, Response
from fastapi import status

from .dependencies import authenticated_username
from .models import (
    CreatePostModel,
    CreateUserModel,
    Detailed,
    PaginationParams,
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
    responses={
        status.HTTP_409_CONFLICT: {
            "description": "Username already taken",
            "model": Detailed,
        },
    },
)
async def register(
    input: Annotated[CreateUserModel, Body()],
    response: Response,
) -> UserModel:
    """Endpoint for registering new users

    While most of applications require two password fields to ensure user never
    mistypes their password, we use only one such field for simplicity. If you
    want to have password and verify password fields in your app, consider
    implementing them on front-end.
    """
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
    """Endpoint for logging in

    Actually as we use Basic auth this endpoint just checks if provided
    credentials are valid. If everything OK, it returns HTTP 204 No Content
    response, otherwise if either username or password provided were invalid it
    returns HTTP 401 Unauthorized.

    Please note that this endpoint does not create any kind of user session or
    whatever.
    """
    if not verify_password(input.username, input.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers={"WWW-Authenticate": "Basic"},
        )
    return None


@api.get(
    "/me",
    tags=["users"],
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Not logged in",
            "model": Detailed,
        }
    },
)
async def me(
    auth_username: Annotated[Optional[str], Depends(authenticated_username)],
    response: Response,
) -> UserModel:
    """Returns currenlty authenticated user"""
    if auth_username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers={"WWW-Authenticate": "Basic"},
        )
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
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "User not found", "model": Detailed}
    },
)
async def get_user(username: str, response: Response) -> UserModel:
    """Returns user information by username"""
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
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "User not found", "model": Detailed}
    },
)
async def get_user_posts(
    auth_username: Annotated[Optional[str], Depends(authenticated_username)],
    username: str,
    query: Annotated[PaginationParams, Query()],
    response: Response,
) -> list[PostModel]:
    """Returns list of posts by username

    The result is paginated with the page size of 10 posts per page.

    While this method does not require authentication, the response slightly
    differs for authenticated and non-authenticated users.

    If user is unauthenticated, only last 10 posts are returned. Pagination is
    not supported, and regardless which page is sent in query parameter only
    last 10 posts will be shown.

    Authenticated users also see whether they liked any of the posts or not.
    """
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
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Not logged in",
            "model": Detailed,
        },
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
    """Endpoint for creating new post.

    This action requires authentication.

    Posts are limited by 140 characters.

    While there is a {username} parameter in the URL, users are not allowed to
    created posts for other users. Therefore if {username} will be different
    from the authenticated user's username HTTP 403 Forbidden error will be
    returned
    """
    if auth_username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers={"WWW-Authenticate": "Basic"},
        )
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
        status.HTTP_404_NOT_FOUND: {
            "description": "Post or user not found",
            "model": Detailed,
        }
    },
)
async def read_post(
    auth_username: Annotated[Optional[str], Depends(authenticated_username)],
    username: str,
    post_id: str,
    response: Response,
) -> PostModel:
    """Endpoint for reading post

    In order to retrieve the post it is necessary to provide correct pair of
    {username} and {post_id}. If the post exists but wrong {username} was
    provided, HTTP 404 Not Found error will be returned instead of post
    contents.

    This action does not require authentication, but if the user is
    authenticated, they will see whether they liked the post or not.
    """
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
    "/users/{username}/posts/{post_id}/like",
    tags=["posts"],
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "User not logged in",
            "model": Detailed,
        },
        status.HTTP_404_NOT_FOUND: {"description": "Post not found", "model": Detailed},
    },
)
async def like_post(
    auth_username: Annotated[Optional[str], Depends(authenticated_username)],
    username: str,
    post_id: str,
    response: Response,
) -> None:
    """Endpoint for liking post

    In order to like the post it is necessary to provide correct pair of
    {username} and {post_id}. If the post with given {post_id} exists but wrong
    {username} was provided, HTTP 404 Not Found error will be returned. 

    This action requires authentication.

    This action is idempotent, meaning if the user has already liked the post
    it will not be liked twice, nor any error will be thrown.
    """
    if auth_username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers={"WWW-Authenticate": "Basic"},
        )

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
    "/users/{username}/posts/{post_id}/like",
    tags=["posts"],
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "User not logged in",
            "model": Detailed,
        },
        status.HTTP_404_NOT_FOUND: {"description": "Post not found", "model": Detailed},
    },
)
async def unlike_post(
    auth_username: Annotated[Optional[str], Depends(authenticated_username)],
    username: str,
    post_id: str,
    response: Response,
) -> None:
    """Endpoint for unliking post

    In order to unlike the post it is necessary to provide correct pair of
    {username} and {post_id}. If the post with given {post_id} exists but wrong
    {username} was provided, HTTP 404 Not Found error will be returned. 

    This action requires authentication.

    This action is idempotent, meaning if the user has already unliked the post
    it will not be unliked twice, if user never liked the post this endpoint
    will just silently return. No error will be thrown in such case.
    """
    if auth_username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers={"WWW-Authenticate": "Basic"},
        )

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
