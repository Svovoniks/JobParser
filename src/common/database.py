from datetime import datetime
import os
from typing import Any, List
from sqlalchemy import CursorResult, Engine, Executable, ForeignKey, MetaData, create_engine
from sqlalchemy import Table, Column, Integer, String, Boolean
from sqlalchemy.dialects.postgresql import insert, TIMESTAMP
from sqlalchemy import delete, select, update

from common.models import ResumeRequest, VacancyRequest, Vacancy, Resume,  Task

metadata = MetaData(schema='main')

vacancy_table = Table(
    "vacancy",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("vacancy_id", String, unique=True),
    Column("name", String),
    Column("area", String),
    Column("salary_from", Integer),
    Column("salary_to", Integer),
    Column("currency", String),
    Column("is_open", Boolean),
    Column("published_at", TIMESTAMP),
    Column("employer_id", Integer),
    Column("employer", String),
    Column("experience", String),
    Column("is_remote", Boolean),
)

resume_table = Table(
    "resume",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("resume_id", String, unique=True),
    Column("gender", String),
    Column("age", Integer),
    Column("salary", Integer),
    Column("experience", Integer),
    Column("search_status", String),
)

vacancy_skill_table = Table(
    'vacancy_skill',
    metadata,
    Column('vacancy_id', Integer, ForeignKey('vacnacy.id')),
    Column('skill_id', Integer, ForeignKey('skill.id'))
)

vacancy_role_table = Table(
    "vacancy_role",
    metadata,
    Column("vacancy_id", Integer, ForeignKey("vacancy.id")),
    Column("role_id", Integer, ForeignKey("role.id")),
)

resume_role_table = Table(
    "resume_role",
    metadata,
    Column("resume_id", Integer, ForeignKey("resume.id")),
    Column("role_id", Integer, ForeignKey("role.id")),
)

resume_skill_table = Table(
    "resume_skill",
    metadata,
    Column("resume_id", Integer, ForeignKey("resume.id")),
    Column("skill_id", Integer, ForeignKey("skill.id")),
)

skill_table = Table(
    "skill",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("skill", String, unique=True),
)

role_table = Table(
    "role",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("role", String, unique=True),
)

task_table = Table(
    "parsing_requests",
    metadata,
    Column('id', Integer, primary_key=True),
    Column("request_json", String),
    Column('status', String),
    Column('request_date', TIMESTAMP)
)

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class DataBase(metaclass=Singleton):
    engine: Engine

    def __init__(self) -> None:
        self.engine = self.connect()

    def connect(self) -> Engine:
        db_name = os.environ['DB_NAME']
        db_host = os.environ['POSTGRES_HOST']
        db_port = os.environ['POSTGRES_PORT']
        db_user = os.environ['POSTGRES_USER']
        db_password = os.environ['POSTGRES_PASSWORD']
        return create_engine(f'postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')

    def execute(self, stmnt: Executable) -> CursorResult[Any]:
        with self.engine.connect() as conn:
            result = conn.execute(stmnt)
            conn.commit()

            return result

    def add_resume(self, resume: Resume) -> None:
        skill_idxs = []
        for i in resume.skills:
            insert_skill = insert(skill_table).values(skill=i).on_conflict_do_update(index_elements=["skill"], set_=dict(skill = i)).returning(skill_table.c.id)
            skill_idxs.append(self.execute(insert_skill).first()[0])

        role_idxs = []
        for i in resume.roles_list:
            insert_role = insert(role_table).values(role=i).on_conflict_do_update(index_elements=["role"], set_=dict(role = i)).returning(role_table.c.id)
            role_idxs.append(self.execute(insert_role).first()[0])

        statement = insert(resume_table).values(
            resume_id=resume.resume_id,
            gender=resume.gender,
            age=resume.age,
            salary=resume.salary,
            experience=resume.experience,
            search_status=resume.search_status,
        )
        insert_or_update = statement.on_conflict_do_update(
            index_elements=["resume_id"],
            set_= dict(
                gender=resume.gender,
                age=resume.age,
                salary=resume.salary,
                experience=resume.experience,
                search_status=resume.search_status,
            )
        ).returning(resume_table.c.id)

        resume_id = self.execute(insert_or_update).first()[0]

        drop_previous_roles = delete(resume_role_table).where(resume_role_table.c.resume_id == resume_id)
        self.execute(drop_previous_roles)

        drop_previous_skills = delete(resume_skill_table).where(resume_skill_table.c.resume_id == resume_id)
        self.execute(drop_previous_skills)

        for i in skill_idxs:
            insert_skill_resume = insert(resume_skill_table).values(resume_id=resume_id, skill_id=i)
            self.execute(insert_skill_resume)

        for i in role_idxs:
            insert_role_resume = insert(resume_role_table).values(resume_id=resume_id, role_id=i)
            self.execute(insert_role_resume)

    def add_vacancy(self, vacancy: Vacancy) -> None:
        role_idxs = []
        for i in vacancy.professional_roles:
            insert_role = insert(role_table).values(role=i).on_conflict_do_update(index_elements=["role"], set_=dict(role = i)).returning(role_table.c.id)
            role_idxs.append(self.execute(insert_role).first()[0])

        skill_idxs = []
        for i in vacancy.skills:
            insert_skill = insert(skill_table).values(skill=i).on_conflict_do_update(index_elements=["skill"], set_=dict(skill = i)).returning(skill_table.c.id)
            skill_idxs.append(self.execute(insert_skill).first()[0])

        statement = insert(vacancy_table).values(
            vacancy_id=vacancy.vacancy_id,
            name=vacancy.name,
            area = vacancy.area,
            salary_from = vacancy.salary_from,
            salary_to = vacancy.salary_to,
            currency = vacancy.currency,
            is_open = vacancy.is_open,
            published_at = vacancy.published_at,
            employer_id = vacancy.employer_id,
            employer = vacancy.employer,
            experience = vacancy.experience,
            is_remote = vacancy.is_remote,
        )
        insert_or_update = statement.on_conflict_do_update(
            index_elements=["vacancy_id"],
            set_= dict(
                name=vacancy.name,
                area = vacancy.area,
                salary_from = vacancy.salary_from,
                salary_to = vacancy.salary_to,
                currency = vacancy.currency,
                is_open = vacancy.is_open,
                published_at = vacancy.published_at,
                employer_id = vacancy.employer_id,
                employer = vacancy.employer,
                experience = vacancy.experience,
                is_remote = vacancy.is_remote,
            )
        ).returning(vacancy_table.c.id)

        vacancy_id = self.execute(insert_or_update).first()[0]

        drop_previous_roles = delete(vacancy_role_table).where(vacancy_role_table.c.vacancy_id == vacancy_id)
        self.execute(drop_previous_roles)

        drop_previous_skills = delete(vacancy_skill_table).where(vacancy_skill_table.c.vacancy_id == vacancy_id)
        self.execute(drop_previous_skills)

        for i in role_idxs:
            insert_role_vacancy = insert(vacancy_role_table).values(vacancy_id=vacancy_id, role_id=i)
            self.execute(insert_role_vacancy)

        for i in skill_idxs:
            insert_skill_vacancy = insert(vacancy_skill_table).values(vacancy_id=vacancy_id, skill_id=i)
            self.execute(insert_skill_vacancy)

    def get_resume_by_id(self, idx: int) -> Resume:
        resume = self.execute(select(
            resume_table.c.resume_id,
            resume_table.c.gender,
            resume_table.c.age,
            resume_table.c.salary,
            resume_table.c.experience,
            resume_table.c.search_status,
        ).where(resume_table.c.id == idx)).first()
        skills = self.execute(select(skill_table.c.skill).select_from(skill_table).join(resume_skill_table).where(resume_skill_table.c.resume_id == idx))
        roles = self.execute(select(role_table.c.role).select_from(role_table).join(resume_role_table).where(resume_role_table.c.resume_id == idx))
        return Resume(
            resume_id=resume[0],
            gender=resume[1],
            age=resume[2],
            salary=resume[3],
            experience=resume[4],
            skills=list(map(lambda a: a[0], skills)),
            search_status=resume[5],
            roles_list=list(map(lambda a: a[0], roles))
        )

    def get_resume_by_resume_id(self, idx: str) -> Resume:
        resume = self.execute(select(
            resume_table.c.resume_id,
            resume_table.c.gender,
            resume_table.c.age,
            resume_table.c.salary,
            resume_table.c.experience,
            resume_table.c.search_status,
            resume_table.c.id,
        ).where(resume_table.c.resume_id == idx)).first()

        skills = self.execute(select(skill_table.c.skill).select_from(skill_table).join(resume_skill_table).where(resume_skill_table.c.resume_id == resume[6]))
        roles = self.execute(select(role_table.c.role).select_from(role_table).join(resume_role_table).where(resume_role_table.c.resume_id == resume[6]))

        return Resume(
            resume_id=resume[0],
            gender=resume[1],
            age=resume[2],
            salary=resume[3],
            experience=resume[4],
            skills=list(map(lambda a: a[0], skills)),
            search_status=resume[5],
            roles_list=list(map(lambda a: a[0], roles))
        )


    def get_resumes(self, resume: ResumeRequest) -> List[Resume]:
        select_statement = select(resume_table.c.id).select_from(resume_table)

        if resume['gender'] !=  None:
            select_statement =  select_statement.where(resume_table.c.gender.in_(resume['gender']))

        if resume['age_from'] != None:
            select_statement = select_statement.where(resume_table.c.age >= resume['age_from'])

        if resume['age_to'] != None:
            select_statement = select_statement.where(resume_table.c.age <= resume['age_to'])

        if resume['salary_from'] != None:
            select_statement = select_statement.where(resume_table.c.salary >= resume['salary_from'])

        if resume['salary_to'] != None:
            select_statement = select_statement.where(resume_table.c.salary <= resume['salary_to'])

        if resume['experience_from'] != None:
            select_statement = select_statement.where(resume_table.c.experience >= resume['experience_from'])

        if resume['experience_to'] != None:
            select_statement = select_statement.where(resume_table.c.experience <= resume['experience_to'])

        if resume['skills'] != None:
            skill_join_table = select(resume_skill_table.c.resume_id, skill_table.c.skill).select_from(resume_skill_table).join(skill_table).subquery()
            for i in resume['skills']:
                select_skill = select(skill_join_table.c.resume_id).where(skill_join_table.c.skill == i).subquery()
                select_statement = select_statement.where(resume_table.c.id.in_(select_skill))

        if resume['search_status'] != None:
            select_statement = select_statement.where(resume_table.c.search_status.in_(resume['search_status']))

        if resume['roles'] != None:
            role_join_table = select(resume_role_table.c.resume_id, role_table.c.role).select_from(resume_role_table.join(role_table)).subquery()
            valid_resumes = select(role_join_table.c.resume_id).select_from(role_join_table).where(role_join_table.c.role.in_(resume['roles'])).subquery()
            select_statement = select_statement.where(resume_table.c.id.in_(valid_resumes))

        return list(map(lambda a: self.get_resume_by_id(a[0]), self.execute(select_statement).all()))

    def get_vacancy_by_id(self, idx: int) -> Vacancy:
        vacancy = self.execute(select(
            vacancy_table.c.vacancy_id,
            vacancy_table.c.name,
            vacancy_table.c.area,
            vacancy_table.c.salary_from,
            vacancy_table.c.salary_to,
            vacancy_table.c.currency,
            vacancy_table.c.is_open,
            vacancy_table.c.published_at,
            vacancy_table.c.employer_id,
            vacancy_table.c.employer,
            vacancy_table.c.is_remote,
            vacancy_table.c.experience,
        ).where(vacancy_table.c.id == idx)).first()

        roles = self.execute(select(role_table.c.role).select_from(role_table).join(vacancy_role_table).where(vacancy_role_table.c.vacancy_id == idx)).all()
        skills = self.execute(select(skill_table.c.skill).select_from(skill_table).join(vacancy_skill_table).where(vacancy_skill_table.c.vacancy_id == idx)).all()

        return Vacancy(
            vacancy_id=vacancy[0],
            name=vacancy[1],
            area=vacancy[2],
            salary_from=vacancy[3],
            salary_to=vacancy[4],
            currency=vacancy[5],
            is_open=vacancy[6],
            published_at=vacancy[7],
            employer_id=vacancy[8],
            employer=vacancy[9],
            is_remote=vacancy[10],
            experience=vacancy[11],
            professional_roles=list(map(lambda a: a[0], roles)),
            skills=list(map(lambda a: a[0], skills)),
            salary_converted=True
        )

    def get_vacancy_by_vacancy_id(self, idx: int) -> Vacancy:
        vacancy = self.execute(select(
            vacancy_table.c.vacancy_id,
            vacancy_table.c.name,
            vacancy_table.c.area,
            vacancy_table.c.salary_from,
            vacancy_table.c.salary_to,
            vacancy_table.c.currency,
            vacancy_table.c.is_open,
            vacancy_table.c.published_at,
            vacancy_table.c.employer_id,
            vacancy_table.c.employer,
            vacancy_table.c.is_remote,
            vacancy_table.c.experience,
            vacancy_table.c.id,
        ).where(vacancy_table.c.vacancy_id == idx)).first()

        roles = self.execute(select(role_table.c.role).select_from(role_table).join(vacancy_role_table).where(vacancy_role_table.c.vacancy_id == vacancy[12])).all()
        skills = self.execute(select(skill_table.c.skill).select_from(skill_table).join(vacancy_skill_table).where(vacancy_skill_table.c.vacancy_id == vacancy[12])).all()

        return Vacancy(
            vacancy_id=vacancy[0],
            name=vacancy[1],
            area=vacancy[2],
            salary_from=vacancy[3],
            salary_to=vacancy[4],
            currency=vacancy[5],
            is_open=vacancy[6],
            published_at=vacancy[7],
            employer_id=vacancy[8],
            employer=vacancy[9],
            is_remote=vacancy[10],
            experience=vacancy[11],
            professional_roles=list(map(lambda a: a[0], roles)),
            skills=list(map(lambda a: a[0], skills)),
            salary_converted=True
        )

    def get_vacancies(self, vacancy: VacancyRequest) -> List[Vacancy]:
        select_statement = select(vacancy_table.c.id).select_from(vacancy_table)

        if vacancy['experience'] !=  None:
            select_statement =  select_statement.where(vacancy_table.c.experience.in_(vacancy['experience']))

        if vacancy['employer'] !=  None:
            select_statement =  select_statement.where(vacancy_table.c.employer.in_(vacancy['employer']))

        if vacancy['currency'] !=  None:
            select_statement =  select_statement.where(vacancy_table.c.currency.in_(vacancy['currency']))

        if vacancy['date_from'] != None:
            select_statement = select_statement.where(vacancy_table.c.published_at >= datetime.strptime(vacancy['date_from'], '%Y-%m-%d'))

        if vacancy['date_to'] != None:
            select_statement = select_statement.where(vacancy_table.c.published_at <= datetime.strptime(vacancy['date_to'], '%Y-%m-%d'))

        if vacancy['area'] != None:
            select_statement = select_statement.where(vacancy_table.c.area.in_(vacancy['area']))

        if vacancy['salary_from'] != None:
            select_statement = select_statement.where(vacancy_table.c.salary_from >= vacancy['salary_from'])

        if vacancy['salary_to'] != None:
            select_statement = select_statement.where(vacancy_table.c.salary_to <= vacancy['salary_to'])

        if vacancy['skills'] != None:
            skill_join_table = select(vacancy_skill_table.c.vacancy_id, skill_table.c.skill).select_from(vacancy_skill_table).join(skill_table).subquery()
            for i in vacancy['skills']:
                select_skill = select(skill_join_table.c.vacancy_id).where(skill_join_table.c.skill == i).subquery()
                select_statement = select_statement.where(vacancy_table.c.id.in_(select_skill))

        if vacancy['roles'] != None:
            role_join_table = select(vacancy_role_table.c.vacancy_id, role_table.c.role).select_from(vacancy_role_table).join(role_table).subquery()
            valid_vacancies = select(role_join_table.c.vacancy_id).select_from(role_join_table).where(role_join_table.c.role.in_(vacancy['roles'])).subquery()
            select_statement = select_statement.where(vacancy_table.c.id.in_(valid_vacancies))

        return list(map(lambda a: self.get_vacancy_by_id(a[0]), self.execute(select_statement).all()))

    def get_all_options(self, column: Column):
        return set(map(lambda a: a[0], self.execute(select(column)).all()))

    def add_new_task(self, json_string: str, status: str) -> int:
        insert_statement = insert(task_table).values(
            request_json=json_string,
            status=status
        ).returning(task_table.c.id)
        return self.execute(insert_statement).first()[0]

    def update_task(self, status: str, idx: int):
        update_statement = update(task_table).where(
            task_table.c.id == idx
        ).values(status=status)
        self.execute(update_statement)

    def get_tasks(self) -> list[Task]:
        select_statement = select(
            task_table.c.id,
            task_table.c.request_json,
            task_table.c.status,
            task_table.c.request_date
        )

        ts = self.execute(select_statement).all()
        tasks = []

        for i in ts:
            tasks.append(
                Task(
                    idx=i[0],
                    json_str=i[1],
                    status=i[2],
                    request_date=i[3]
                )
            )

        return tasks

    def get_task(self, idx) -> Task | None:
        select_statement = select(
            task_table.c.id,
            task_table.c.request_json,
            task_table.c.status,
            task_table.c.request_date
        ).where(
            task_table.c.id == idx
        )

        ts = self.execute(select_statement).first()

        if ts == None:
            return None

        return Task(
            idx==ts[0],
            json_str=ts[1],
            status=ts[2],
            request_date=ts[3]
        )
