***Employer_Parser***
===

Это программа для быстрого получения информации об компаниях-работодателях и их вакансиях.

Выбранные мною компании: Яндекс, Пятерочка, Росгосстрах, Tele2, Ростелеком, СБЕР, РЖД, Почта РФ, Мегафон, Магнит и Гаспром Нефть

Программа поддерживает поиск по ключевому слову (название профессии).

`Нюанс` - Поиск по ключевому слову производится в списке уже выбранных вакансий (по 100 последних от каждой компании)

На данный момент программе доступно использование сайта [`Head Hanter`](hh.ru).

Также программа подлючается к вашей базе данных PostgreSQL. Для этого нужно будет ввести необходимые для этого данные: host name, название базы данных, имя и пароль аккаунта.

---
В программе предусмотренны следующие функции:
-
1.  Получение списка всех компаний и количество вакансий у каждой компании.

2.  Получение списка всех вакансий с указанием названия компании, названия вакансии и зарплаты и ссылки на вакансию.

3.  Получение средней зарплаты по вакансиям.

4.  Получение списка всех вакансий, у которых зарплата выше средней по всем вакансиям.

5.  Получение списка всех вакансий, в названии которых содержится переданное в метод слово.

---
**Ход работы:**
-
1. При первом использовании программы убедитесь, что функции `vacancy_parser()` и `upload_databace()`  в строках `317` и `319` , включены (отсутсвует знак `#`).

   После первого запуска создания таблиц эти функции следует отключить во избежания лишней траты времени и появления ошибок.


2. После завершения этапа поиска информации в консоль будет выведена информация, либо об компаниях, либо об их вакансиях.

    Выбрать вариант можно в строках `265` и `266`. 


3. Также после завершения работы программы `в ее корневой папке` будут созданны или перезаписанны два json файла `data_employers` и `json-vacancies`, для возможной дальнейшей работы, с информацие об компаниях-работодателях и их вакансиях.


4. При включеной функции `№5`, программа потребует от вас введения ключегого слова, по нему будет производится отбор вакансий, в названии или описании которых, оно указано.
---
Структура json файла `data_employers`:
````
            {'name': Название компании,
            'description': Описание компании,
            'area': Город, где находится глав. офис,
            'hh.ru_url': ссылка на кампанию на сайте hh.ru,
            'site_url': ссылка на вебсайт компании,
            'vacancy_count': количество вакансий компании}
````
---
Структура json файла `json-vacancies`:
````
             {'name': Название вакансии,
             'url': ссылка на вакансию,
             'salary_from': зарплата от...,
             'salary_to': зарплата до...,
             'experience': требуемый опыт,
             'requirement_and_responsibility': требования и обязаности,
             'employer': работодатель}
````
---
В следующие запуски файлы будет переписываться.

---
Для работы программы необходимы библиотеки `requests` и `psycopg2`!
-
Для быстрой установки предусмотрен файл `requirements.txt`.

В терминал вводится команда:
````
pip install -r requirements.txt
````
