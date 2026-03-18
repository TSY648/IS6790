from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='InfoCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=50, unique=True)),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Level',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level_code', models.CharField(max_length=50, unique=True)),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('order', models.PositiveIntegerField(unique=True)),
                ('is_active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='ResultRule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rule_name', models.CharField(max_length=100)),
                ('condition_json', models.JSONField(default=dict)),
                ('is_success', models.BooleanField(default=False)),
                ('message', models.TextField()),
                ('score', models.IntegerField(default=0)),
                ('next_action', models.CharField(blank=True, max_length=50)),
                ('level', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='result_rules', to='levels.level')),
            ],
        ),
        migrations.CreateModel(
            name='LevelItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_code', models.CharField(max_length=100)),
                ('title', models.CharField(max_length=200)),
                ('content_type', models.CharField(choices=[('dialogue', 'Dialogue'), ('image', 'Image'), ('chart', 'Chart'), ('table', 'Table'), ('text', 'Text')], max_length=20)),
                ('content_text', models.TextField(blank=True)),
                ('content_json', models.JSONField(blank=True, default=dict)),
                ('is_initial_visible', models.BooleanField(default=True)),
                ('is_key_item', models.BooleanField(default=False)),
                ('sort_order', models.PositiveIntegerField(default=1)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='levels.infocategory')),
                ('level', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='levels.level')),
            ],
            options={'ordering': ['sort_order'], 'unique_together': {('level', 'item_code')}},
        ),
        migrations.CreateModel(
            name='DecisionConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('target_text', models.TextField()),
                ('decision_type', models.CharField(choices=[('single_choice', 'Single Choice'), ('slider', 'Slider')], max_length=30)),
                ('config_json', models.JSONField(default=dict)),
                ('level', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='decision', to='levels.level')),
            ],
        ),
    ]
