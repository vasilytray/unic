from fastapi import FastAPI
from app.students.router import router as router_students
from app.majors.router import router as router_majors
from app.users.router import router as router_users
from app.roles.router import router as router_roles



app = FastAPI()


@app.get("/") # эндпоинт главной страницы
def home_page():
    return {"message": "Привет, Все!"}


app.include_router(router_students) # подключить (включить) роутер
app.include_router(router_majors)
app.include_router(router_users) # подключить (включить) роутер
app.include_router(router_roles)