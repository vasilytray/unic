from fastapi import FastAPI
from app.students.router import router as router_students
from app.users.router import router as router_users


app = FastAPI()


@app.get("/") # эндпоинт главной страницы
def home_page():
    return {"message": "Привет, Все!"}


app.include_router(router_students) # подключить (включить) роутер

app.include_router(router_users) # подключить (включить) роутер