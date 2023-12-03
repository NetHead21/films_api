from fastapi import FastAPI, Request, Header, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager

from typing import Optional
from database import SessionLocal, engine
import models

models.Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    db = SessionLocal()
    num_films = db.query(models.Films).count()
    if num_films == 0:
        films = [
            {"name": "Blade Runner", "director": "Ridley Scott"},
            {"name": "Pulp Fiction", "director": "Quentin Tarantino"},
            {"name": "Mulholland Drive", "director": "David Lynch"},
            {"name": "Avatar", "director": "James Cameron"},
            {"name": "Ang Provinsiano The Movie", "director": "Coco Martin"},
            {"name": "Batman", "director": "Lynch"},
        ]
        for film in films:
            db.add(models.Films(**film))
        db.commit()
        db.close()
    yield


USE_LIFESPAN = True

app = FastAPI(lifespan=lifespan if USE_LIFESPAN else None)

templates = Jinja2Templates(directory="templates")


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/", response_class=HTMLResponse)
async def movie_list(
    request: Request,
    hx_request: Optional[str] = Header(None),
    db: Session = Depends(get_db),
    page: int = 1,
):
    num = 2
    OFFSET = (page - 1) * num
    films = db.query(models.Films).offset(OFFSET).limit(num)

    context = {"request": request, "films": films, "page": page}
    if hx_request:
        return templates.TemplateResponse("partials/table.html", context)
    return templates.TemplateResponse("index.html", context)
