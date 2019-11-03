from bs4 import BeautifulSoup as bs
import requests
from pprint import pprint
import re
import time
import pandas as pd

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)


# ============= hh =============
def parsing_hh_page(vacances_list, vacs):
    for vac in vacances_list:

        vac_data = {}
        # поиск названия вакансии
        vac_name = vac.find('a', {'class': 'bloko-link HH-LinkModifier'})
        # поиск выдает несколько результатов None (реклама), которые мешают подобраться к данным
        # поэтому делаю такую проверку
        if vac_name is None:
            continue
        else:
            # выдает ссылку, но в ней указан город поиска.
            # отдельно писать обработчик ссылки не стал тк идея показалась сомнительной
            vac_link = vac_name['href']  # ссылка на вакансию
            vac_name = vac_name.getText()
        # поиск зарплаты
        salary = vac.find('div', {'class': 'vacancy-serp-item__compensation'})

        if not salary:
            min_salary = None
            max_salary = None
            money_type = None
        else:
            salary = salary.getText().replace(u'\xa0', u'')
            salary = re.split('-| ', salary)
            money_type = salary[-1]

            if salary[0] == 'от':
                min_salary = salary[1]
                max_salary = None
            elif salary[0] == 'до':
                min_salary = None
                max_salary = salary[1]
            else:
                min_salary = salary[0]
                max_salary = salary[1]

        # локация вакансии
        vac_city = vac.find('span', {'class': 'vacancy-serp-item__meta-info'}).getText().split(',')[0]

        vac_data['name'] = vac_name
        vac_data['min_salary'] = min_salary
        vac_data['max_salary'] = max_salary
        vac_data['money_type'] = money_type
        vac_data['vac_link'] = vac_link
        vac_data['site'] = main_link
        vac_data['city'] = vac_city

        vacs.append(vac_data)

    return vacs


def hh_vac_parser(headers, vacs):  # result_list - передаем список куда добавлять данные
    vacancy_name = vacancy.replace(' ', '+')
    page = 0

    while True:
        html = requests.get(main_link + f"/search/vacancy?L_is_autosearch=false&area=113&clusters=true&"
                                        f"enable_snippets=true&text={vacancy_name}&page={page}",
                            headers=headers).text
        parsed_html = bs(html, 'lxml')

        # Все вакансии находятся в классе vacancy-serp, попробуем их найти
        vacances_block = parsed_html.find('div', {'class': 'vacancy-serp'})
        vacances_list = vacances_block.findChildren(recursive=False)
        parsing_hh_page(vacances_list, vacs)
        # Ожидание
        time.sleep(1)

        # Критерий остановки цикла - отсутствие кнопки "дальше"
        is_next = parsed_html.find('a', {'class': 'HH-Pager-Controls-Next'})
        if is_next is None:
            break
        page += 1
    return vacs  # result_list


# ============= SuperJob =============
def parsing_sj_page(vac_list, vacs):
    for vac in vac_list:
        vac_data = {}
        # поиск названия вакансии
        vacancy_name = vac.find('div', {'class': '_3mfro CuJz5 PlM3e _2JVkc _3LJqf'}).getText()
        vacancy_link = main_link_2 + vac.find('div', {'class': '_3mfro CuJz5 PlM3e _2JVkc _3LJqf'}).findParent()['href']
        vacancy_city = vac.find('span', {'class': '_3mfro _9fXTd _2JVkc _3e53o _3Ll36'}) \
            .next_sibling.next_sibling.text.split(',')[0]
        # pprint(vacancy_city)
        # тут полным ходом идут эксперементы поиска, прошу понять и простить
        vacancy_salary_find = vac.find('span', {
            'class': '_3mfro _2Wp8I f-test-text-company-item-salary PlM3e _2JVkc _2VHxz'}).text
        salary = re.split(u'\xa0', vacancy_salary_find)

        if salary[0] == 'По договорённости':
            min_salary = None
            max_salary = None
            money_type = None
        else:
            # тут пока оставю символьное обозначение для последующей доработки
            money_type = salary[-1]

            if salary[0] == 'от':
                min_salary = salary[1] + salary[2]
                max_salary = None
            elif salary[2] == '—':
                min_salary = salary[0] + salary[1]
                max_salary = salary[3] + salary[4]
            else:
                min_salary = salary[0] + salary[1]
                max_salary = None

        vac_data['name'] = vacancy_name
        vac_data['min_salary'] = min_salary
        vac_data['max_salary'] = max_salary
        vac_data['money_type'] = money_type
        vac_data['vac_link'] = vacancy_link
        vac_data['site'] = main_link_2
        vac_data['city'] = vacancy_city

        vacs.append(vac_data)
    return vacs


def sj_vac_parser(headers, vacs):
    vacancy_name = vacancy.replace(' ', '%20')

    start_search = f'/vacancy/search/?keywords={vacancy_name}&geo%5Bc%5D%5B0%5D=1'

    while True:

        html = requests.get(f'{main_link_2}{start_search}',
                            headers=headers).text
        parsed_html = bs(html, 'lxml')
        vac_list = parsed_html.findAll('div', {'class': '_3zucV _2GPIV f-test-vacancy-item i6-sc _3VcZr'})
        parsing_sj_page(vac_list, vacs)

        try:
            start_search = parsed_html.find('a', {'class': 'f-test-button-dalshe'})['href']
        except TypeError:
            break

        time.sleep(1)

    return vacs


vacancy = 'начальник отдела маркетинга'
headers = {'User-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) '
                         'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 '
                         'Safari/537.36'}
main_link = 'https://hh.ru'
main_link_2 = 'https://www.superjob.ru'
vacs = []

hh_vac_parser(headers, vacs)
sj_vac_parser(headers, vacs)

df = pd.DataFrame(vacs)
pprint(df)
