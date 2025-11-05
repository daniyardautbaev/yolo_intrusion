import json

def load_zones(path: str):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            zones = json.load(f)
        return zones
    except FileNotFoundError:
        print(f"⚠️ Файл {path} не найден, возвращаю пустой список.")
        return []


def save_zones(path: str, zones: list):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(zones, f, indent=2, ensure_ascii=False)
    print(f" Зоны сохранены в {path}")