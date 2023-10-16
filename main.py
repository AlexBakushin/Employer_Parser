import requests
import json
import psycopg2

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
                salary_vacancy_from = None
                salary_vacancy_to = None
            else:
                salary_vacancy_from = vac.get("salary").get("from")
                salary_vacancy_to = vac.get("salary").get("to")
            experience_vacancy = vac.get('experience').get('name')
            requirement = f"Требования: {vac.get('snippet').get('requirement')}\n" \
                          f"Обязаности: {vac.get('snippet').get('responsibility')}"
            requirement_and_responsibility = requirement.replace('\n', '').replace('<highlighttext>', '').replace(
                '</highlighttext>', '')
            employer = vac.get('employer').get('name')
            filtered_vacancy = {'name': name_vacancy,
                                'url': url_vacancy,
                                'salary_from': salary_vacancy_from,
                                'salary_to': salary_vacancy_to,
                                'experience': experience_vacancy,
                                'requirement_and_responsibility': requirement_and_responsibility,
                                'employer': employer}
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
            '\xa0', '').replace(
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


def upload_databace():
    conn = psycopg2.connect(
        host='localhost',
        database='hh.ru',
        user='postgres',
        password='2202'
    )
    try:
        with conn:
            with conn.cursor() as cur:
                cycle_1 = 1
                cycle_2 = 1

                create_table_vacancy = """CREATE TABLE vacancy(
                                    vacancy_id int PRIMARY KEY,
                                    name varchar(100) NOT NULL,
                                    url varchar(100),
                                    salary_from int,
                                    salary_to int,
                                    experience text,
                                    requirement_and_responsibility text,
                                    employer varchar(100) REFERENCES employer(name) NOT NULL
                                );"""

                create_table_employer = """CREATE TABLE employer(
                                    employer_id int NOT NULL,
                                    name varchar(100) PRIMARY KEY,
                                    description text,
                                    area varchar(100),
                                    hh_ru_url varchar(100),
                                    site_url varchar(100),
                                    vacancy_count int
                                );"""

                cur.execute(create_table_employer)
                cur.execute(create_table_vacancy)

                for employer in data_employers:
                    cur.execute("INSERT INTO employer VALUES (%s, %s, %s, %s, %s, %s, %s)", (
                        cycle_1, employer.get('name'),
                        employer.get('description'),
                        employer.get('area'),
                        employer.get('hh.ru_url'),
                        employer.get('site_url'),
                        employer.get('vacancy_count')))
                    cycle_1 += 1

                for vacancy in data_vacancies:
                    cur.execute("INSERT INTO vacancy VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (
                        cycle_2, vacancy.get('name'),
                        vacancy.get('url'),
                        vacancy.get('salary_from'),
                        vacancy.get('salary_to'),
                        vacancy.get('experience'),
                        vacancy.get('requirement_and_responsibility'),
                        vacancy.get('employer')))
                    cycle_2 += 1

                # cur.execute('SELECT * FROM employer')
                # cur.execute('SELECT * FROM vacancy')

                conn.commit()
                rows = cur.fetchall()

                for row in rows:
                    print(row)

    finally:
        conn.close()


employer_filtering()

names_vac = []
for i in range(len(employers_id)):
    names_vac.append(f'vacancy{i}')
    names_vac[i] = EmployerParser(employers_id[i])
    vacancy = names_vac[i].vacancy_filtering()
    for vac in vacancy:
        data_vacancies.append(vac)

with open('json-vacancies.json', 'w', encoding='utf-8') as file:
    json.dump(data_vacancies, file, ensure_ascii=False)

upload_databace()
