[![Build Status](https://travis-ci.com/YuriSilenok/self-checking.svg?branch=main)](https://travis-ci.com/YuriSilenok/self-checking)
# Горизонтальная проверка

Мы не проверяли минимальные версии ПО на котором можно запустить проект, но мы уже пробовали запускать на:
- Python=['3.8.10', '3.9.2']
- Flask=['2.0.1']
- Flask-SQLAlchemy=['2.5.1']

[Наша документация](documentation)

# Быстрый старт

- Установите PyCharm
- Клонируйте репозиторий
- Создайте окружение
- Установите пакеты
- Создайте БД командами 
```Shell
python manage.py makemigrations app
python manage.py migrate
```
- Настройте конфигурация для запуска сервера
- Запустите сервер
