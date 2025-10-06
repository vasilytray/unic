from fastapi import APIRouter, Depends
from app.majors.dao import MajorsDAO
from app.majors.rb import RBMajor
from app.majors.schemas import SMajorsAdd, SMajorsUpdDesc, SMajors


router = APIRouter(prefix='/majors', tags=['Работа с факультетами'])

@router.get("/", summary="Получить список факультетов")
async def get_all_majors(request_body: RBMajor = Depends()) -> list[SMajors]:
    return await MajorsDAO.find_all(**request_body.to_dict())

@router.post("/add/")
async def register_user(major: SMajorsAdd) -> dict:
    check = await MajorsDAO.add(**major.model_dump())
    if check:
        return {"message": "Факультет успешно добавлен!", "major": major}
    else:
        return {"message": "Ошибка при добавлении факультета!"}
    
@router.put("/update_description/")
async def update_major_description(major: SMajorsUpdDesc) -> dict:
    check = await MajorsDAO.update(filter_by={'major_name': major.major_name},
                                   major_description=major.major_description)
    if check:
        return {"message": "Описание факультета успешно обновлено!", "major": major}
    else:
        return {"message": "Ошибка при обновлении описания факультета!"}