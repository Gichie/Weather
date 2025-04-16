Проект “Погода”

Веб-приложение для просмотра текущей погоды. Пользователь может зарегистрироваться и добавить в коллекцию одну или несколько локаций (городов, сёл, других пунктов), после чего главная страница приложения начинает отображать список локаций с их текущей погодой.

Проект создан в рамках курса по развитию своих профессиональных навыков.
ТЗ проекта: https://zhukovsd.github.io/python-backend-learning-course/projects/weather-viewer/

## Установка

1. Клонируйте репозиторий из папки на вашем компьютере в которой должен находится проект:
   ```bash
   git clone https://github.com/Gichie/Weather.git
   cd Weather
   ```

2. Создайте и активируйте виртуальное окружение (опционально):
   ```bash
   # Для Windows
   python -m venv venv
   venv\Scripts\activate

   # Для Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Настройте переменные окружения:
   - Создайте файл `.env` в корневой директории проекта 
   - Укажите следующие переменные окружения:
     ```
     POSTGRES_DB=your_bd_name
     POSTGRES_USER=your_db_user
     POSTGRES_PASSWORD=your_password
     POSTGRES_HOST=postgres
     POSTGRES_PORT=5432
   
     SECRET_KEY=SECRET_KEY #  Для генерации ключа можно использовать команду: 
     python manage.py shell -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
     WEATHER_API=API_KEY # https://home.openweathermap.org/users/sign_in
     ```
   - Замените значения на актуальные

4. Установите и запустите Docker:
   - https://docs.docker.com/desktop/setup/install/windows-install/

5. Запустите проект:
   - docker-compose up -d --build