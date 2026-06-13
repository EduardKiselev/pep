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

# Размер батча для записи в БД (меньше = меньше памяти)
BATCH_SIZE_ITEMS = 200 

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

    # 2. Кэши ID существующих объектов
    print("   Загрузка кэша ID из БД...")
    existing_nutr_cache = dict(NutrientsName.objects.values_list('name', 'id'))
    existing_food_cache = dict(Food.objects.values_list('description', 'id'))
    print(f"   Кэш: {len(existing_nutr_cache)} нутриентов, {len(existing_food_cache)} продуктов.")

    items_processed = 0
    quants_processed = 0
    
    # Буфер для пачки связей
    batch_quantities = [] 
    batch_seen_quants = set() 

    # Открываем файл в бинарном режиме для ijson
    with open(filepath, 'rb') as f:
        # ijson парсит массив item за item-ом, не загружая файл целиком
        # f'{key}.item' означает "взять массив по ключу key и итерировать его элементы"
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
            # Проверяем, есть ли продукт в кэше
            current_food_id = existing_food_cache.get(desc)
            
            # Если нет, проверяем, не создавали ли мы его только что в этом цикле
            # (на случай если логика ниже сработает некорректно, но здесь мы создаем сразу)
            
            if not current_food_id:
                # Создаем продукт сразу, чтобы получить ID для связей
                try:
                    f_obj = Food(
                        description=desc,
                        fdcId=fdcId,
                        ndbNumber=ndbNumber,
                        foodCategory=category,
                        author=author_user
                    )
                    f_obj.save() # DB Hit, но надежно
                    current_food_id = f_obj.id
                    existing_food_cache[desc] = current_food_id
                except Exception as e:
                    # Если ошибка (например дубликат в БД, которого нет в кэше)
                    try:
                        current_food_id = Food.objects.get(description=desc).id
                        existing_food_cache[desc] = current_food_id
                    except Exception:
                        print(f"⚠️ Ошибка создания продукта {desc}: {e}")
                        current_food_id = None

            if not current_food_id:
                continue # Пропускаем нутриенты, если нет продукта

            # --- 2. Парсинг Нутриентов ---
            energy_added_for_this_food = False
            
            # Список нутриентов для текущего продукта (name, id, amount)
            nutrients_for_item = []

            # Обработка расчетных нутриентов
            calc_totals = {}

            for fn in item.get('foodNutrients', []):
                amount = fn.get('amount') or fn.get('median')
                if amount is None: continue

                name = fn['nutrient']['name']
                unit = fn['nutrient'].get('unitName', 'g')
                if unit == 'µg': unit = 'ug'
                if name in name_map: name = name_map[name]

                # Обработка энергии
                if name == 'Energy':
                    if unit == 'kJ': amount = round(amount / 4.184, 2)
                    if energy_added_for_this_food: continue
                    energy_added_for_this_food = True
                    unit = 'kcal'

                # Поиск ID нутриента
                nutr_id = existing_nutr_cache.get(name)
                
                # Если нет - создаем
                if not nutr_id:
                    is_pub = 1 if name in good_nutrients_set else 0
                    order = nutrients_order.get(name, 100)
                    try:
                        n_obj = NutrientsName.objects.create(
                            name=name, 
                            unit_name=unit, 
                            is_published=bool(is_pub), 
                            order=order
                        )
                        nutr_id = n_obj.id
                        existing_nutr_cache[name] = nutr_id
                    except Exception:
                        # Если конкурентно создали или ошибка - пробуем достать
                        try:
                            nutr_id = NutrientsName.objects.get(name=name).id
                            existing_nutr_cache[name] = nutr_id
                        except Exception:
                            continue # Пропускаем, если не получилось

                nutrients_for_item.append((name, nutr_id, amount))
                
                # Логика расчетных нутриентов (суммируем в память)
                if name in calculated:
                    target = calculated[name]
                    if target not in existing_nutr_cache:
                        # Создаем "заглушку" расчетного нутриента
                        t_unit = unit 
                        t_pub = 1 if target in good_nutrients_set else 0
                        t_ord = nutrients_order.get(target, 100)
                        try:
                            n_obj = NutrientsName.objects.create(name=target, unit_name=t_unit, is_published=bool(t_pub), order=t_ord)
                            existing_nutr_cache[target] = n_obj.id
                        except:
                            try:
                                existing_nutr_cache[target] = NutrientsName.objects.get(name=target).id
                            except: pass
                    
                    target_id = existing_nutr_cache.get(target)
                    if target_id:
                        calc_totals[target] = (target, target_id, calc_totals.get(target, 0)[2] + amount if target in calc_totals else amount)
                        # Исправление логики суммы выше: calc_totals хранит (name, id, sum_amount)
                        # Перепишем проще:
                        pass 

            # Пересоберем calc_totals корректно
            calc_totals = {} # Reset
            # (Логика выше была сложной, упростим)
            
            # Пройдемся еще раз для расчетных (или встроим в цикл выше, но так чище)
            # Для оптимизации лучше делать в одном цикле, но для читаемости разделим.
            # В реальном цикле выше мы просто накапливали сырые данные.
            
            # Вернемся к логике sum внутри цикла:
            # nutrients_for_item.append(...) - это добавлено
            
            # Расчетные:
            # Нам нужно просуммировать Methionine и Cystine -> Methionine + cystine
            # Это требует прохода по всем нутриентам.
            
            # Для упрощения и скорости на слабом сервере:
            # Простая агрегация в dict
            calc_map = {} # target_name -> total_amount
            
            # Проход по собранным нутриентам
            for n_name, n_id, n_amt in nutrients_for_item:
                if n_name in calculated:
                    target = calculated[n_name]
                    calc_map[target] = calc_map.get(target, 0) + n_amt
            
            # Добавляем итоговые расчетные
            for target_name, total_amt in calc_map.items():
                t_id = existing_nutr_cache.get(target_name)
                if t_id:
                    nutrients_for_item.append((target_name, t_id, total_amt))

            # --- 3. Формирование связей (Quantity) ---
            for n_name, n_id, amt in nutrients_for_item:
                key = (current_food_id, n_id)
                if key not in batch_seen_quants:
                    batch_seen_quants.add(key)
                    batch_quantities.append(
                        NutrientsQuantity(food_id=current_food_id, nutrient_id=n_id, amount=amt)
                    )
            
            # --- 4. Flush Batch (Запись в БД) ---
            # Если буфер переполнен - пишем
            # Размер буфера ограничен кол-вом связей. ~10 связей на еду * 200 еды = 2000 объектов
            if len(batch_quantities) >= 2000:
                with transaction.atomic():
                    NutrientsQuantity.objects.bulk_create(batch_quantities, ignore_conflicts=True)
                    quants_processed += len(batch_quantities)
                    # Очистка памяти
                    del batch_quantities[:] 
                    batch_seen_quants.clear()
                
                sys.stdout.write(f"\r   💾 Сохранено связей: {quants_processed}")
                sys.stdout.flush()

    # --- 5. Final Flush ---
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