from django.contrib import admin

from .models import DecisionConfig, InfoCategory, Level, LevelItem, ResultRule


@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = ('order', 'title', 'level_code', 'is_active')
    ordering = ('order',)


@admin.register(InfoCategory)
class InfoCategoryAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')


@admin.register(LevelItem)
class LevelItemAdmin(admin.ModelAdmin):
    list_display = ('level', 'title', 'item_code', 'category', 'content_type', 'is_key_item', 'sort_order')
    list_filter = ('level', 'category', 'content_type')
    search_fields = ('title', 'item_code')


@admin.register(DecisionConfig)
class DecisionConfigAdmin(admin.ModelAdmin):
    list_display = ('level', 'title', 'decision_type')


@admin.register(ResultRule)
class ResultRuleAdmin(admin.ModelAdmin):
    list_display = ('level', 'rule_name', 'is_success', 'score', 'next_action')
    list_filter = ('level', 'is_success')
