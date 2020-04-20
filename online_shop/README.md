Для запуска проекта необходимо проделать следующие действия:

Установить зависимости:
```
pip install -r requirements.txt
```
Загрузить статику:
```
python manage.py collectstatic
```
Провести миграцию:
```
python manage.py migrate
```
Загрузить тестовые данные:
```
python manage.py loaddata shop.json
```
Запустить отладочный веб-сервер проекта:
```
python manage.py runserver
```



