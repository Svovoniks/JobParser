from celery import Celery
from common.models import ResumeRequest, VacancyRequest, Resume
from app.hh_parser import HH_parser
from common.database import DataBase

import logging

celery_app = Celery(
    'main',
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0"
)

@celery_app.task
def start_parsing_resumes(json_: dict, task_idx: int):
    db = DataBase()
    db.update_task('started', task_idx)

    resumes = HH_parser().get_resumes(ResumeRequest(json_))
    
    for i in resumes:
        db.add_resume(i)
    
    db.update_task('finished', task_idx)

@celery_app.task
def start_parsing_vacancies(json_:  dict, task_idx: int):
    db = DataBase()
    db.update_task('started', task_idx)

    vacancies = HH_parser().get_vacancies(VacancyRequest(json_))
    
    for i in vacancies:
        db.add_vacancy(i)
    
    db.update_task('finished', task_idx)


@celery_app.task
def get_vacancy(ls: list):
    logging.info('Proceessing batch')
    db = DataBase()
    for i in ls:
        vc = HH_parser()._get_vacancy_by_id(i)
        if vc != None:
            db.add_vacancy(vc)