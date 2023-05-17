# Для запуска веб-интерфейса нужно следующее:
1) Установить все необходимое для работы бэкенд части
2) Зайти в эту папку и ввести последовательно следующие команды для создания базы данных:
    ```
    python3 manage.py makemigrations
    python3 manage.py migrate
    ```
3) Далее нужно создать суперпользователя, поскольку для использования приложения нужна авторизация. Используем команду
    ```
   python3 manage.py createsuperuser
   ```
   Далее вводим username, пароль и все остальное
4) Для запуска непосредственно веб-интерфейса пишем 
    ```
   python3 manage.py runserver
   ```
   В выводе получаем веб-адрес, на котором и будет находиться веб-интерфейс. Далее вводим данные суперпользователя и 
пользуемся.

