# Food Assistant
![Deploy status](https://github.com/vadikam100500/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)

On this service, you can publish recipes, subscribe to publications of other users, 
add your favorite recipes to the Favorites list, and before going to the store, 
download a summary list of products required to prepare one or more selected dishes.

## Functionality

* Full user authentication.
* Create/edit/delete new recipe.
* Filter by tags.  
* Choose from a bunch of ingredients.
* Add to favourites.
* Favourites page.
* Follow another authors.
* Add to shopping list.
* Download shopping list.

## What I used

- Python
- Django
- Django REST Framework
- PostgreSQL
- Djoser
- OpenAPI
- Docker

## Deploy

### Local:

+ Delete whole dir .github/workflows
+ Uncomment .env in .gitignore and set secrets in .env like:
    ```sh
    SECRET_KEY=YOUR_SECRET_KEY
    DEBUG=TRUE # if you want to work in dev
    ALLOWED_HOSTS=host1, host2, etc 
    CORS_ALLOWED_ORIGINS=host1, host2, etc. # uncomment CORS_ALLOWED_ORIGINS and comment CORS_ALLOW_ALL_ORIGINS in settings.py, if you want  special hosts for CORS
    DJANGO_SUPERUSER_USERNAME=admin # set instead admin, username of superuser
    DJANGO_SUPERUSER_EMAIL=admin@gmail.com # set instead admin@gmail.com, email of superuser
    DJANGO_SUPERUSER_PASSWORD=admin # set instead admin, password of superuser
    DJANGO_SUPERUSER_FIRST_NAME=angry_admin
    DJANGO_SUPERUSER_LAST_NAME=superangry_admin
    LICENSE=BSD License
    CONTACT_EMAIL=contakt@gmail.com
    DB_ENGINE=django.db.backends.postgresql
    DB_NAME=postgres # set instead postgres, name of db
    POSTGRES_USER=postgres # set instead postgres, nikname of superuser of db
    POSTGRES_PASSWORD=postgres # set instead postgres, password of db
    DB_HOST=db # you can rename it or set a needed host, but before make changes to docker-compose.yaml
    DB_PORT=5432
    ```

+ [Install docker ](https://docs.docker.com/get-docker/)
+ If you don't need any files or dirs in container, you can set them in .dockerignore
+ In dir 'infra' run:
    ```sh
    $ docker-compose up
    ```
+ Open a new window of terminal and from dir of project run:
    ```sh
    $ sudo docker-compose exec backend ./manage.py migrate --noinput
    $ sudo docker-compose exec backend ./manage.py collectstatic --no-input
    $ sudo docker-compose exec backend ./manage.py create_admin
    $ sudo docker-compose exec backend ./manage.py loaddata data/dump.json
    ```
+ You can get admin panel in http://localhost/admin/ with username and password, that you set in .env (DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_PASSWORD)

### Continuous Integration and Continuous Deployment with testing by GithubActions:
+ Install Docker and Docker-compose on your server.
+ Copy docker-compose.yaml and nginx.conf to your server
+ Prepare your repository in GitHub:
  + In settings of repo find secrets and set in them:
    + DOCKER_PASSWORD, DOCKER_USERNAME - for pull and download image from DockerHub
    + SECRET_KEY, ALLOWED_HOSTS - for django app
    + DB_ENGINE, DB_NAME, POSTGRES_USER, POSTGRES_PASSWORD, DB_HOST, DB_PORT - to connect to default database
    + DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_EMAIL, DJANGO_SUPERUSER_PASSWORD - for creating superuser
    + Other secrets
+ After push to github, the main application will pass the tests, update the image on DockerHub, and deploy to the server.

## Documentation and requests examples

+ If you local deployed project, you can see that here:
    * [ Task and full documentation (Redoc) ]( http://localhost/api/docs/redoc.html )
    * [ Documentation and manual work with api - Swagger]( http://localhost/api/docs/swagger/ )

+ If not local:
    + ://yourhost/api/docs/redoc/ - Task and full documentation
    + ://yourhost/api/docs/swagger/  - Swagger

# Task
##  **Базовые модели проекта**
Более подробно с базовыми моделями можно ознакомиться в спецификации API.
### Рецепт
Рецепт должен описываться такими полями:
- Автор публикации (пользователь).
- Название.
- Картинка.
- Текстовое описание.
- Ингредиенты: продукты для приготовления блюда по рецепту. Множественное поле, выбор из предустановленного списка, с указанием количества и единицы измерения.
- Тег (можно установить несколько тегов на один рецепт, выбор из предустановленных).
- Время приготовления в минутах.
Все поля обязательны для заполнения.
### Тег
Тег должен описываться такими полями:
- Название.
- Цветовой HEX-код (например, #49B64E).
- Slug.
Все поля обязательны для заполнения и уникальны.
### Ингредиент
Данные об ингредиентах хранятся в нескольких связанных таблицах. В результате на стороне пользователя ингредиент должен описываться такими полями:

- Название.
- Количество.
- Единицы измерения.
Все поля обязательны для заполнения.
## Сервисы и страницы проекта
### Главная страница
Содержимое главной страницы — список первых шести рецептов, отсортированных по дате публикации (от новых к старым). Остальные рецепты доступны на следующих страницах: внизу страницы есть пагинация.
### Страница рецепта
На странице — полное описание рецепта. Для авторизованных пользователей — возможность добавить рецепт в избранное и в список покупок, возможность подписаться на автора рецепта.
### Страница пользователя
На странице — имя пользователя, все рецепты, опубликованные пользователем и возможность подписаться на пользователя.
### Подписка на авторов
Подписка на публикации доступна только авторизованному пользователю. Страница подписок доступна только владельцу.
Сценарий поведения пользователя:
- Пользователь переходит на страницу другого пользователя или на страницу рецепта и подписывается на публикации автора кликом по кнопке «Подписаться на автора».
- Пользователь переходит на страницу «Мои подписки» и просматривает список рецептов, опубликованных теми авторами, на которых он подписался. Сортировка записей — по дате публикации (от новых к старым).
- При необходимости пользователь может отказаться от подписки на автора: переходит на страницу автора или на страницу его рецепта и нажимает «Отписаться от автора»
### Список избранного
Работа со списком избранного доступна только авторизованному пользователю. Список избранного может просматривать только его владелец.
Сценарий поведения пользователя:
- Пользователь отмечает один или несколько рецептов кликом по кнопке «Добавить в избранное».
- Пользователь переходит на страницу «Список избранного» и просматривает персональный список избранных рецептов.
- При необходимости пользователь может удалить рецепт из избранного.
### Список покупок
Работа со списком покупок доступна авторизованным пользователям. Список покупок может просматривать только его владелец.
Сценарий поведения пользователя:
- Пользователь отмечает один или несколько рецептов кликом по кнопке «Добавить в покупки».
- Пользователь переходит на страницу Список покупок, там доступны все добавленные в список рецепты. Пользователь нажимает кнопку Скачать список и получает файл с суммированным перечнем и количеством необходимых ингредиентов для всех рецептов, сохранённых в «Списке покупок».
- При необходимости пользователь может удалить рецепт из списка покупок.
Список покупок скачивается в формате .txt (или, по желанию, можно сделать другую выгрузку).
При скачивании списка покупок ингредиенты в результирующем списке не должны дублироваться; если в двух рецептах есть сахар (в одном рецепте 5 г, в другом — 10 г), то в списке должен быть один пункт: Сахар — 15 г.
### Фильтрация по тегам
При нажатии на название тега выводится список рецептов, отмеченных этим тегом. Фильтрация может проводится по нескольким тегам в комбинации «или»: если выбраны несколько тегов — в результате должны быть показаны рецепты, которые отмечены хотя бы одним из этих тегов.
При фильтрации на странице пользователя должны фильтроваться только рецепты выбранного пользователя. Такой же принцип должен соблюдаться при фильтрации списка избранного.
### Регистрация и авторизация
В проекте должна быть доступна система регистрации и авторизации пользователей. Чтобы собрать весь код для управления пользователями воедино — создайте приложение users.
#### Обязательные поля для пользователя:
- Логин
- Пароль
- Email
- Имя
- Фамилия
#### Уровни доступа пользователей:
- Гость (неавторизованный пользователь)
- Авторизованный пользователь
- Администратор
### Что могут делать неавторизованные пользователи
- Создать аккаунт.
- Просматривать рецепты на главной.
- Просматривать отдельные страницы рецептов.
- Просматривать страницы пользователей.
- Фильтровать рецепты по тегам.
### Что могут делать авторизованные пользователи
- Входить в систему под своим логином и паролем.
- Выходить из системы (разлогиниваться).
- Менять свой пароль.
- Создавать/редактировать/удалять собственные рецепты
- Просматривать рецепты на главной.
- Просматривать страницы пользователей.
- Просматривать отдельные страницы рецептов.
- Фильтровать рецепты по тегам.
- Работать с персональным списком избранного: добавлять в него рецепты или удалять их, просматривать свою страницу избранных рецептов.
- Работать с персональным списком покупок: добавлять/удалять любые рецепты, выгружать файл со количеством необходимых ингридиентов для рецептов из списка покупок.
- Подписываться на публикации авторов рецептов и отменять подписку, просматривать свою страницу подписок.
### Что может делать администратор
Администратор обладает всеми правами авторизованного пользователя.
Плюс к этому он может:
изменять пароль любого пользователя,
- создавать/блокировать/удалять аккаунты пользователей,
- редактировать/удалять любые рецепты,
- добавлять/удалять/редактировать ингредиенты.
- добавлять/удалять/редактировать теги.
Все эти функции нужно реализовать в стандартной админ-панели Django.
### Настройки админки
В интерфейс админ-зоны нужно вывести необходимые поля моделей и настроить фильтры.
#### Модели:
- Вывести все модели с возможностью редактирования и удаление записей.
##### Модель пользователей:
- Добавить фильтр списка по email и имени пользователя.
#### Модель рецептов:
- В списке рецептов вывести название и автора рецепта.
- Добавить фильтры по автору, названию рецепта, тегам.
- На странице рецепта вывести общее число добавлений этого рецепта в избранное.
#### Модель ингредиентов:
- В список вывести название ингредиента и единицы измерения.
- Добавить фильтр по названию.
#### Технические требования и инфраструктура
- Проект должен использовать базу данных PostgreSQL.
- В Django-проекте должен быть файл requirements.txt со всеми зависимостями.
- Проект нужно запустить в трёх контейнерах (nginx, PostgreSQL и Django) (контейнер frontend используется лишь для подготовки файлов) через docker-compose на вашем сервере в Яндекс.Облаке. Образ с проектом должен быть запушен на Docker Hub