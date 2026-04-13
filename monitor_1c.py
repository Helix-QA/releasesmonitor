import requests
from bs4 import BeautifulSoup
import re
import json
import time
import os
from datetime import datetime

# ===================== НАСТРОЙКИ =====================
LOGIN = os.getenv("LOGIN_1C")
PASSWORD = os.getenv("PASSWORD_1C")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# ===================== JENKINS =====================
JENKINS_URL = os.getenv("JENKINS_URL")
JENKINS_JOB_NAME = os.getenv("JENKINS_JOB_NAME")
JENKINS_USER = os.getenv("JENKINS_USER")
JENKINS_API_TOKEN = os.getenv("JENKINS_API_TOKEN")

# Соответствие продукта → параметр, который передаём в Jenkins
JENKINS_PRODUCT_MAP = {
    "Фитнес клуб КОРП, редакция 4.0": "fintessCorp",      
    "Салон красоты, редакция 3.0": "salon30",
    "1С:Предприятие 8. SPA-Салон, редакция 3.0": "SpaSalon3",
}

# === СТРОГАЯ ПРОВЕРКА ЛОГИНА И ПАРОЛЯ ===
if not LOGIN or not PASSWORD:
    print("❌ КРИТИЧЕСКАЯ ОШИБКА: Не заданы LOGIN_1C и/или PASSWORD_1C")
    print("   Проверьте файл .env и перезапустите контейнер.")
    exit(1)

PRODUCTS = [
    "1С:Медицина. Стоматологическая клиника, редакция 2.1",
    "1С:Предприятие 8. SPA-Салон, редакция 3.0",
    "Салон красоты, редакция 3.0",
    "Фитнес клуб КОРП, редакция 4.0",
    "Фитнес клуб, редакция 4.0"
]

VERSIONS_FILE = "/data/1c_versions.json"

# ====================================================

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
})

def version_to_tuple(version_str):
    numbers = re.findall(r'\d+', version_str)
    return tuple(map(int, numbers)) if numbers else (0,)

def send_telegram(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️  Telegram не настроен")
        return
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
        requests.post(url, data=data, timeout=10)
        print(f"✅ Отправлено в Telegram")
    except Exception as e:
        print(f"❌ Ошибка Telegram: {e}")

def trigger_jenkins_job(product_name: str, new_version: str):
    """Запускает Jenkins job только для нужных продуктов"""
    jenkins_param = JENKINS_PRODUCT_MAP.get(product_name)
    if not jenkins_param:
        return  # это не тот продукт

    if not JENKINS_URL or not JENKINS_JOB_NAME:
        print(f"⚠️  Jenkins не настроен для продукта {product_name}")
        return

    url = f"{JENKINS_URL.rstrip('/')}/job/{JENKINS_JOB_NAME}/buildWithParameters"

    # ← Здесь можно поменять имена параметров, если в твоей джобе они называются по-другому
    params = {
        "product": jenkins_param,   # fintessCorp / salon30 / SpaSalon3
        "version": new_version
    }

    try:
        auth = (JENKINS_USER, JENKINS_API_TOKEN) if JENKINS_USER and JENKINS_API_TOKEN else None
        resp = requests.post(url, params=params, auth=auth, timeout=20, allow_redirects=True)
        
        if resp.status_code in (200, 201, 302):
            print(f"🚀 Jenkins job запущена → {jenkins_param} v{new_version}")
            send_telegram(f"🚀 <b>Jenkins job запущена!</b>\nПродукт: <b>{product_name}</b>\nВерсия: <code>{new_version}</code>")
        else:
            print(f"❌ Jenkins ответил {resp.status_code}")
            print(resp.text[:300])
    except Exception as e:
        print(f"❌ Ошибка вызова Jenkins: {e}")

def load_versions():
    if os.path.exists(VERSIONS_FILE):
        try:
            with open(VERSIONS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {}

def save_versions(versions):
    os.makedirs(os.path.dirname(VERSIONS_FILE), exist_ok=True)
    with open(VERSIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(versions, f, ensure_ascii=False, indent=2)

def extract_latest_version(full_text, product_name):
    pattern = re.compile(
        rf'{re.escape(product_name)}\s*[^0-9]*?(\d+\.\d+(?:\.\d+){{1,3}})',
        re.IGNORECASE | re.DOTALL
    )
    matches = pattern.findall(full_text)
    return max(matches, key=version_to_tuple) if matches else None

# ===================== АВТОРИЗАЦИЯ =====================
print("🔄 Авторизация на 1c.ru...")
# ... (весь блок авторизации без изменений) ...

# ===================== ОСНОВНОЙ ЦИКЛ =====================
print(f"🚀 Мониторинг {len(PRODUCTS)} продуктов + Jenkins запущен в Docker.\n")

if JENKINS_URL and JENKINS_JOB_NAME:
    print(f"✅ Jenkins интеграция активна (job: {JENKINS_JOB_NAME})\n")

versions = load_versions()

while True:
    print(f"📡 Проверка — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        page = session.get("https://releases.1c.ru/total", timeout=30)
        soup = BeautifulSoup(page.text, "html.parser")
        full_text = soup.get_text(separator=" ", strip=True)

        updated = False

        for product in PRODUCTS:
            new_version = extract_latest_version(full_text, product)
            old_version = versions.get(product)

            if new_version:
                if old_version is None or version_to_tuple(new_version) > version_to_tuple(old_version):
                    message = f"<b>🔥 Выпущен новый релиз 1С!</b>\n\n<b>{product}</b>\nНовая: <code>{new_version}</code>\nСтарая: <code>{old_version or '—'}</code>"
                    send_telegram(message)
                    
                    # ← НОВОЕ: запуск Jenkins
                    if product in JENKINS_PRODUCT_MAP:
                        trigger_jenkins_job(product, new_version)
                    
                    versions[product] = new_version
                    print(f"   🎉 {product} → {new_version}")
                    updated = True
                else:
                    print(f"   ✅ {product} — {new_version} (актуально)")
            else:
                print(f"   ⚠️  {product} — версия не найдена")

        if updated:
            save_versions(versions)

    except Exception as e:
        print(f"❌ Ошибка: {e}")

    print("⏳ Следующая проверка через 5 минут...\n")
    time.sleep(300)