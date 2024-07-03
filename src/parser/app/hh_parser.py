import requests
from selenium import webdriver
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support import expected_conditions as EC
import logging

from common.models import Vacancy, Resume, VacancyRequest, ResumeRequest
# from models import Vacancy, Resume, VacancyRequest, ResumeRequest
class HH_parser:
    vacancy_url = "https://api.hh.ru/vacancies"
    resume_url = "https://hh.ru/search/resume"
    headers = {"HH-User-Agent": "newapp/1.0 (svovoniks@gmail.com)"}

    def get_vacancies(self, template: VacancyRequest) -> list[Vacancy]:
        rs = requests.get(self.vacancy_url, headers=self.headers, json=template.json)
        if not rs.status_code == 200:
            print("Error")
            return []
        
        vacancies = self._get_vacancy_form_page(0, template=template)
        
        logging.info(rs.json()['pages'])
        for i in range(1, rs.json()['pages']):
            logging.info(f"Getting page {i}")
            vacancies.extend(self._get_vacancy_form_page(i, template))
        
        return list(filter(lambda a: a != None, vacancies))
    
    def _get_vacancy_form_page(self, page_number: int, template: VacancyRequest):
        rs = requests.get(self.vacancy_url+template.with_page(page_number).build_suburl(), headers=self.headers)

        if not rs.status_code == 200:
            print("Error")
            return []
            
        return [self._get_vacancy_by_id(vacancy['id']) for vacancy in rs.json()["items"]]

    def _get_vacancy_by_id(self, vacancy_id: str):
        rs = requests.get(f'{self.vacancy_url}/{vacancy_id}', headers=self.headers)

        if not rs.status_code == 200:
            print('Error')
            print(rs.text)
            return None
        
        return Vacancy.from_json(rs.json())

    def get_resumes(self, template: ResumeRequest):
        firefoxProfile = FirefoxProfile()
        firefoxProfile.set_preference('permissions.default.stylesheet', 2)
        firefoxProfile.set_preference('permissions.default.image', 2)
        firefoxProfile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so','false')
        firefoxProfile.set_preference("javascript.enabled", False)
        options = Options()
        options.profile = firefoxProfile
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        selenium_driver = Service()
        
        browser = webdriver.Firefox(options=options,service=selenium_driver)
        url = self.resume_url+template.build_suburl()
        browser.get(url)
        
        mx_page = None
        
        try:
            pager = browser.find_element(By.XPATH, '//div[@class="pager" and @data-qa="pager-block"]')
            page_numbers = pager.find_elements(By.XPATH, './/a[@data-qa="pager-page"]')
            page_numbers = [int(i.text) for i in page_numbers]
            mx_page = max(page_numbers)
        except:
            mx_page = -1
        
        resumes = self._get_resumes_from_page(browser)
        mx_page = min(mx_page, 2)
        for i in range(1, mx_page):
            browser.get(url+f"&page={i}")
            resumes.extend(self._get_resumes_from_page(browser))
            if len(resumes) >= 50:
                break
        
        browser.quit()
        
        return resumes
    
    def _get_resumes_from_page(self, browser: WebDriver):
        resumes = []
        hrefs = None
        
        try:
            resume_cards = browser.find_elements(By.XPATH, "//a[@data-qa='serp-item__title']")
            hrefs = [card.get_attribute('href') for card in resume_cards]
        except:
            return []
        
        for i in hrefs:
            browser.get(i)
            logging.info(f"Getting resume {i}")
            resumes.append(Resume().from_browser(browser))
        
        return resumes
    