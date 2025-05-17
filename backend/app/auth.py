from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from starlette.config import Config
from starlette.responses import RedirectResponse

from .database import get_db
from .models import User
from .settings import get_settings

router = APIRouter()
settings = get_settings()
config = Config(environ={})
oauth = OAuth(config)
oauth.register(
    name="google",
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


def create_user(db: Session, profile: dict):
    user = db.query(User).filter(User.sub == profile["sub"]).first()
    if not user:
        user = User(sub=profile["sub"], email=profile["email"], name=profile.get("name"))
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


@router.get("/login")
async def login(request: Request):
    redirect_uri = request.url_for("auth_callback")
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/auth")
async def auth_callback(request: Request, db: Session = Depends(get_db)):
    token = await oauth.google.authorize_access_token(request)
    if not token:
        raise HTTPException(status_code=400, detail="Auth failed")
    userinfo = await oauth.google.parse_id_token(request, token)
    user = create_user(db, userinfo)
    response = RedirectResponse(url="/")
    response.set_cookie("session_user", str(user.id), httponly=True, max_age=3600 * 24 * 7)
    return response
