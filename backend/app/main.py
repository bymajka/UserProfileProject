from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

from .api import api


def init():
    from app.models import CreatePostModel, CreateUserModel
    from app.logic import add_like_to_post, create_post, create_user
    import random

    password = "12345678"
    texts = [
        'Is history repeating itself...?',
        "Damn, it's hard to wrap presents when you're drunk.",
        "Don't Look a Gift Horse In The Mouth",
        "Shot In the Dark",
        "Let Her Rip",
        "He excelled at firing people nicely.",
        "I don’t respect anybody who can’t tell the difference between Pepsi and Coke.",
        "We have a lot of rain in June.",
        "I may struggle with geography, but I'm sure I'm somewhere around here."
        "He wasn't bitter that she had moved on but from the radish.",
        "Barking dogs and screaming toddlers turn friendly neighbors into cranky enemies."
        "He uses onomatopoeia as a weapon of mental destruction.",
        "Every manager should be able to recite at least ten nursery rhymes backward.",
        "Make a sandwich blindfolded, then take a bite."
        "You Can't Teach an Old Dog New Tricks",
        "Off One's Base",
        "Mountain Out of a Molehill",
        "There's a message for you if you look up.",
        "It must be five o'clock somewhere.",
    ]
    users = [
        create_user(CreateUserModel(
            username=f"user_{i + 1}",
            password=password,
            full_name=random.choice([f"User {i + 1}", None]),
        ))
        for i in range(3)
    ]
    posts = [
        create_post(random.choice(users).username, CreatePostModel(content=text))
        for text in texts
    ]
    for _ in range(len(texts) * 2):
        add_like_to_post(random.choice(posts), random.choice(users).username)


init()


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
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
