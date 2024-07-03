from app.celery_app import celery_app
from common.models import ResumeRequest, VacancyRequest
from app.hh_parser import HH_parser
from common.database import DataBase

@celery_app.task
def start_parsing_resumes(json_: dict):
    resumes = HH_parser().get_resumes(ResumeRequest(json_))
    
    db = DataBase()
    for i in resumes:
        db.add_resume(i)

@celery_app.task
def start_parsing_vacancies(json_:  dict):
    vacancies = HH_parser().get_vacancies(ResumeRequest(json_))
    
    db = DataBase()
    for i in vacancies:
        db.add_vacancy(i)