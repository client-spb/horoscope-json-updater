# update_horoscope.py (исправленная версия)
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

SIGN_URLS = {
    "aries": "https://1001goroskop.ru/?znak=aries",
    "taurus": "https://1001goroskop.ru/?znak=taurus",
    "gemini": "https://1001goroskop.ru/?znak=gemini",
    "cancer": "https://1001goroskop.ru/?znak=cancer",
    "leo": "https://1001goroskop.ru/?znak=leo",
    "virgo": "https://1001goroskop.ru/?znak=virgo",
    "libra": "https://1001goroskop.ru/?znak=libra",
    "scorpio": "https://1001goroskop.ru/?znak=scorpio",
    "sagittarius": "https://1001goroskop.ru/?znak=sagittarius",
    "capricornus": "https://1001goroskop.ru/?znak=capricornus",
    "aquarius": "https://1001goroskop.ru/?znak=aquarius",
    "pisces": "https://1001goroskop.ru/?znak=pisces"
}

JSON_OUTPUT = "horoscope.json"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
}

def get_russian_sign_name(sign: str) -> str:
    names = {
        "aries": "Овен", "taurus": "Телец", "gemini": "Близнецы",
        "cancer": "Рак", "leo": "Лев", "virgo": "Дева",
        "libra": "Весы", "scorpio": "Скорпион", "sagittarius": "Стрелец",
        "capricornus": "Козерог", "aquarius": "Водолей", "pisces": "Рыбы"
    }
    return names.get(sign, sign.capitalize())

def fetch_horoscope(sign: str) -> dict:
    url = SIGN_URLS[sign]
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        # КРИТИЧЕСКИ ВАЖНО: сайт использует Windows-1251
        response.encoding = 'windows-1251'
        soup = BeautifulSoup(response.text, 'html.parser')
    except Exception as e:
        return {"sign": sign, "error": str(e), "text": None}
    
    # Ищем заголовок (h1)
    title_elem = soup.find('h1')
    title = title_elem.get_text(strip=True) if title_elem else None
    
    # Ищем текст гороскопа - обычно в первом параграфе после h1
    text = None
    if title_elem:
        # Ищем следующий параграф после заголовка
        next_p = title_elem.find_next('p')
        if next_p:
            text = next_p.get_text(strip=True)
    
    # Если не нашли, ищем любой параграф с текстом
    if not text:
        for p in soup.find_all('p'):
            p_text = p.get_text(strip=True)
            if len(p_text) > 100:  # Гороскоп обычно длинный
                text = p_text
                break
    
    # Ищем дату
    date_elem = soup.find('p', string=re.compile(r'\d{1,2}\s+\w+\s+\d{4}'))
    source_date = date_elem.get_text(strip=True) if date_elem else None
    
    return {
        "sign": sign,
        "sign_name_ru": get_russian_sign_name(sign),
        "text": text or "Текст гороскопа не найден",
        "title": title,
        "source_date": source_date,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "url": url
    }

def main():
    print("🌙 Обновление гороскопов с 1001goroskop.ru (кодировка Windows-1251)")
    print("=" * 50)
    
    all_data = {}
    
    for i, sign in enumerate(SIGNS, 1):
        print(f"[{i}/12] {get_russian_sign_name(sign)}...", end=" ", flush=True)
        
        try:
            data = fetch_horoscope(sign)
            all_data[sign] = data
            
            if "error" in data:
                print(f"❌ Ошибка: {data['error']}")
            else:
                print(f"✅ {len(data['text'])} символов")
                
            # Сохраняем после каждого знака
            with open(JSON_OUTPUT, 'w', encoding='utf-8') as f:
                json.dump(all_data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"❌ Критическая ошибка: {e}")
            all_data[sign] = {"sign": sign, "error": str(e)}
        
        time.sleep(1)  # Пауза между запросами
    
    print("\n" + "=" * 50)
    print(f"✅ Сохранено в {JSON_OUTPUT}")
    
    # Проверка - покажем первый гороскоп
    if "aries" in all_data and "text" in all_data["aries"]:
        print("\n📖 Пример (Овен):")
        print(all_data["aries"]["text"][:200] + "...")

if __name__ == "__main__":
    main()