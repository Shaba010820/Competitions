from fastapi import FastAPI
from app.routers.matches import router as matches_router
from app.routers.users import router as user_router
from app.routers.competitions import router as comp_router
from app.routers.disciplines import router as discipline_router
from app.routers.match_paricipants import router as match_part_router
from app.routers.user_profiles import router as profile_router
from app.routers.auth import router as auth_router
from app.routers.auth_google import router as google_auth_router
from starlette.middleware.sessions import SessionMiddleware
from app.models.base import Base
from app.database.session import engine
from app.routers.elastic_search import router as elastic_router


app = FastAPI()

app.add_middleware(
    SessionMiddleware,
    secret_key="somesecretkeysomesecretkeysomess",
    https_only=False,
    same_site="lax"
)


@app.on_event('startup')
def startup():
    Base.metadata.create_all(bind=engine)

app.include_router(google_auth_router)
app.include_router(matches_router)
app.include_router(user_router)
app.include_router(comp_router)
app.include_router(discipline_router)
app.include_router(match_part_router)
app.include_router(profile_router)
app.include_router(auth_router)
app.include_router(elastic_router)
