from fastapi import FastAPI, Request
from app.students.router import router as router_students
from app.majors.router import router as router_majors
from app.users.router import router as router_users
from app.roles.router import router as router_roles
from app.pages.router import router as router_pages
# from app.chat.router import router as chat_router
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.exceptions import TokenExpiredException, TokenNoFoundException


app = FastAPI()

app.mount('/static', StaticFiles(directory='app/static'), 'static')

@app.get("/") # эндпоинт главной страницы
def home_page():
    return {"message": "Привет, Все!"}

@app.get("/auth")
async def redirect_to_auth():
    return RedirectResponse(url="/users/")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешить запросы с любых источников. Можете ограничить список доменов
    allow_credentials=True,
    allow_methods=["*"],  # Разрешить все методы (GET, POST, PUT, DELETE и т.д.)
    allow_headers=["*"],  # Разрешить все заголовки
)


app.include_router(router_students) # подключить (включить) роутер
app.include_router(router_majors)
app.include_router(router_users) # подключить (включить) роутер
app.include_router(router_roles)
app.include_router(router_pages)
# app.include_router(chat_router)

# Обработчик для TokenExpired
@app.exception_handler(TokenExpiredException)
async def token_expired_exception_handler(request: Request, exc: HTTPException):
    # Возвращаем редирект на страницу /auth
    return RedirectResponse(url="/auth")

# Обработчик для TokenNoFound
@app.exception_handler(TokenNoFoundException)
async def token_no_found_exception_handler(request: Request, exc: HTTPException):
    # Возвращаем редирект на страницу /auth
    return RedirectResponse(url="/auth")