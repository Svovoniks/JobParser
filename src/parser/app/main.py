from fastapi import FastAPI, Request
from common.database import DataBase
from app.celery_app import start_parsing_resumes, start_parsing_vacancies
from json import dumps

app = FastAPI()

@app.post("/parse_resumes/")
async def parse_resumes(request: Request):
    json_ = await request.json()
    idx = DataBase().add_new_task(dumps(json_), 'received')
    start_parsing_resumes.apply_async(args=[json_, idx], countdown=1)
    
    return {'task_id': idx}

@app.post("/parse_vacancies/")
async def parse_vacancies(request: Request):
    json_ = await request.json()
    idx = DataBase().add_new_task(dumps(json_), 'received')
    start_parsing_vacancies.apply_async(args=[json_, idx], countdown=1)

    return {'task_id': idx}
