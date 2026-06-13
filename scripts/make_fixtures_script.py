# pep/scripts/make_fixtures_script.py
import json
import os
import sys
import django

# --- НАСТРОЙКА DJANGO ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "foodcalc.settings")
django.setup()

try:
    import ijson
except ImportError:
    print("❌ ОШИБКА: Библиотека 'ijson' не найдена.")
    print("Установите её командой: docker compose run --rm web pip install ijson")
    sys.exit(1)

from food.models import Food, NutrientsName, NutrientsQuantity
from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()
SUPERUSER_PASSWORD = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
if not SUPERUSER_PASSWORD:
    raise ValueError("⚠️ ОШИБКА: Не установлена переменная окружения DJANGO_SUPERUSER_PASSWORD.")

# --- КОНФИГУРАЦИЯ ---
good_nutrients = [
    'Water', 'Energy', 'Protein', 'Arginine', 'Histidine', 'Isoleucine',
    'Leucine', 'Lysine', 'Methionine', 'Methionine + cystine', 'Phenylalanine',
    'Phenylalanine + tyrosine', 'Threonine', 'Tryptophan', 'Valine', 'Taurine',
    'Total lipid (fat)', 'Linoleic acid (omega-6)', 'Arachidonic acid (omega-6)',
    'Alpha-linolenic acid (omega-3)', 'EPA + DHA (omega-3)', 'Calcium, Ca',
    'Phosphorus, P', 'Potassium, K', 'Sodium, Na', 'Chloride', 'Magnesium, Mg',
    'Copper, Cu', 'Iodine, I', 'Iron, Fe', 'Manganese, Mn', 'Selenium, Se',
    'Zinc, Zn', 'Vitamin A', 'Vitamin D (D2 + D3)', 'Vitamin E (alpha-tocopherol)',
    'Thiamin', 'Riboflavin', 'Pantothenic acid', 'Vitamin B-6', 'Vitamin B-12',
    'Niacin', 'Folate, total', 'Biotin', 'Choline, total', 'Vitamin K (phylloquinone)',
]

good_nutrients_set = set(good_nutrients)
nutrients_order = {nutr: i * 3 for i, nutr in enumerate(good_nutrients, 1)}

# Карта для расчета составных нутриентов (Источник -> Цель)
calculated = {
    'Methionine': 'Methionine + cystine',
    'Cystine': 'Methionine + cystine',
    'Phenylalanine': 'Phenylalanine + tyrosine',
    'Tyrosine': 'Phenylalanine + tyrosine',
    'PUFA 20:5 n-3 (EPA)': 'EPA + DHA (omega-3)',
    'PUFA 22:6 n-3 (DHA)': 'EPA + DHA (omega-3)',
}

name_map = {
    'Vitamin A, IU': 'Vitamin A',
    'PUFA 18:2 n-6 c,c': 'Linoleic acid (omega-6)',
    'PUFA 20:4': 'Arachidonic acid (omega-6)',
    'PUFA 18:3 n-3 c,c,c (ALA)': 'Alpha-linolenic acid (omega-3)'
}

files = [
    ('FoodData_Central_sr_legacy_food_json_2018-04.json', 'SRLegacyFoods', 'legacy'),
    ('surveyDownload.json', 'SurveyFoods', 'survey'),
    ('FoodData_Central_foundation_food_json_2026-04-30.json', 'FoundationFoods', 'foundation2'),
]

# Размер батча для записи в БД (оптимально для 1ГБ ОЗУ)
BATCH_SIZE_ITEMS = 2000

def process_stream(file_info):
    filename, key, suffix = file_info
    filepath = os.path.join(os.path.dirname(__file__), filename)
    if not os.path.exists(filepath):
        print(f"   Файл {filename} не найден. Пропуск.")
        return

    print(f"\n📦 Чтение {filename} (Stream mode)...")
    
    # 1. Автор
    try:
        author_user = User.objects.get(username='FoodData')
    except User.DoesNotExist:
        author_user = User.objects.create_superuser(username='FoodData', email='fooddata@example.com', password=SUPERUSER_PASSWORD)
        print("✅ Создан пользователь FoodData")

    # 2. Кэши ID существующих объектов (чтобы не дергать БД лишний раз)
    print("   Загрузка кэша ID из БД...")
    existing_nutr_cache = dict(NutrientsName.objects.values_list('name', 'id'))
    existing_food_cache = dict(Food.objects.values_list('description', 'id'))
    print(f"   Кэш: {len(existing_nutr_cache)} нутриентов, {len(existing_food_cache)} продуктов.")

    items_processed = 0
    quants_processed = 0
    
    # Буфер для пачки связей (NutrientsQuantity)
    batch_quantities = [] 
    # Set для проверки уникальности внутри текущего батча
    batch_seen_quants = set() 

    # Открываем файл в бинарном режиме для ijson
    # ijson парсит массив item за item-ом, не загружая файл целиком в память
    with open(filepath, 'rb') as f:
        items_generator = ijson.items(f, f'{key}.item')

        for item in items_generator:
            items_processed += 1
            
            # Прогресс
            if items_processed % 1000 == 0:
                sys.stdout.write(f"\r   📖 Распарсено items: {items_processed}")
                sys.stdout.flush()

            desc = item['description']
            fdcId = item['fdcId']
            ndbNumber = item.get('ndbNumber', 0)
            
            # Категория
            category = 'None'
            cat_data = item.get('foodCategory')
            if isinstance(cat_data, dict):
                category = cat_data.get('description', 'None')
            else:
                wweia = item.get('wweiaFoodCategory')
                if isinstance(wweia, dict):
                    category = wweia.get('wweiaFoodCategoryDescription', 'None')

            # --- 1. Работа с Продуктом ---
            # Проверяем кэш
            current_food_id = existing_food_cache.get(desc)
            
            if not current_food_id:
                # Если нет в кэше, создаем
                try:
                    f_obj = Food(
                        description=desc,
                        fdcId=fdcId,
                        ndbNumber=ndbNumber,
                        foodCategory=category,
                        author=author_user
                    )
                    f_obj.save() 
                    current_food_id = f_obj.id
                    existing_food_cache[desc] = current_food_id
                except Exception as e:
                    # Если вдруг уже есть (конкурентная запись или расхождение кэша)
                    try:
                        current_food_id = Food.objects.get(description=desc).id
                        existing_food_cache[desc] = current_food_id
                    except Exception:
                        current_food_id = None

            if not current_food_id:
                continue # Пропускаем, если не удалось получить продукт

            # --- 2. Парсинг Нутриентов ---
            energy_added_for_this_food = False
            nutrients_for_item = [] # Список (name, id, amount)
            
            # Словарь для накопления сумм расчетных нутриентов
            calc_sums = {} 

            for fn in item.get('foodNutrients', []):
                amount = fn.get('amount')
                if amount is None: 
                    amount = fn.get('median')
                if amount is None: 
                    continue

                name = fn['nutrient']['name']
                unit = fn['nutrient'].get('unitName', 'g')
                if unit == 'µg': unit = 'ug'
                if name in name_map: name = name_map[name]

                # Обработка энергии (берем только первую попавшуюся)
                if name == 'Energy':
                    if unit == 'kJ': amount = round(amount / 4.184, 2)
                    if energy_added_for_this_food: continue
                    energy_added_for_this_food = True
                    unit = 'kcal'

                # Поиск или создание нутриента в БД
                nutr_id = existing_nutr_cache.get(name)
                if not nutr_id:
                    is_pub = 1 if name in good_nutrients_set else 0
                    order = nutrients_order.get(name, 100)
                    try:
                        n_obj = NutrientsName.objects.create(
                            name=name, unit_name=unit, 
                            is_published=bool(is_pub), order=order
                        )
                        nutr_id = n_obj.id
                        existing_nutr_cache[name] = nutr_id
                    except Exception:
                        # Если ошибка создания, пробуем получить
                        try:
                            nutr_id = NutrientsName.objects.get(name=name).id
                            existing_nutr_cache[name] = nutr_id
                        except Exception:
                            continue # Пропускаем, если ничего не вышло

                nutrients_for_item.append((name, nutr_id, amount))
                
                # Логика расчетных нутриентов (накапливаем сумму)
                if name in calculated:
                    target = calculated[name]
                    if target not in calc_sums:
                        calc_sums[target] = {'amount': 0, 'unit': unit}
                    calc_sums[target]['amount'] += amount

            # --- 3. Обработка расчетных нутриентов ---
            for target, info in calc_sums.items():
                t_id = existing_nutr_cache.get(target)
                if not t_id:
                    # Создаем новый нутриент для суммы
                    is_pub = 1 if target in good_nutrients_set else 0
                    order = nutrients_order.get(target, 100)
                    try:
                        n_obj = NutrientsName.objects.create(
                            name=target, unit_name=info['unit'], 
                            is_published=bool(is_pub), order=order
                        )
                        t_id = n_obj.id
                        existing_nutr_cache[target] = t_id
                    except Exception:
                        try:
                            t_id = NutrientsName.objects.get(name=target).id
                            existing_nutr_cache[target] = t_id
                        except Exception:
                            t_id = None
                
                if t_id:
                    nutrients_for_item.append((target, t_id, info['amount']))

            # --- 4. Добавление в батч ---
            for n_name, n_id, amt in nutrients_for_item:
                key = (current_food_id, n_id)
                if key not in batch_seen_quants:
                    batch_seen_quants.add(key)
                    batch_quantities.append(
                        NutrientsQuantity(food_id=current_food_id, nutrient_id=n_id, amount=amt)
                    )
            
            # --- 5. Flush (Запись в БД) ---
            if len(batch_quantities) >= BATCH_SIZE_ITEMS:
                with transaction.atomic():
                    NutrientsQuantity.objects.bulk_create(batch_quantities, ignore_conflicts=True)
                    quants_processed += len(batch_quantities)
                    # Очистка памяти
                    del batch_quantities[:] 
                    batch_seen_quants.clear()
                
                sys.stdout.write(f"\r   💾 Сохранено связей: {quants_processed}")
                sys.stdout.flush()

    # --- 6. Final Flush ---
    if batch_quantities:
        with transaction.atomic():
            NutrientsQuantity.objects.bulk_create(batch_quantities, ignore_conflicts=True)
            quants_processed += len(batch_quantities)
    
    print(f"\n   ✅ Готово. Всего записей: {items_processed}, связей записано: {quants_processed}")


if __name__ == "__main__":
    print("=== НАЧАЛО ЗАГРУЗКИ (STREAM MODE) ===")
    for f in files:
        process_stream(f)
    print("=== ВСЕ ГОТОВО ===")