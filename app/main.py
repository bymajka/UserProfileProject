from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from app.models import CreatePostModel, CreateUserModel
from .routers import api

from app.logic import add_like_to_post, create_post, create_user


def init():
    password = "12345678"
    user_1 = CreateUserModel(username="user_1", password=password, full_name="User 1")
    user_2 = CreateUserModel(username="user_2", password=password, full_name="User 2")
    user_3 = CreateUserModel(username="user_3", password=password, full_name=None)

    create_user(user_1)
    create_user(user_2)
    create_user(user_3)

    post_1_1 = create_post(user_1.username, CreatePostModel(content="Hello world!"))
    post_1_2 = create_post(
        user_1.username, CreatePostModel(content="Hello university!")
    )
    post_1_3 = create_post(user_1.username, CreatePostModel(content="Hello Ukraine!"))

    post_2_1 = create_post(user_2.username, CreatePostModel(content="Init bot user"))
    post_2_2 = create_post(
        user_2.username, CreatePostModel(content="Initialization failed!")
    )

    add_like_to_post(post_1_1, user_2.username)
    add_like_to_post(post_1_3, user_2.username)
    add_like_to_post(post_1_2, user_1.username)
    add_like_to_post(post_2_1, user_3.username)
    add_like_to_post(post_2_2, user_3.username)
    add_like_to_post(post_1_1, user_3.username)


init()


app = FastAPI()
app.include_router(api, prefix="/api", tags=["api"])

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
        <html><head><title>KPI-tter</title></head>
        <body><h1>KPI-tter</h1>
        <p><a href="/docs">Swagger UI</a></p>
        <p><a href="/redoc">Redoc</a></p>
        <p><a href="/openapi.json">OpenAPI Schema</a></p>
        </body></html>
    """
