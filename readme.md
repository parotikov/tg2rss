# Установка и запуск
- `python3 -m venv tg2rss_venv`
- `source tg2rss_venv/bin/activate`
- `git clone` этот репозиторий
- `pip install -r requirements.txt`
- заполнить `.env`. Как получить api id описано здесь: `https://telethon.readthedocs.io/en/latest/basic/signing-in.html`
- выполняем команду `uvicorn main:app --reload --host 0.0.0.0 --port 8091`
- открыть в браузере `localhost:8091/channel/temablog`
  
