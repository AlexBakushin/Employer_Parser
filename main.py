# Импорт необходимых библиотек
import requests
import json
import psycopg2

# Список id компаний-работодателей
employers_id = [1740, 1942330, 2245, 4219, 2748, 3529, 23427, 4352, 3127, 49357, 39305]

# Пустые списки для данных компаний и их вакансий
data_employers = []
data_vacancies = []


class EmployerParser:
    """
    Класс для поиска вакинсий по каждому работодателю из списка компаний
    """

    def __init__(self, emp_id):
        """
        Инициация id компании
        :param emp_id: id компании
        """
        self.emp_id = emp_id

    def vacancy_filtering(self):
        """
        Метод для нахождения и фильтрации массива данных о вакансиях с hh.ru
        :return: Отфильтрованный и приведенный к общему шаблону массив с необходимой информацией об вакансиях
                 {'name': Название вакансии,
                  'url': ссылка на вакансию,
                  'salary_from': зарплата от...,
                  'salary_to': зарплата до...,
                  'experience': требуемый опыт,
                  'requirement_and_responsibility': требования и обязаности,
                  'employer': работодатель}
        """
        parametrs = {'per_page': 100}
        data_vac = json.loads(
            requests.get('https://api.hh.ru/vacancies?employer_id=' + str(self.emp_id), parametrs).content.decode())[
            'items']
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


class DBManager:
    """
    Класс для подключения с базе данных PostgreSQL
    """

    def __init__(self):
        """
        Инициация подключения к базе данных
        """
        self.conn = psycopg2.connect(host=user_db_info[0],
                                     database=user_db_info[1],
                                     user=user_db_info[2],
                                     password=user_db_info[3])
        self.cur = self.conn.cursor()

    def get_companies_and_vacancies_count(self):
        """
        Функция для получения списка всех компаний и количество вакансий у каждой компании
        :return: список
        """
        self.cur.execute("SELECT employer_name, vacancy_count FROM employer")
        rows = self.cur.fetchall()
        for row in rows:
            print(row)

    def get_all_vacancies(self):
        """
        Функция для получения списка всех вакансий с указанием названия компании, названия вакансии и зарплаты
        и ссылки на вакансию
        :return: список
        """
        self.cur.execute("SELECT  employer, vacancy_name,  salary_from, salary_to, url FROM vacancy")
        rows = self.cur.fetchall()
        for row in rows:
            print(row)

    def get_avg_salary(self):
        """
        Функция для получения средней зарплаты по вакансиям
        :return: список
        """
        self.cur.execute("SELECT  salary_from, salary_to FROM vacancy")
        rows = self.cur.fetchall()
        result = 0
        cycle = 0
        for row in rows:
            if row[0] is not None and row[1] is not None:
                res = (row[0] + row[1]) / 2
                result += res
                cycle += 1
        result /= cycle
        result_round = int(result + (0.5 if result > 0 else -0.5))
        print(f'Средняя зарплата: {result_round} руб.')
        return result_round

    def get_vacancies_with_higher_salary(self):
        """
        Функция для получения  списка всех вакансий, у которых зарплата выше средней по всем вакансиям
        :return: список
        """
        avg_salary = int(self.get_avg_salary())
        self.cur.execute("SELECT * FROM vacancy")
        rows = self.cur.fetchall()
        for row in rows:
            if row[3] is not None and row[4] is not None:
                if row[3] > avg_salary and row[4] > avg_salary:
                    print(row)

    def get_vacancies_with_keyword(self, word):
        """
        Функция для получения  списка всех вакансий, в названии которых содержатся переданные в метод слова
        :return: список
        """
        self.cur.execute("SELECT * FROM vacancy")
        rows = self.cur.fetchall()
        for row in rows:
            if row[6].find(word) != -1 or row[1].find(word) != -1:
                print(row)


def employer_filtering():
    """
    Функция для нахождения и фильтрации массива данных о вакансиях с hh.ru и записи их в файл
    :return: Отфильтрованный и приведенный к общему шаблону массив с необходимой информацией об вакансиях
            {'name': Название компании,
            'description': Описание компании,
            'area': Город, где находится глав. офис,
            'hh.ru_url': ссылка на кампанию на сайте hh.ru,
            'site_url': ссылка на вебсайт компании,
            'vacancy_count': количество вакансий компании}
    """
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
            '<li>', '').replace(  # Это символы исключения, нужны для нормального отображения описания компаний
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
    """
    Функция для подключения к PostgreSQL, создания в ней таблиц  и заполнения их данными, полученными с сайта
    :return:
    """
    # Подключение к базе данных
    conn = psycopg2.connect(
        host=user_db_info[0],
        database=user_db_info[1],
        user=user_db_info[2],
        password=user_db_info[3])
    try:
        with conn:
            with conn.cursor() as cur:
                cycle_1 = 1
                cycle_2 = 1

                # Создание таблицы для вакансий
                create_table_vacancy = """CREATE TABLE vacancy(
                                    vacancy_id int PRIMARY KEY,
                                    vacancy_name varchar(100) NOT NULL,
                                    url varchar(100),
                                    salary_from int,            
                                    salary_to int,
                                    experience text,
                                    requirement_and_responsibility text,
                                    employer varchar(100) REFERENCES employer(employer_name) NOT NULL
                                );"""

                # Создание таблицы для компаний
                create_table_employer = """CREATE TABLE employer(
                                    employer_id int NOT NULL,
                                    employer_name varchar(100) PRIMARY KEY,
                                    description text,
                                    area varchar(100),
                                    hh_ru_url varchar(100),
                                    site_url varchar(100),
                                    vacancy_count int
                                );"""

                cur.execute(create_table_employer)
                cur.execute(create_table_vacancy)

                # Заполнение таблицы с информацией об компаниях
                for employer in data_employers:
                    cur.execute("INSERT INTO employer VALUES (%s, %s, %s, %s, %s, %s, %s)", (
                        cycle_1, employer.get('name'),
                        employer.get('description'),
                        employer.get('area'),
                        employer.get('hh.ru_url'),
                        employer.get('site_url'),
                        employer.get('vacancy_count')))
                    cycle_1 += 1

                # Заполнение таблицы с информацией об вакансиях
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

                    # Опциональный выбор вывода в консоль
                # cur.execute('SELECT * FROM employer')             # Вывести полную таблицу с компаниями (11 шт.)
                cur.execute('SELECT * FROM vacancy')  # Вывести полную таблицу с вакансиями (1100 шт.)

                conn.commit()
                rows = cur.fetchall()

                for row in rows:
                    print(row)

    finally:
        conn.close()


def vacancy_parser():
    """
    Функция для инициации в класс компаний для получения по каждой информации об их вакансиях и записи ее в файл
    """
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


def user_interaction():
    """
    Функция для работы с пользователем
    :return: Параметры поиска вакансий
    """
    # Запрос host
    user_host = input('Введите host вашей базы данных:\n')
    # Запрос названия базы данных
    user_database = input('Введите название для вашей базы данных: \n')
    # Запрос имени аккаунта в PostgreSQL
    user_name = input('Введите имя вашего аккаунта PostgreSQL:\n')
    # Запрос пароля от аккаунта в PostgreSQL для подключения к базе данных
    user_password = input('Введите пароль от вашего аккаунта PostgreSQL:\n')
    # Создание параметров пользователя
    user_info = (user_host, user_database, user_name, user_password)
    return user_info


user_db_info = user_interaction()

# Поиск и запись в файлы информации по компаниям и их вакансиям
vacancy_parser()                                           # - (включить 1 раз)
# Создания и заполнение таблиц PostgreSQL данными и информацией об компаниях и их вакансиях
upload_databace()                                          # - (включить 1 раз)

# Цикл для работы программы с пользователем
while True:
    # Инициация класса для работы с базой данных
    manager = DBManager()
    command = input("\nВыберите одну из функций:\n"
                    "1 - Получить список всех компаний и количество вакансий у каждой компании\n"
                    "2 - Получить список всех вакансий с указанием названия компании,"
                    " названия вакансии и зарплаты и ссылки на вакансию\n"
                    "3 - Получить среднюю зарплату по вакансиям\n"
                    "4 - Получить список всех вакансий, у которых зарплата выше средней по всем вакансиям\n"
                    "5 - Получить список всех вакансий, в названии которых содержатся переданные в метод слова\n"
                    "exit - Завершить программу\n"
                    "\nВведите команду: \n")
    if command == "exit":
        break
    elif command == '1':
        manager.get_companies_and_vacancies_count()
    elif command == '2':
        manager.get_all_vacancies()
    elif command == '3':
        manager.get_avg_salary()
    elif command == '4':
        manager.get_vacancies_with_higher_salary()
    elif command == '5':
        manager.get_vacancies_with_keyword(input('Введите ключевое слово:\n'))
