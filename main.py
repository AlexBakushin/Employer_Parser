# import psycopg2
#
#
# conn = psycopg2.connect(
#     host='localhost',
#     database='test',
#     user='postgres',
#     password='2202'
# )
# try:
#     with conn:
#         with conn.cursor() as cur:
#             cur.execute("INSERT INTO user_acount VALUES (%s, %s)", (6, "Len"))
#             cur.execute('SELECT * FROM user_acount')
#
#             rows = cur.fetchall()
#
#             for row in rows:
#                 print(row)
#
# finally:
#     conn.close()


import requests
import json

employers_id = [1740, 1942330, 2245, 4219, 2748, 3529, 23427, 4352, 3127, 49357, 39305]

data_employers = []
data_vacancies = []


class EmployerParser:

    def __init__(self, emp_id):
        self.emp_id = emp_id

    def vacancy_filtering(self):
        """
        Метод для фильтрации массива данных о вакансиях с hh.ru
        :return: Отфильтрованный и приведенный к общему шаблону массив с необходимой информацией об вакансиях
        """
        data_vac = json.loads(
            requests.get('https://api.hh.ru/vacancies?employer_id=' + str(self.emp_id)).content.decode())['items']
        filtered_vacancies = []
        for vac in data_vac:
            name_vacancy = vac.get('name')
            url_vacancy = vac.get('alternate_url')
            if vac.get('salary') is None:
                salary_vacancy = 'По договоренности'
            else:
                if vac.get("salary").get("from") is None:
                    salary_vacancy = f'от {0} до {vac.get("salary").get("to")}'
                elif vac.get("salary").get("to") is None:
                    salary_vacancy = f'от {vac.get("salary").get("from")} до {0}'
                else:
                    salary_vacancy = f'от {vac.get("salary").get("from")} до {vac.get("salary").get("to")}'
            experience_vacancy = vac.get('experience').get('name')
            requirement = f"Требования: {vac.get('snippet').get('requirement')}\n" \
                          f"Обязаности: {vac.get('snippet').get('responsibility')}"
            requirement_and_responsibility = requirement.replace('\n', '').replace('<highlighttext>', '').replace(
                '</highlighttext>', '')
            filtered_vacancy = {'name': name_vacancy,
                                'url': url_vacancy,
                                'salary': salary_vacancy,
                                'experience': experience_vacancy,
                                'requirement_and_responsibility': requirement_and_responsibility}
            filtered_vacancies.append(filtered_vacancy)
        return filtered_vacancies


def employer_filtering():
    for emp_id in employers_id:
        data_emp = json.loads(requests.get('https://api.hh.ru/employers/' + str(emp_id)).content.decode())
        employer_name = data_emp.get("name")
        description = data_emp.get("description")
        employer_description = description.replace(
            '<p>', '').replace(
            '<strong>', '').replace(
            '</strong>', '').replace(
            '</p>', '').replace(
            '<ul>', '').replace(
            '</ul>', '').replace(
            '<li>', '').replace(
            '</li>', '').replace(
            '&quot;', '').replace(
            '\r\n', '').replace(
            '&ndash;', '').replace(
            '&nbsp;', '').replace(
            '&raquo;', '').replace(
            '&laquo;', '').replace(
            '</em>', '').replace(
            '<br />', '')
        employer_area = data_emp.get("area").get("name")
        vacancy_count = data_emp.get("open_vacancies")
        url_hh = data_emp.get("alternate_url")
        site_url = data_emp.get("site_url")
        filtered_employer = {'name': employer_name,
                             'description': employer_description,
                             'area': employer_area,
                             'hh.ru_url': url_hh,
                             'site_url': site_url,
                             'vacancy_count': vacancy_count}
        data_employers.append(filtered_employer)

    with open('data_employers.json', 'w', encoding='utf-8') as file:
        json.dump(data_employers, file, ensure_ascii=False)


employer_filtering()

names_vac = []
for i in range(len(employers_id)):
    names_vac.append(f'vacancy{i}')
    names_vac[i] = EmployerParser(employers_id[i])
    data_vacancies.append(names_vac[i].vacancy_filtering())

with open('json-vacancies.json', 'w', encoding='utf-8') as file:
    json.dump(data_vacancies, file, ensure_ascii=False)
