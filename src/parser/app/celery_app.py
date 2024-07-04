from celery import Celery
from common.models import ResumeRequest, VacancyRequest, Resume
from app.hh_parser import HH_parser
from common.database import DataBase
from celery import shared_task
from celery_heimdall import HeimdallTask, RateLimit


celery_app = Celery(
    'main',
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0"
)

@shared_task(
    base=HeimdallTask,
    heimdall={
        'rate_limit': RateLimit((1, 1))
    }
)
def hh_call_limiter():
    return True

@celery_app.task
def start_parsing_resumes(json_: dict, task_idx: int):
    db = DataBase()
    db.update_task('started', task_idx)

    resumes = HH_parser(hh_call_limiter).get_resumes(ResumeRequest(json_))

    for i in resumes:
        db.add_resume(i)

    db.update_task('finished', task_idx)

@celery_app.task
def start_parsing_vacancies(json_:  dict, task_idx: int):
    db = DataBase()
    db.update_task('started', task_idx)

    vacancies = HH_parser(hh_call_limiter).get_vacancies(VacancyRequest(json_))

    for i in vacancies:
        db.add_vacancy(i)

    db.update_task('finished', task_idx)
