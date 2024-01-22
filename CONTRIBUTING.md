# Как развернуть сервис

## Шаг 1: Создание окружения venv

```sh
python -m venv venv
```

## Шаг 2: Активация окружения venv
```sh
.\venv\Scripts\Activate.ps1  
```

## Шаг 3: Установка пакетов из requirements.txt
```sh
pip install -r requirements.txt
```

## Шаг 4: Конфигурация запуска через pycharm:

### Настроить интерпритатор:
> Add New Interpreter - Local - Existing - <YOUR_PATH_TO_VENV>/venv/Scripts/python.exe\
> Запустить main.py