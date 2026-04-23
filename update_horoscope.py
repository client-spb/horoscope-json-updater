# update_horoscope_advanced.py
import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime, timezone
import time
import re

# ─── НАСТРОЙКИ ─────────────────────────────────────────────
SIGNS = [
    "aries", "taurus", "gemini", "cancer", "leo", "virgo",
    "libra", "scorpio", "sagittarius", "capricornus", "aquarius", "pisces"
]

# Базовые URL для разных типов гороскопов
BASE_URL = "https://1001goroskop.ru/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
}

# Соответствие типов гороскопа параметрам URL
HOROSCOPE_TYPES = {
    "general": "",      # общий на сегодня: ?znak=sign
    "love": "&tm=love", # любовный
    "business": "&tm=business", # бизнес/работа
    "tomorrow": "&kn=tomorrow"  # общий на завтра
}

def get_russian_sign_name(sign: str) -> str:
    """Переводит английское имя знака в русское."""
    names = {
        "aries": "Овен", "taurus": "Телец", "gemini": "Близнецы",
        "cancer": "Рак", "leo": "Лев", "virgo": "Дева",
        "libra": "Весы", "scorpio": "Скорпион", "sagittarius": "Стрелец",
        "capricornus": "Козерог", "aquarius": "Водолей", "pisces": "Рыбы"
    }
    return names.get(sign, sign.capitalize())

def fetch_horoscope(sign: str, horoscope_type: str) -> dict:
    """
    Получает гороскоп для знака sign и указанного типа.
    horoscope_type: 'general', 'love', 'business', 'tomorrow'
    """
    # Формируем URL в зависимости от типа
    if horoscope_type == "general":
        url = f"{BASE_URL}?znak={sign}"
    elif horoscope_type == "tomorrow":
        url = f"{BASE_URL}?znak={sign}&kn=tomorrow"
    else: # love или business
        url = f"{BASE_URL}?znak={sign}{HOROSCOPE_TYPES[horoscope_type]}"
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        # Сайт использует кодировку Windows-1251
        response.encoding = 'windows-1251'
        soup = BeautifulSoup(response.text, 'html.parser')
    except Exception as e:
        return {"type": horoscope_type, "error": str(e), "text": None, "url": url}
    
    # --- Ищем текст гороскопа ---
    # Способ 1: Ищем заголовок h1 (например, "Любовный гороскоп на сегодня: Овен")
    title_elem = soup.find('h1')
    title = title_elem.get_text(strip=True) if title_elem else None
    
    text = None
    # Ищем параграф с текстом. Обычно он либо сразу после h1, либо внутри div с контентом.
    # На сайте текст часто находится в первом же <p> после h1.
    if title_elem:
        next_p = title_elem.find_next('p')
        if next_p and len(next_p.get_text(strip=True)) > 50:
            text = next_p.get_text(strip=True)
    
    # Способ 2: Если не нашли, ищем любой длинный параграф (вероятно, текст гороскопа)
    if not text:
        for p in soup.find_all('p'):
            p_text = p.get_text(strip=True)
            # Гороскоп обычно содержит больше 100 символов
            if len(p_text) > 100 and not p.find_parent('div', class_='calendar'):
                text = p_text
                break
    
    # --- Ищем дату (если есть) ---
    # На страницах дата часто в параграфе с классом 'date' или в виде "Четверг, 23 апреля 2026 года"
    date_elem = None
    date_pattern = re.compile(r'\d{1,2}\s+\w+\s+\d{4}')
    for p in soup.find_all('p'):
        if date_pattern.search(p.get_text()):
            date_elem = p
            break
    
    source_date = date_elem.get_text(strip=True) if date_elem else None
    
    return {
        "type": horoscope_type,
        "sign": sign,
        "sign_name_ru": get_russian_sign_name(sign),
        "text": text or f"Текст {horoscope_type} гороскопа не найден",
        "title": title,
        "source_date": source_date,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "url": url
    }

def main():
    print("🌙 Расширенный парсер гороскопов с 1001goroskop.ru")
    print("Сбор: общий (сегодня), любовный, бизнес, общий (завтра)")
    print("=" * 60)
    
    # Структура для хранения всех данных:
    # {
    #   "aries": {
    #       "general": {...},
    #       "love": {...},
    #       "business": {...},
    #       "tomorrow": {...}
    #   },
    #   ...
    # }
    all_data = {}
    
    for i, sign in enumerate(SIGNS, 1):
        print(f"\n[{i}/12] Обработка знака: {get_russian_sign_name(sign)}")
        sign_data = {}
        
        for h_type in HOROSCOPE_TYPES.keys():
            print(f"  ├─ {h_type.upper()}...", end=" ", flush=True)
            try:
                data = fetch_horoscope(sign, h_type)
                sign_data[h_type] = data
                
                if "error" in data:
                    print(f"❌ Ошибка: {data['error']}")
                else:
                    # Показываем длину текста для проверки
                    text_len = len(data.get('text', ''))
                    print(f"✅ {text_len} символов")
                    
            except Exception as e:
                print(f"❌ Критическая ошибка: {e}")
                sign_data[h_type] = {"type": h_type, "error": str(e)}
            
            # Небольшая пауза между запросами для одного знака, чтобы не перегружать сервер
            time.sleep(0.5)
        
        all_data[sign] = sign_data
        
        # Сохраняем промежуточный результат после каждого знака
        with open("horoscope_advanced.json", 'w', encoding='utf-8') as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)
        
        # Пауза между разными знаками
        time.sleep(1)
    
    print("\n" + "=" * 60)
    print(f"✅ Полные данные сохранены в horoscope_advanced.json")
    
    # Выводим небольшой пример для проверки (Овен, любовный)
    if "aries" in all_data and "love" in all_data["aries"]:
        print("\n📖 Пример (Овен, любовный гороскоп):")
        love_text = all_data["aries"]["love"].get("text", "Нет текста")
        print(love_text[:250] + "..." if len(love_text) > 250 else love_text)

if __name__ == "__main__":
    main()
