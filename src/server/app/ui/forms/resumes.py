from django import forms
from common.database import DataBase
from common.database import resume_table, skill_table, role_table

GENDER_CHOICES = (
    ('unknown', 'Не имеет значения'),
    ('male', 'Мужской'),
    ('female', 'Женский'),
)

EXPERIENCE_CHOICES = (
    (None, 'Любой опыт'),
    ('noExperience', 'Нет опыта'),
    ('between1And3', 'От 1 года до 3 лет'),
    ('between3And6', 'От 3 до 6 лет'),
    ('moreThan6', 'Более 6 лет'),
)

skills = []
with open('ui/dictionaries/skills.txt', 'r', encoding="utf-8") as file:
    skills = file.readlines()

SKILLS_CHOICES = [tuple(i.strip().split(' ', maxsplit=1)) for i in skills]

ver_skills = []
with open('ui/dictionaries/ver_skills.txt', 'r', encoding="utf-8") as file:
    ver_skills = file.readlines()

VER_SKILLS_CHOICES = [tuple(i.strip().split(' ', maxsplit=1)) for i in ver_skills]

roles = []
with open('ui/dictionaries/roles.txt', 'r', encoding="utf-8") as file:
    roles = file.readlines()

ROLES_CHOICES = [tuple(i.strip().split(' ', maxsplit=1)) for i in roles]

areas = []
with open('ui/dictionaries/areas.txt', 'r', encoding="utf-8") as file:
    areas = file.readlines()

AREA_CHOICES = [tuple(i.strip().split(' ', maxsplit=1)) for i in areas]

SEARCH_STATUS_CHOICES = (
    ('unknown', 'Не имеет значения'),
    ('not_looking_for_job', 'Не ищет работу'),
    ('looking_for_offers', 'Рассматривает предложения'),
    ('active_search', 'Активно ищет работу'),
    ('has_job_offer', 'Предложили работу, решает'),
    ('accepted_job_offer', 'Вышел на новое место'),
)



class ResumeRequestForm(forms.Form):
    text = forms.CharField(max_length=255, required=False, label='Название должености')
    experience = forms.MultipleChoiceField(choices=EXPERIENCE_CHOICES, required=False, widget=forms.SelectMultiple, label='Опыт работы')
    gender = forms.ChoiceField(choices=GENDER_CHOICES, required=False, label='Пол')
    age_from = forms.IntegerField(required=False, label='Возраст от')
    age_to = forms.IntegerField(required=False, label='Возраст до')
    roles = forms.MultipleChoiceField(choices=ROLES_CHOICES, widget=forms.SelectMultiple, required=False, label='Профессия')
    salary_from = forms.IntegerField(required=False, label='Зарплата от')
    salary_to = forms.IntegerField(required=False, label='Зарплата до')
    skills = forms.MultipleChoiceField(choices=SKILLS_CHOICES, widget=forms.SelectMultiple, required=False, label='Навыки')
    area = forms.MultipleChoiceField(choices=AREA_CHOICES, widget=forms.SelectMultiple, required=False, label='Район')
    search_status = forms.MultipleChoiceField(choices=SEARCH_STATUS_CHOICES, widget=forms.SelectMultiple, required=False, label='Статус поиска')

    def to_json(self):
        cleaned_data = self.cleaned_data
        for i in cleaned_data:
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

class ResumeFilterForm(forms.Form):
    experience_from = forms.IntegerField(label='Опыт от', required=False)
    experience_to = forms.IntegerField(label='Опыт до', required=False)
    gender = forms.ChoiceField(choices=get_choices(resume_table.c.gender, True), required=False, label='Пол')
    age_from = forms.IntegerField(required=False, label='Возраст от')
    age_to = forms.IntegerField(required=False, label='Возраст до')
    roles = forms.MultipleChoiceField(choices=get_choices(role_table.c.role), widget=forms.SelectMultiple, required=False, label='Профессия')
    salary_from = forms.IntegerField(required=False, label='Зарплата от')
    salary_to = forms.IntegerField(required=False, label='Зарплата до')
    skills = forms.MultipleChoiceField(choices=get_choices(skill_table.c.skill), widget=forms.SelectMultiple, required=False, label='Навыки')
    search_status = forms.ChoiceField(choices=get_choices(resume_table.c.search_status), required=False, label='Статус поиска')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update()
    
    def update(self):
        self.fields['gender'] = forms.MultipleChoiceField(choices=get_choices(resume_table.c.gender), widget=forms.SelectMultiple, required=False, label='Пол')
        self.fields['roles'] = forms.MultipleChoiceField(choices=get_choices(role_table.c.role), widget=forms.SelectMultiple, required=False, label='Профессия')
        self.fields['skills'] = forms.MultipleChoiceField(choices=get_choices(skill_table.c.skill), widget=forms.SelectMultiple, required=False, label='Навыки')
        self.fields['search_status'] = forms.MultipleChoiceField(choices=get_choices(resume_table.c.search_status), widget=forms.SelectMultiple, required=False, label='Статус поиска')
    
    def to_json(self):
        cleaned_data = self.cleaned_data
        for i in cleaned_data:
            if not cleaned_data[i]:
                cleaned_data[i] = None
        return cleaned_data
    
    def __repr__(self) -> str:
        return repr(self.cleaned_data)
    
    