# Проект "Погода" (WeatherApp)

Веб-приложение для просмотра текущей погоды. Пользователь может зарегистрироваться и добавить в коллекцию одну или несколько локаций (городов, сёл, других пунктов), после чего главная страница приложения начинает отображать список локаций с их текущей погодой.

Проект создан в рамках [учебного курса](https://zhukovsd.github.io/python-backend-learning-course/).
Ссылка на ТЗ проекта: [https://zhukovsd.github.io/python-backend-learning-course/projects/weather-viewer/](https://zhukovsd.github.io/python-backend-learning-course/projects/weather-viewer/)

## Технологии

*   Python
*   Django
*   PostgreSQL
*   Nginx
*   Docker / Docker Compose
*   Gunicorn
*   OpenWeatherMap API

## Локальный запуск (с использованием Docker)

### Предварительные требования

*   Установленный [Docker](https://docs.docker.com/get-docker/) и [Docker Compose](https://docs.docker.com/compose/install/)
*   Git

### Установка и запуск

1.  **Клонируйте репозиторий:**
    Перейдите в директорию, где вы хотите разместить проект, и выполните:
    ```bash
    git clone https://github.com/Gichie/Weather.git
    cd Weather
    ```

2.  **Настройте переменные окружения:**
    *   Создайте файл `.env` в корневой директории проекта (рядом с `docker-compose.yml`).
    *   Скопируйте в него следующее содержимое и **замените значения** на ваши:

        ```dotenv
        # Настройки базы данных PostgreSQL
        POSTGRES_DB=weather_db            # Имя базы данных
        POSTGRES_USER=weather_user        # Имя пользователя БД
        POSTGRES_PASSWORD=your_strong_password # Пароль для пользователя БД
        POSTGRES_HOST=postgres            
        POSTGRES_PORT=5432                # Стандартный порт PostgreSQL

        # Настройки Django
        # Сгенерируйте новый ключ командой:
        # python manage.py shell -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
        SECRET_KEY=your_django_secret_key

        # Ключ API OpenWeatherMap
        # Получите ключ здесь: https://home.openweathermap.org/users/sign_up
        WEATHER_API=your_openweathermap_api_key
        ```

3.  **Соберите и запустите контейнеры:**
    Выполните в терминале из корневой директории проекта:
    ```bash
    docker compose up -d --build
    ```

### Доступ к приложению

*   **Веб-приложение:** Откройте в браузере `http://localhost` или `http://127.0.0.1`

### Остановка приложения

Чтобы остановить и удалить контейнеры, сети и тома (кроме именованных):
```bash
docker compose down