from django.db import models


class Level(models.Model):
    level_code = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    objective_text = models.TextField(blank=True)
    briefing_title = models.CharField(max_length=200, blank=True)
    briefing_text = models.TextField(blank=True)
    briefing_hint = models.TextField(blank=True)
    order = models.PositiveIntegerField(unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.order}. {self.title}'


class InfoCategory(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class LevelItem(models.Model):
    CONTENT_TYPES = (
        ('dialogue', 'Dialogue'),
        ('image', 'Image'),
        ('chart', 'Chart'),
        ('table', 'Table'),
        ('text', 'Text'),
    )

    level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name='items')
    category = models.ForeignKey(InfoCategory, on_delete=models.CASCADE, related_name='items')
    item_code = models.CharField(max_length=100)
    title = models.CharField(max_length=200)
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES)
    content_text = models.TextField(blank=True)
    content_json = models.JSONField(default=dict, blank=True)
    is_initial_visible = models.BooleanField(default=True)
    is_key_item = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['sort_order']
        unique_together = ('level', 'item_code')

    def __str__(self):
        return f'{self.level.title} - {self.title}'


class DecisionConfig(models.Model):
    DECISION_TYPES = (
        ('single_choice', 'Single Choice'),
        ('slider', 'Slider'),
    )

    level = models.OneToOneField(Level, on_delete=models.CASCADE, related_name='decision')
    title = models.CharField(max_length=200)
    target_text = models.TextField()
    decision_type = models.CharField(max_length=30, choices=DECISION_TYPES)
    config_json = models.JSONField(default=dict)

    def __str__(self):
        return f'Decision - {self.level.title}'


class ResultRule(models.Model):
    level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name='result_rules')
    rule_name = models.CharField(max_length=100)
    condition_json = models.JSONField(default=dict)
    is_success = models.BooleanField(default=False)
    message = models.TextField()
    score = models.IntegerField(default=0)
    next_action = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f'{self.level.title} - {self.rule_name}'
