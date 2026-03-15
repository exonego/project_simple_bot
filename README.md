Для запуска бота на компьютер небоходимо установить python 3.12 и docker
ВНИМАНИЕ! На старых версиях docker необходимо дополнительно устанавливать docker-compose

Первый запуск бота:
1. Создайте файл .env в корне проекта и скопируйте туда содержимое .env.example, замените значения переменных на свои.
2. Создайте виртуальное окружение python командой python3 -m venv .venv (Mac, Linux) или python -m venv .venv (Windows)
3. Активируйте виртуальное окружение в терминале командой source .venv/bin/activate (Mac, Linux) или .venv\\Scripts\\activate (Windows)
4. Установите необходимые зависимости из файла requirements.txt командой pip install -r requirements.txt в терминале
5. Поднимите БД командой docker compose up (docker-compose up в старых версиях docker)
6. Создайте таблицы в БД командой python3 -m migrations.create_tables (Mac, Linux) или python -m migrations.create_tables (Windows)
7. Запустите бота командой python3 main.py (Mac, Linux) или python main.py (Windows)

При следуйщих запусках бота выполняйте только шаги 3, 5, 7.
