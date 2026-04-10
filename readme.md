# 1С Releases Monitor 🚀

**Автоматический мониторинг новых релизов 1С с уведомлениями в Telegram**

[![Docker Image](https://img.shields.io/badge/Docker%20Hub-mishan358/1c--releases--monitor-blue?logo=docker)](https://hub.docker.com/r/mishan358/1c-releases-monitor)
[![GitHub Actions](https://github.com/Helix-QA/releasesmonitor/actions/workflows/build-and-push.yml/badge.svg)](https://github.com/Helix-QA/releasesmonitor/actions)

---

### ✨ Что делает скрипт

- Парсит сайт [releases.1c.ru](https://releases.1c.ru)  
- Отслеживает актуальные версии **конкретных продуктов** 1С  
- При появлении **новой версии** мгновенно отправляет красивое уведомление в Telegram  
- Работает 24/7 в Docker-контейнере  

### 📦 Поддерживаемые продукты

- 1С:Медицина. Стоматологическая клиника, редакция 2.1
- 1С:Предприятие 8. SPA-Салон, редакция 3.0
- Салон красоты, редакция 3.0
- Фитнес клуб КОРП, редакция 4.0
- Фитнес клуб, редакция 4.0

Смена продуктов в блоке PRODUCTS в файле **monitor_1c.py**

### 🐳 Быстрый запуск (Docker)









```bash
# 1. Склонируй репозиторий
git clone https://github.com/Helix-QA/releasesmonitor.git
cd releasesmonitor

# 2. Создай .env файл
cp .env
# ← открой .env и укажи свои данные

# 3. Запусти
docker compose up -d --force-recreate

```

**Пример файла .env**
```bash
LOGIN_1C=твой_логин_1c
PASSWORD_1C=твой_пароль_1c
TELEGRAM_BOT_TOKEN=твой_токен_бота
TELEGRAM_CHAT_ID=твой_chat_id
```
