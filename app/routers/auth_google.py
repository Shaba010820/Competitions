from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from starlette.requests import Request
from typing import Dict, Any, Optional

from app.database.session import get_db
from app.models.user import User
from app.core.security import create_access_token, create_refresh_token
from app.core.oauth import oauth

router = APIRouter(prefix="/auth/google", tags=["Auth (Google)"])


@router.get("/login")
async def login_via_google(request: Request) -> Any:
    """Initiate Google OAuth login flow"""
    redirect_uri = request.url_for("auth_callback")
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/callback", name="auth_callback")
async def auth_callback(request: Request, db: Session = Depends(get_db)):
    try:
        token = await oauth.google.authorize_access_token(request)

        user_info = token.get('userinfo')

        email = user_info.get("email")
        if not email:
            raise HTTPException(400, "Email not found in token")

        username = user_info.get("name", email.split("@")[0])

        user = db.query(User).filter(User.email == email).first()
        if not user:
            user = User(username=username, email=email)
            db.add(user)
            db.commit()
            db.refresh(user)

        token_data = {"sub": str(user.id)}
        return {
            "access_token": create_access_token(token_data),
            "refresh_token": create_refresh_token(token_data),
            "token_type": "bearer"
        }

    except Exception as e:
        raise HTTPException(400, detail=f"Authentication failed: {e}")
