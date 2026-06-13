# pep/scripts/load_recommendations.py
import os
import sys
import django

# --- НАСТРОЙКА DJANGO ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "foodcalc.settings")
django.setup()

from calc.models import RecommendedNutrientLevelsDM, RecommendedNutrientLevels1000kcal
from animal.models import AnimalType, PetStage
from food.models import NutrientsName
from django.db import transaction

# Маппинг названий из txt файлов в имена нутриентов в БД
name_map = {
    'Vitamin A, IU': 'Vitamin A',
    'PUFA 18:2 n-6 c,c': 'Linoleic acid (omega-6)',
    'PUFA 20:4': 'Arachidonic acid (omega-6)',
    'PUFA 18:3 n-3 c,c,c (ALA)': 'Alpha-linolenic acid (omega-3)',
}

# КОНФИГУРАЦИЯ ФАЙЛОВ
# Формат: (имя_файла, title_AnimalType, desc_AnimalType, '1000kcal'/'DM', [Список названий стадий])
FILES_CONFIG = [
    ('cat_1000_kcal.txt', 'Cat', 'Кот', '1000kcal', 
     ['Kitten Growth', 'Adult Maintenance', 'Senior/Weight Loss', 'Gestation/Lactation']),
    ('dog_1000_kcal.txt', 'Dog', 'Собака', '1000kcal', 
     ['Puppy Growth', 'Adult Maintenance', 'Senior/Less Active', 'Gestation', 'Lactation']),
    ('cat_dm.txt', 'Cat', 'Кот', 'DM', 
     ['Kitten Growth', 'Adult Maintenance', 'Senior/Weight Loss', 'Gestation/Lactation']),
    ('dog_dm.txt', 'Dog', 'Собака', 'DM', 
     ['Puppy Growth', 'Adult Maintenance', 'Senior/Less Active', 'Gestation', 'Lactation']),
]

def get_or_create_type(title, desc):
    t, _ = AnimalType.objects.get_or_create(
        title=title, defaults={'description': desc, 'info': 'NRC Standards'}
    )
    return t

def get_or_create_stage(pet_type, stage_name):
    code = stage_name.replace(' ', '_').replace('/', '_').lower()
    # Создаем стадию с дефолтными значениями. 
    # Их можно будет позже отредактировать через Django Admin.
    s, created = PetStage.objects.get_or_create(
        pet_stage=code,
        defaults={
            'pet_type': pet_type,
            'description': stage_name,
            'sterilized': False,
            'nursing': False,
            'age_start': 0,
            'age_finish': 999,
            'MER_power': 1.0
        }
    )
    return s, created

def process_file(filename, animal_title, animal_desc, model_key, stage_names):
    filepath = os.path.join(os.path.dirname(__file__), filename)
    if not os.path.exists(filepath):
        print(f"  ⏭ {filename} не найден. Пропуск.")
        return

    print(f"  📂 Загрузка {filename} ({model_key})...")
    
    animal_type = get_or_create_type(animal_title, animal_desc)
    stages = [get_or_create_stage(animal_type, s)[0] for s in stage_names]

    ModelClass = RecommendedNutrientLevels1000kcal if model_key == '1000kcal' else RecommendedNutrientLevelsDM

    batch_objs = []
    total_recs = 0
    skipped = 0

    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or '/' not in line:
                continue

            name_part, data_part = line.split('/', 1)
            name_part = name_part.strip()
            name_part = name_map.get(name_part, name_part)

            parts = data_part.split()
            if not parts: continue
            
            # Последняя часть - единица измерения (игнорируем, т.к. она уже в NutrientsName)
            values_str = parts[:-1]

            if len(values_str) != len(stages):
                skipped += 1
                continue

            try:
                values = [float(v.replace(',', '.')) for v in values_str] # поддержка запятых
            except ValueError:
                skipped += 1
                continue

            try:
                nutrient = NutrientsName.objects.get(name=name_part)
            except NutrientsName.DoesNotExist:
                skipped += 1
                continue

            for i, val in enumerate(values):
                total_recs += 1
                batch_objs.append(ModelClass(
                    pet_type=animal_type,
                    pet_stage=stages[i],
                    nutrient_name=nutrient,
                    nutrient_amount=val
                ))

            if len(batch_objs) >= 1000:
                ModelClass.objects.bulk_create(batch_objs, ignore_conflicts=True)
                batch_objs.clear()
                sys.stdout.write(f"\r    💾 Записано: {total_recs}")
                sys.stdout.flush()

    if batch_objs:
        ModelClass.objects.bulk_create(batch_objs, ignore_conflicts=True)

    print(f"\n  ✅ Готово {filename}: {total_recs} записей добавлено, {skipped} строк пропущено.")


if __name__ == "__main__":
    print("=== НАЧАЛО ЗАГРУЗКИ РЕКОМЕНДАЦИЙ ===")
    # Оборачиваем в транзакцию. Если что-то пойдет не так, всё откатится.
    with transaction.atomic():
        for conf in FILES_CONFIG:
            process_file(*conf)
    print("=== ВСЕ РЕКОМЕНДАЦИИ УСПЕШНО ЗАГРУЖЕНЫ ===")