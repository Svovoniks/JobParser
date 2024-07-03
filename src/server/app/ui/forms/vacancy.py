from django import forms
from common.database import DataBase, vacancy_table, role_table, skill_table

EMPLOYMENT_CHOICES = (
    ('full', 'Полная занятость'),
    ('part', 'Частичная занятость'),
    ('project', 'Проектная работа'),
    ('volunteer', 'Волонтерство'),
    ('probation', 'Стажировка'),
)

EXPERIENCE_CHOICES = (
    ('noExperience', 'Нет опыта'),
    ('between1And3', 'От 1 года до 3 лет'),
    ('between3And6', 'От 3 до 6 лет'),
    ('moreThan6', 'Более 6 лет'),
)

SCHEDULE_CHOICES = (
    ('fullDay', 'Полный день'),
    ('shift', 'Сменный график'),
    ('flexible', 'Гибкий график'),
    ('remote', 'Удаленная работа'),
    ('flyInFlyOut', 'Вахтовый метод'),
)

areas = []
with open('ui/dictionaries/areas.txt', 'r', encoding="utf-8") as file:
    areas = file.readlines()

AREA_CHOICES = [tuple(i.strip().split(' ', maxsplit=1)) for i in areas]

roles = []
with open('ui/dictionaries/roles.txt', 'r', encoding="utf-8") as file:
    roles = file.readlines()

ROLES_CHOICES = [tuple(i.strip().split(' ', maxsplit=1)) for i in roles]
ROLES_CHOICES.insert(0, (None, 'Любая профессия'))

CURRENCY_CHOICES = (
    (None, 'Любая валюта'),
    ('AZN', 'AZN'),
    ('BYR', 'BYR'),
    ('EUR', 'EUR'),
    ('RUR', 'RUB'),
    ('GEL', 'GEL'),
    ('KGS', 'KGS'),
    ('KZT', 'KZT'),
    ('UAH', 'UAH'),
    ('USD', 'USD'),
    ('UZS', 'UZS')
)

class VacancyRequestForm(forms.Form):
    text = forms.CharField(max_length=255, required=False, label='Название вакансии')
    experience = forms.MultipleChoiceField(choices=EXPERIENCE_CHOICES, required=False, label='Опыт работы', widget=forms.SelectMultiple)
    employment = forms.MultipleChoiceField(choices=EMPLOYMENT_CHOICES, required=False, label='Тип занятости', widget=forms.SelectMultiple)
    schedule = forms.MultipleChoiceField(choices=SCHEDULE_CHOICES, required=False, label='График работы', widget=forms.SelectMultiple)
    area = forms.MultipleChoiceField(choices=AREA_CHOICES, required=False, label='Район', widget=forms.SelectMultiple)
    professional_role = forms.ChoiceField(choices=ROLES_CHOICES, required=False, label='Профессия')
    salary = forms.IntegerField(required=False, label='Зарплата от')
    currency = forms.ChoiceField(choices=CURRENCY_CHOICES, required=False, label='Валюта')
    only_with_salary = forms.BooleanField(required=False, label='Только с зарплатой')
    date_from = forms.DateField(
        required=False,
        label='C даты',
        widget=forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
        input_formats=["%Y-%m-%d"]
    )
    date_to = forms.DateField(
        required=False,
        label='До даты',
        widget=forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
        input_formats=["%Y-%m-%d"]
    )
    
    
    def to_json(self):
        cleaned_data = self.cleaned_data
        for i in cleaned_data:
            if i == 'date_from' and cleaned_data[i]:
                cleaned_data[i] = cleaned_data[i].strftime('%Y-%m-%d')
                continue
            
            if i == 'date_to' and cleaned_data[i]:
                cleaned_data[i] = cleaned_data[i].strftime('%Y-%m-%d')
                continue

            if not cleaned_data[i]:
                cleaned_data[i] = None
        return cleaned_data
    
    def __repr__(self) -> str:
        return repr(self.cleaned_data)
    
    

def get_choices(column, single_choice=False):
    ls = list(map(lambda a: (a, a), DataBase().get_all_options(column)))
    if single_choice:
        ls.insert(0, (None, 'Не указанно'))
    return ls

class VacancyFilterForm(forms.Form):
    experience = forms.ChoiceField(choices=get_choices(vacancy_table.c.experience, True), label='Опыт', required=False)
    area = forms.ChoiceField(choices=get_choices(vacancy_table.c.area, True), label='Место работы', required=False)
    employer = forms.ChoiceField(choices=get_choices(vacancy_table.c.employer, True), label='Компания', required=False)
    roles = forms.MultipleChoiceField(choices=get_choices(role_table.c.role), widget=forms.SelectMultiple, required=False, label='Профессия')
    salary_from = forms.IntegerField(required=False, label='Зарплата от')
    salary_to = forms.IntegerField(required=False, label='Зарплата до')
    skills = forms.MultipleChoiceField(choices=get_choices(skill_table.c.skill), widget=forms.SelectMultiple, required=False, label='Навыки')
    date_from = forms.DateField(
        required=False,
        label='C даты',
        widget=forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
        input_formats=["%Y-%m-%d"]
    )
    date_to = forms.DateField(
        required=False,
        label='До даты',
        widget=forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
        input_formats=["%Y-%m-%d"]

    )
    
    
    def to_json(self):
        cleaned_data = self.cleaned_data
        for i in cleaned_data:
            if i == 'date_from' and cleaned_data[i]:
                cleaned_data[i] = cleaned_data[i].strftime('%Y-%m-%d')
                continue
            
            if i == 'date_to' and cleaned_data[i]:
                cleaned_data[i] = cleaned_data[i].strftime('%Y-%m-%d')
                continue

            if not cleaned_data[i]:
                cleaned_data[i] = None
        return cleaned_data
    
    def __repr__(self) -> str:
        return repr(self.cleaned_data)
    