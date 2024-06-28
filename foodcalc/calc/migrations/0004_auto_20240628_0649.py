# Generated by Django 3.2.16 on 2024-06-28 06:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('calc', '0003_animals'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnimalTypes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=50)),
                ('description', models.TextField(blank=True, verbose_name='Описание')),
            ],
        ),
        migrations.AddField(
            model_name='animals',
            name='age',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='animals',
            name='mass',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='animals',
            name='name',
            field=models.CharField(default='Noname', max_length=50),
        ),
        migrations.AddField(
            model_name='animals',
            name='type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='type', to='calc.animaltypes'),
        ),
    ]
