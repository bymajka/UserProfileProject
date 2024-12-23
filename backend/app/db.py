from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import uuid4


@dataclass
class User:
    username: str
    password_hash: bytes
    full_name: Optional[str]
    posts: list["Post"]


@dataclass
class Post:
    id: str
    author: User
    content: str
    likes: set[str]
    created_at: datetime


class Database:
    def __init__(self):
        self._storage = {"users": {}}

    def find_user(self, username: str) -> Optional[User]:
        return self._storage["users"].get(username)

    def save_user(self, key: str, user: User):
        self._storage["users"][key] = user

    def save_post(self, post: Post):
        author = post.author
        id_ = uuid4().hex
        post.id = id_
        author.posts.insert(0, post)
        author.posts.sort(key=lambda p: p.created_at, reverse=True)


database = Database()
