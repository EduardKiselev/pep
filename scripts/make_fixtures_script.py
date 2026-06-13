# pep/scripts/make_fixtures_script.py
import json, os, sys
import django

# --- НАСТРОЙКА DJANGO ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "foodcalc.settings")
django.setup()

from food.models import Food, NutrientsName, NutrientsQuantity
from django.contrib.auth import get_user_model
from django.db import transaction
from itertools import islice

User = get_user_model()
SUPERUSER_PASSWORD = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
if not SUPERUSER_PASSWORD:
    raise ValueError("⚠️ ОШИБКА: Не установлена DJANGO_SUPERUSER_PASSWORD в .env")

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
    'Methionine': 'Methionine + cystine', 'Cystine': 'Methionine + cystine',
    'Phenylalanine': 'Phenylalanine + tyrosine', 'Tyrosine': 'Phenylalanine + tyrosine',
    'PUFA 20:5 n-3 (EPA)': 'EPA + DHA (omega-3)', 'PUFA 22:6 n-3 (DHA)': 'EPA + DHA (omega-3)',
}

name_map = {
    'Vitamin A, IU': 'Vitamin A', 'PUFA 18:2 n-6 c,c': 'Linoleic acid (omega-6)',
    'PUFA 20:4': 'Arachidonic acid (omega-6)', 'PUFA 18:3 n-3 c,c,c (ALA)': 'Alpha-linolenic acid (omega-3)'
}

files = [
    ('FoodData_Central_sr_legacy_food_json_2018-04.json', 'SRLegacyFoods', 'legacy'),
    ('surveyDownload.json', 'SurveyFoods', 'survey'),
    ('FoodData_Central_foundation_food_json_2026-04-30.json', 'FoundationFoods', 'foundation2'),
]

# Автор
try:
    author_user = User.objects.get(username='FoodData')
except User.DoesNotExist:
    author_user = User.objects.create_superuser(username='FoodData', email='fooddata@example.com', password=SUPERUSER_PASSWORD)
    print("✅ Создан пользователь FoodData")

def process_file(file_info):
    filename, key, suffix = file_info
    filepath = os.path.join(os.path.dirname(__file__), filename)
    if not os.path.exists(filepath):
        print(f"   Файл {filename} не найден. Пропуск.")
        return

    print(f"\n📦 Чтение {filename}...")
    with open(filepath, encoding='utf-8') as f:
        data = json.load(f).get(key, [])
    
    total_items = len(data)
    print(f"   Найдено записей: {total_items}. Парсинг в память...")

    foods_to_create = {}
    unique_nutrients = {}
    quantities_buffer = []
    energy_added = set()

    for i, item in enumerate(data):
        if i % 5000 == 0 and i > 0:
            sys.stdout.write(f"\r   🔍 Распарсено: {i}/{total_items} ({i/total_items*100:.1f}%)")
            sys.stdout.flush()

        desc = item['description']
        fdcId = item['fdcId']
        ndbNumber = item.get('ndbNumber', 0)
        category = 'None'
        cat_data = item.get('foodCategory')
        if isinstance(cat_data, dict): category = cat_data.get('description', 'None')
        else:
            wweia = item.get('wweiaFoodCategory')
            if isinstance(wweia, dict): category = wweia.get('wweiaFoodCategoryDescription', 'None')

        if desc not in foods_to_create:
            foods_to_create[desc] = {'description': desc, 'fdcId': fdcId, 'ndbNumber': ndbNumber, 'foodCategory': category, 'author': author_user}

        current_item_calc = {}
        for fn in item.get('foodNutrients', []):
            amount = fn.get('amount') or fn.get('median')
            if amount is None: continue

            name = fn['nutrient']['name']
            unit = fn['nutrient'].get('unitName', 'g')
            if unit == 'µg': unit = 'ug'
            if name in name_map: name = name_map[name]

            if name == 'Energy':
                if unit == 'kJ': amount = round(amount / 4.184, 2)
                if desc in energy_added: continue
                energy_added.add(desc)
                unit = 'kcal'

            if name not in unique_nutrients:
                is_pub = 1 if name in good_nutrients_set else 0
                unique_nutrients[name] = {'unit': unit, 'is_pub': is_pub, 'order': nutrients_order.get(name, 100)}

            quantities_buffer.append((desc, name, amount))

            if name in calculated:
                target = calculated[name]
                if target not in unique_nutrients:
                    unique_nutrients[target] = {'unit': unit, 'is_pub': 1 if target in good_nutrients_set else 0, 'order': nutrients_order.get(target, 100)}
                current_item_calc[target] = current_item_calc.get(target, 0) + amount
        
        for c_name, c_val in current_item_calc.items():
            quantities_buffer.append((desc, c_name, c_val))

    sys.stdout.write(f"\r   ✅ Распарсено: {total_items}/{total_items} (100.0%)\n")
    sys.stdout.flush()

    print("   🌱 Синхронизация нутриентов...")
    existing_nutr = dict(NutrientsName.objects.filter(name__in=unique_nutrients.keys()).values_list('name', 'id'))
    
    nutr_to_create = [NutrientsName(name=n, unit_name=i['unit'], is_published=bool(i['is_pub']), order=i['order']) 
                      for n, i in unique_nutrients.items() if n not in existing_nutr]
    if nutr_to_create:
        NutrientsName.objects.bulk_create(nutr_to_create, batch_size=1000)
        print(f"   + Создано {len(nutr_to_create)} нутриентов")
        existing_nutr.update(dict(NutrientsName.objects.filter(name__in=[n.name for n in nutr_to_create]).values_list('name', 'id')))

    print("   🥗 Синхронизация продуктов...")
    existing_food = dict(Food.objects.filter(description__in=foods_to_create.keys()).values_list('description', 'id'))
    food_to_create = [Food(**foods_to_create[d]) for d in foods_to_create if d not in existing_food]
    if food_to_create:
        Food.objects.bulk_create(food_to_create, batch_size=500)
        print(f"   + Создано {len(food_to_create)} продуктов")
        existing_food.update(dict(Food.objects.filter(description__in=[f.description for f in food_to_create]).values_list('description', 'id')))

    print(f"   🔗 Запись связей (NutrientsQuantity)...")
    total_quants = len(quantities_buffer)
    batch_objs = []
    seen = set()
    batch_size = 2000
    processed = 0

    for desc, n_name, amount in quantities_buffer:
        processed += 1
        if processed % 10000 == 0:
            sys.stdout.write(f"\r   📝 Обработано связей: {processed}/{total_quants} ({processed/total_quants*100:.1f}%)")
            sys.stdout.flush()

        f_id, n_id = existing_food.get(desc), existing_nutr.get(n_name)
        if f_id and n_id:
            key = (f_id, n_id)
            if key not in seen:
                seen.add(key)
                batch_objs.append(NutrientsQuantity(food_id=f_id, nutrient_id=n_id, amount=amount))
                
                if len(batch_objs) >= batch_size:
                    NutrientsQuantity.objects.bulk_create(batch_objs, ignore_conflicts=True)
                    batch_objs = []

    if batch_objs:
        NutrientsQuantity.objects.bulk_create(batch_objs, ignore_conflicts=True)
        
    sys.stdout.write(f"\r   🎉 Все связи записаны ({processed} шт). Очистка памяти...\n")
    sys.stdout.flush()

if __name__ == "__main__":
    print("=== НАЧАЛО ЗАГРУЗКИ ===")
    for f in files:
        with transaction.atomic():
            process_file(f)
    print("=== ГОТОВО ===")