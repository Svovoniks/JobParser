from django.http import HttpResponse
from django.template import loader
from django import forms
from django.shortcuts import render
from django.contrib import messages
from django.urls import reverse
from collections import Counter
import requests
import json

from common.database import DataBase
from common.models import VacancyRequest, ResumeRequest
from .forms.vacancy import VacancyRequestForm, VacancyFilterForm
from .forms.resumes import ResumeRequestForm, ResumeFilterForm

def vacancies(request):
    if request.method == 'POST':
        form = VacancyRequestForm(request.POST)
        if form.is_valid():
            rq = requests.post('http://parser_server:8000/parse_vacancies/', json=form.to_json())
            messages.info(request, f'ID вашего запроса: {rq.json()["task_id"]}')
    else:
        form = VacancyRequestForm()
    
    return render(request, 'ui/search_view.html', {'form': form, 'page_title': 'Поиск вакансий'})


def resumes(request):
    if request.method == 'POST':
        form = ResumeRequestForm(request.POST)
        if form.is_valid():
            rq = requests.post('http://parser_server:8000/parse_resumes/', json=form.to_json())
            messages.info(request, f'ID вашего запроса: {rq.json()["task_id"]}')
    else:
        form = ResumeRequestForm()
        
    return render(request, 'ui/search_view.html', {'form': form, 'page_title': 'Поиск резюме'})

def get_task_json(task_id):
    json_data = 'Error'

    if task_id == None:
        return json_data
    
    task = DataBase().get_task(task_id)
    if task == None:
        return json_data
    
    return json.dumps(json.loads(task.json_str), indent=4)

def task(request, task_id=None):
    return render(request, 'ui/json_view.html', {'json_data': get_task_json(task_id), 'page_title': 'Тело запроса'})

def resume_skills(request, resume_id=None):
    skills = DataBase().get_resume_by_resume_id(resume_id).skills
    return render(request, 'ui/json_view.html', {'json_data': str(skills), 'page_title': 'Навыки'})

def resume_roles(request, resume_id=None):
    roles = DataBase().get_resume_by_resume_id(resume_id).roles_list
    return render(request, 'ui/json_view.html', {'json_data': str(roles), 'page_title': 'Роли'})
    
def vacancy_skills(request, vacancy_id=None):
    skills = DataBase().get_vacancy_by_vacancy_id(vacancy_id).skills
    return render(request, 'ui/json_view.html', {'json_data': str(skills), 'page_title': 'Навыки'})

def vacancy_roles(request, vacancy_id=None):
    roles = DataBase().get_vacancy_by_vacancy_id(vacancy_id).professional_roles
    return render(request, 'ui/json_view.html', {'json_data': str(roles), 'page_title': 'Роли'})

def get_tasks():
    tasks = []
    for i in DataBase().get_tasks():
        tasks.append((i.idx, i.status, i.request_date.strftime("%m-%d-%Y, %H:%M:%S")))
    
    return tasks

def tasks(request):
    columns = [
        'ID',
        'Статус',
        'Время добавления (UTC)',
        'Тело запроса',
    ]
    rows = []
    
    for i in get_tasks():
        rows.append(((i[0], ''), (i[1], ''), (i[2], ''), (i[1], reverse('task', args=[i[0]]))))
    
    return render(request, 'ui/table.html', {'columns': columns, 'rows': rows, 'page_title': 'История запросов'})

def analytics(request):
    buttons = [
        {'label': 'Отношение резюме к вакансиям', 'url': 'vacancy_resume_ratio/'},
        {'label': 'Анализ резюме', 'url': 'resume_averages/'},
        {'label': 'Анализ вакансий', 'url': 'vacancy_averages/'},
    ]
    return render(request, 'ui/analytics.html', {'buttons': buttons})

def vacancy_resume_ratio(request):
    if request.method == 'POST':
        resume_form = ResumeFilterForm(request.POST, prefix='resume')
        vacancy_form = VacancyFilterForm(request.POST, prefix='vacancy')
        if resume_form.is_valid() and vacancy_form.is_valid():
            number_of_vacancies, number_of_resumes = get_vacancy_resume_ratio(resume_form, vacancy_form)
            return render(request, 'ui/vacancy_resume_ratio.html', {
                'resume_form': resume_form,
                'vacancy_form': vacancy_form,
                'page_title': 'Поиск вакансий',
                'have_answer': True,
                'number_of_vacancies': number_of_vacancies,
                'number_of_resumes': number_of_resumes,
                'resume_vacancy': f'{number_of_resumes/number_of_vacancies:.2f}'.rstrip('0').rstrip('.') if number_of_vacancies != 0 else 'Infinity'
                }
            )
    else:
        resume_form = ResumeFilterForm(prefix='resume')
        vacancy_form = VacancyFilterForm(prefix='vacancy')
        
    return render(request, 'ui/vacancy_resume_ratio.html', {'resume_form': resume_form, 'vacancy_form': vacancy_form, 'page_title': 'Поиск вакансий', 'have_answer': False})

def get_vacancy_resume_ratio(resume_request: ResumeFilterForm, vacancy_request: VacancyFilterForm):
    db = DataBase()
    resumes = db.get_resumes(ResumeRequest(resume_request.to_json()))
    vacancies = db.get_vacancies(VacancyRequest(vacancy_request.to_json()))
    return len(vacancies), len(resumes)

def get_most_common(ls):
    ls = list(filter(lambda a: a != None, ls))
    most_common = Counter(ls).most_common(1)
    if not most_common:
        return 'Ничего не нашлось'
    most_common = most_common[0]
    return f'"{most_common[0]}", встречается {most_common[1]} {"раз" if (9 < most_common[1] < 20) or not (1 < most_common[1]%10 < 5) else "раза"}'  

def get_average(ls):
    ls = list(filter(lambda a: a != None, ls))
    sm = sum(ls)
    return f'{sm/len(ls):.2f}'.rstrip('0').rstrip('.') if len(ls) != 0 else 'Не достаточно информации'

def flatten(xss):
    return [x for xs in xss for x in xs]

def get_averages_vacancy(vacancy_request: VacancyRequest):
    db = DataBase()
    vacancies = db.get_vacancies(vacancy_request)
    names = list(map(lambda a: a.name, vacancies))
    areas = list(map(lambda a: a.area, vacancies))
    currency = list(map(lambda a: a.currency, vacancies))
    is_open = list(map(lambda a: a.is_open, vacancies))
    employer = list(map(lambda a: a.employer, vacancies))
    experience = list(map(lambda a: a.experience, vacancies))
    employer = list(map(lambda a: a.employer, vacancies))
    roles = flatten(list(map(lambda a: a.professional_roles, vacancies)))
    skills = flatten(list(map(lambda a: a.skills, vacancies)))
    salary_from = list(map(lambda a: a.salary_from, vacancies))
    salary_to = list(map(lambda a: a.salary_to, vacancies))
    return [
        ('Всего подходящих вакансий', len(vacancies)),
        ('Самое частое название', get_most_common(names)),
        ('Самое частое место работы', get_most_common(areas)),
        ('Самая частая валюта', get_most_common(currency)),
        ('Самый частый статус', get_most_common(is_open)),
        ('Самая частая компания', get_most_common(employer)),
        ('Самый часто требуемый опыт', get_most_common(experience)),
        ('Самая частая роль', get_most_common(roles)),
        ('Самый частый навык', get_most_common(skills)),
        ('Средняя начальная зарплата', get_average(salary_from)),
        ('Средняя максимальная зарплата', get_average(salary_to)),
    ]

def get_averages_resume(resume_request: ResumeRequest):
    db = DataBase()
    resumes = db.get_resumes(resume_request)
    genders = list(map(lambda a: a.gender, resumes))
    ages = list(map(lambda a: a.age, resumes))
    salaries = list(map(lambda a: a.salary, resumes))
    experiences = list(map(lambda a: a.experience, resumes))
    skills = flatten(list(map(lambda a: a.skills, resumes)))
    search_statuses = list(map(lambda a: a.search_status, resumes))
    roles = flatten(list(map(lambda a: a.roles_list, resumes)))
    
    return [
        ('Всего подходящих резюме', len(resumes)),
        ('Самый частый пол', get_most_common(genders)),
        ('Самая частая роль', get_most_common(roles)),
        ('Самый частый навык', get_most_common(skills)),
        ('Самый частый статус', get_most_common(search_statuses)),
        ('Средняя зарплата', get_average(salaries)),
        ('Средний возраст', get_average(ages)),
        ('Средний опыт', get_average(experiences)),
    ]

def render_resume_view(render_request, resume_request: ResumeRequest):
    resumes = DataBase().get_resumes(resume_request)
    
    columns = [
        'resume_id',
        'Пол',
        'Возраст',
        'Зарплата',
        'Опыт',
        'Статус поиска',
        'Навыки',
        'Професси',
    ]
    rows = []
    
    for i in resumes:
        rows.append((
            (i.resume_id, ''), 
            (i.gender, ''), 
            (i.age, ''), 
            (i.salary, ''),
            (i.experience, ''),
            (i.search_status, ''),
            ('Навыки', reverse('resume_skills', args=[i.resume_id])),
            ('Професии', reverse('resume_roles', args=[i.resume_id])))
        )
    
    return render(render_request, 'ui/table.html', {'columns': columns, 'rows': rows, 'page_title': 'Резюме'})


def resume_averages(request):
    have_answer = False
    results = []
    print('lol')
    
    if request.method == 'POST':
        form = ResumeFilterForm(request.POST)
        if form.is_valid():
            resume_request = ResumeRequest(form.to_json()) 
            if 'view_button' in form.data:
                return render_resume_view(request, resume_request)
            elif 'analytics_button' in form.data:
                results = get_averages_resume(resume_request)
                have_answer = True
    else:
        form = ResumeFilterForm()
        
    return render(request, 'ui/average.html', {'form': form, 'page_title': 'Анализ резюме', 'have_answer': have_answer, 'results': results})
        
def render_vacancy_view(render_request, vacancy_request: VacancyRequest):
    vacancies_list = DataBase().get_vacancies(vacancy_request)
    
    columns = [
        'vacancy_id',
        'Название',
        'Место работы',
        'Начальная зарплата (в  рублях)',
        'Максимальная зарплата (в рублях)',
        'Валюта',
        'Открыта',
        'Опубликованна',
        'ID компании',
        'Компания',
        'Требуемый опыт',
        'Удалённо',
        'Навыки',
        'Роли',
    ]
    rows = []
    
    for i in vacancies_list:
        rows.append((
            (i.vacancy_id, ''), 
            (i.name, ''), 
            (i.area, ''), 
            (i.salary_from, ''),
            (i.salary_to, ''),
            (i.currency, ''),
            (i.is_open, ''),
            (i.published_at, ''),
            (i.employer_id, ''),
            (i.employer, ''),
            (i.experience, ''),
            (i.is_remote, ''),
            ('Навыки', reverse('vacancy_skills', args=[i.vacancy_id])),
            ('Професии', reverse('vacancy_roles', args=[i.vacancy_id])))
        )
    
    return render(render_request, 'ui/table.html', {'columns': columns, 'rows': rows, 'page_title': 'Вакансии'})
    
def vacancy_averages(request):
    have_answer = False
    results = []

    if request.method == 'POST':
        form = VacancyFilterForm(request.POST)
        if form.is_valid():
            vacancy_request = VacancyRequest(form.to_json())
            if 'view_button' in form.data:
                return render_vacancy_view(request, vacancy_request)
            elif 'analytics_button' in form.data:
                results = get_averages_vacancy(vacancy_request)
                have_answer = True
    else:
        form = VacancyFilterForm()
        
    return render(request, 'ui/average.html', {'form': form, 'page_title': 'Анализ вакансий', 'have_answer': have_answer, 'results': results})