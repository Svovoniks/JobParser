from datetime import datetime
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
import re

curency_conversion_map = {
    'AZN': 0.019478,
    'BYR': 0.036613,
    'EUR': 0.010668,
    'GEL': 0.032117,
    'KGS': 0.992093,
    'USD': 0.011458,
    'KZT': 5.331059,
    'UZS': 144.367016,
    'RUR': 1.0,
    'UAH': 0.464619
}

curency_char_conversion_map = {
    '₼': 0.019478,
    'Br': 0.036613,
    '€': 0.010668,
    '₾': 0.032117,
    'сом': 0.992093,
    '$': 0.011458,
    '₸': 5.331059,
    "so'm": 144.367016,
    '₽': 1.0,
    '₴': 0.464619
}

def try_get(json, key, on_error=None):
    try:
        return json[key]
    except:
        return None

class Vacancy:
    def __init__(self, 
                vacancy_id, 
                name, 
                area, 
                salary_from, 
                salary_to, 
                currency,
                is_open,
                published_at,
                employer_id,
                employer,
                is_remote,
                experience,
                professional_roles,
                skills,
                salary_converted = False
                ) -> None:
        self.vacancy_id = vacancy_id
        self.name = name
        self.area = area
        self.salary_from = salary_from
        self.salary_to = salary_to
        self.currency = currency
        self.is_open = is_open
        self.published_at = published_at
        self.employer_id = employer_id
        self.employer = employer
        self.is_remote = is_remote
        self.experience = experience
        self.professional_roles = professional_roles
        self.skills = skills
        if not salary_converted:
            self.salary_from = Vacancy.convert_currency(self.salary_from, self.currency)
            self.salary_to = Vacancy.convert_currency(self.salary_to, self.currency)
    
    def convert_currency(salary, currency):
        if currency != None and salary != None:
            return salary // curency_conversion_map[currency]
        else:
            return None
    
    def __repr__(self) -> str:
        return f'Vacancy(vacancy_id={self.vacancy_id}, name={self.name}, area={self.area}, salary_from={self.salary_from}, salary_to={self.salary_to} currency={self.currency}, is_open={self.is_open}, published_at={self.published_at}, employer_id={self.employer_id}, employer={self.employer}, is_remote={self.is_remote}, professional_roles={self.professional_roles}), skills={self.skills}'
    
    @staticmethod
    def from_json(json):
        date = try_get(json, 'published_at')
        if date:
            date = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S%z')
        vacancy = Vacancy(
            vacancy_id=try_get(json, 'id'),
            name=try_get(json, 'name'),
            area=try_get(try_get(json, 'area'), 'name'),
            salary_from=try_get(try_get(json, 'salary'), 'from'),
            salary_to=try_get(try_get(json, 'salary'), 'to'),
            currency=try_get(try_get(json, 'salary'), 'currency'),
            is_open=try_get(try_get(json, 'type'), 'id') == 'open',
            published_at=date,
            employer_id=try_get(try_get(json, 'employer'), 'id'),
            employer=try_get(try_get(json, 'employer'), 'name'),
            professional_roles=list(map(lambda a: a["name"], try_get(json, 'professional_roles', on_error=[]))),
            skills=list(map(lambda a: a['name'], try_get(json, 'key_skills', on_error=[]))),
            is_remote=try_get(json, 'schedule') == 'remote',
            experience=try_get(try_get(json, 'experience'), 'name')
        )
        
        return vacancy

class VacancyRequest:
    def __init__(self, json: dict) -> None:
        self.json = json
        self.json['per_page'] = 20
    
    def with_page(self, page_number):
        self.json['page'] = page_number
        return self
    
    def process_text(self, text: str):
        return text.replace(" ", "+")
    
    def build_suburl(self):
        def_url = f"?&exp_period=all_time&ored_clusters=true&order_by=relevance&search_period=0&logic=normal&pos=full_text&hhtmFrom=resume_search_result&hhtmFromLabel=resume_search_line"
        
        for i in self.json.keys():
            if i == "text" and self.json[i]:
                def_url += f"&{i}={self.process_text(self.json[i])}"
                continue
            
            if type(self.json[i]) == list:
                for j in self.json[i]:
                    def_url += f"&{i}={j}"
            elif self.json[i]:
                def_url += f"&{i}={self.json[i]}"
        
        return def_url
    
    def __getitem__(self, key):
        return self.json[key]

class Resume:
    def __init__(self,
                resume_id: str = None,
                gender: str = None,
                age: int = None,
                salary: int = None,
                experience: int = None,
                skills: list[str] = None,
                search_status: str = None,
                roles_list: list[str] = None
                ) -> None:
        self.resume_id = resume_id
        self.gender = gender
        
        if self.gender == 'Мужчина':
            self.gender = 'Male'
        elif self.gender == 'Женщина':
            self.gender = 'Female'
        
        self.age = age
        self.salary = salary
        self.experience = experience
        self.skills = skills if skills != None else []
        self.search_status = search_status
        self.roles_list = roles_list if roles_list != None else []

    def from_browser(self, browser: WebDriver):
        rx = r'resume/([^\?]+)?'
        resume_id = re.search(rx, browser.current_url)[1]
        
        try:
            gender = browser.find_element(By.XPATH, '//span[@data-qa="resume-personal-gender"]').text
        except:
            gender = None
        try:
            age = browser.find_element(By.XPATH, '//span[@data-qa="resume-personal-age"]').text
            age = int(re.search(r'\d+', age)[0])
        except:
            age = None
        try:
            salary_str = browser.find_element(By.XPATH, '//span[@data-qa="resume-block-salary"]').text
            salary = int(re.sub(r'[^\d]', '', salary_str))
            for i in curency_char_conversion_map.keys():
                if i in salary_str:
                    salary //= curency_char_conversion_map[i]
                
        except:
            salary = None
        try:
            experience_list = browser.find_elements(By.XPATH, "//span[@class='resume-block__title-text resume-block__title-text_sub']//span")
            experience = None
            if len(experience_list) >= 1:
                experience_str = experience_list[0].text
                if 'year' in experience_str or 'год' in experience_str or 'лет' in experience_str:
                    experience = int(re.sub(r'[^\d]', '', experience_str))
            
        except:
            experience = None
        try:
            skills = browser.find_elements(By.XPATH, "//span[@class='bloko-tag__section bloko-tag__section_text' and @data-qa='bloko-tag__text']")
            skills = [skill.text for skill in skills]
        except:
            skills = None
        try:
            search_status = browser.find_element(By.XPATH, "//span[@data-qa='job-search-status']").text
        except:
            search_status = None
        try:
            roles_div = browser.find_element(By.XPATH, "//div[@class='bloko-gap bloko-gap_bottom']/span[@data-qa='resume-block-specialization-category']/following-sibling::ul")

            roles_li = roles_div.find_elements(By.XPATH, "./li[@class='resume-block__specialization']")

            roles_list = [li.text for li in roles_li]
        except:
            roles_list = None
        
        # print(f"resume_id: {resume_id}, gender: {gender}, age: {age}, salary: {salary}, experiense: {experiense}, skills: {skills}, search_status: {search_status}, roles_list: {roles_list}")

        return Resume(
            resume_id=resume_id,
            gender=gender,
            age=age,
            salary=salary,
            experience=experience,
            skills=skills,
            search_status=search_status,
            roles_list=roles_list,
        )
    
    def __repr__(self) -> str:
        return f"Resume(resume_id={self.resume_id}, gender={self.gender}, age={self.age}, salary={self.salary}, experiense={self.experiense}, skills={self.skills}, search_status={self.search_status})"

class ResumeRequest:
    def __init__(self, json: dict) -> None:
        self.json = json
    
    def process_text(self, text: str):
        return text.replace(" ", "+")
    
    def build_suburl(self):
        def_url = f"?&exp_period=all_time&ored_clusters=true&order_by=relevance&search_period=0&logic=normal&pos=full_text&hhtmFrom=resume_search_result&hhtmFromLabel=resume_search_line"
        
        for i in self.json.keys():
            if i == "text" and self.json[i]:
                def_url += f"&{i}={self.process_text(self.json[i])}"
                continue
            
            if type(self.json[i]) == list:
                for j in self.json[i]:
                    def_url += f"&{i}={j}"
            elif self.json[i]:
                def_url += f"&{i}={self.json[i]}"
        
        return def_url
    
    def __getitem__(self, key):
        return self.json[key]
    

class Task:
    def __init__(self, idx, json_str, status, request_date) -> None:
        self.idx = idx
        self.json_str = json_str 
        self.status = status
        self.request_date = request_date