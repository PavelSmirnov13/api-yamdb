# YaMDb Api

## Описание проекта

Данное приложение является REST API для сбора отзывов пользователей на произведения. Произведения в YaMDb не хранятся - нельзя посмотреть фильм, послушать музыку, прочитать книгу.

### Возможности API:

- получать, создавать, изменять или удалять отзывы и оценки на произведения
- получать, создавать, изменять или удалять комментарии к отзывам
- аутентификация по JWT-токену
- Подтверждение пользователя через код, отправленный по почте

Создание, изменение и удаление отзывов, комментариев, оценок - доступ предоставлен Автору. Доступ на редактирование и удаление отзывов и комментариев любых пользователей предоставлен Модератору. Полный доступ к любому контенту предоставлен Администраторам. Неаутентифицированным пользователям доступ предоставлен на чтение: отзывов, комментариев и просмотр оценок к произведениям.

## Стек технологий:
- Python 3.12
- Django 5.1
- Django REST Framework
- djangorestframework-simplejwt - аутентификация по JWT-токенам
- SQLite

### Инструкция к запуску проекта:

Клонировать репозиторий и перейти на него в командной строке:
git clone git@github.com:PavelSmirnov13/api-yamdb.git
cd api-yamdb

text

Создать и активировать виртуальное окружение:

Команды для OS Windows:
python -m venv venv
source venv/Scripts/activate

text

Команды для OS Mac/Linux:
python3 -m venv venv
source venv/bin/activate

text

Установить зависимости из файла requirements.txt:
pip install -r requirements.txt

text

Выполнить миграции:
python manage.py migrate

text

Выполнить загрузку данных из csv файлов:
python manage.py load_csv

text

Создать суперпользователя:
python manage.py createsuperuser

text

Запустить проект:
python manage.py runserver

text

API будет доступен по адресу http://127.0.0.1:8000/api/v1/.

### Примеры запросов:

#### Регистрация пользователя

POST /auth/signup/

Тело запроса:
```json
{
    "email": "user@example.com",
    "username": "string"
}
Тело ответа:

json
{
    "email": "string",
    "username": "string"
}
Получение токена
POST /auth/token/

Тело запроса:

json
{
    "username": "string",
    "confirmation_code": "string"
}
Тело ответа:

json
{
    "token": "string"
}
Получение списка произведений
GET /titles/

Тело ответа:

json
{
    "count": 0,
    "next": "string",
    "previous": "string",
    "results": [{}]
}
Создание отзыва
POST /titles/{title_id}/reviews/

Тело запроса:

json
{
    "text": "string",
    "score": 1
}
Тело ответа:

json
{
    "id": 0,
    "text": "string",
    "author": "string",
    "score": 1,
    "pub_date": "2019-08-24T14:15:22Z"
}
Также с полной документацией можно ознакомиться, пройдя по адресу http://127.0.0.1:8000/redoc/

Авторы:
Ivan - разработка блока пользователей и аутентификации
Pavel - разработка блока произведений с импортом csv
Alexsandr - разработка блока отзывов с комментариями
