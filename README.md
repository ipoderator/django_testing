# Vice Versa - это тестовый проект на платформе Яндекс Практикум

#### В этом проекты мы научились работать с pytest и unittest
#### Стэк который я использовал в этом проекте:

- Python3.11

- Django3.2

- Sqlite2.8.17

- Pytest7.1.3

- Pytils0.4.1
  
## Установить репозиторий по `ssh`:

```sh 

git clone git@github.com:ipoderator/django_testing.git 

``` 

### Создать вирутальное `окружение`:

```sh

python3.11 -m venv venv 

```

### Активировать виртуальное `окружение`:

```sh 

. ./venv/bin/activate 

``` 

 

### Установить `зависимости`:

```sh 

pip install -r requirements.txt 

``` 

 

### Установить `миграции`:

```sh

python3.11 manage.py migrate 

```

### Запустить `проект`:

```sh

./manage.py runserver 

```

### Создать суперпользователя  

```sh

python3.11 manage.py createsuperuser 

```

### После того как проект сделан - запускаем bash скрипт из корневой директории проекта

```sh 

bash run_tests.sh  

``` 