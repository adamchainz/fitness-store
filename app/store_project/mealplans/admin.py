from django.contrib import admin

from store_project.mealplans import models


@admin.register(models.DailyNutrition)
class DailyNutritionAdmin(admin.ModelAdmin):
    """DailyNutrition admin view"""

    list_display = [
        "user",
        "created",
        "view_kcals",
    ]
    ordering = ["-created"]
    search_fields = [
        "user",
    ]

    @admin.display()
    def view_kcals(self, obj):
        return obj.get_kcals()


@admin.register(models.Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Recipe)
class RecipeAdmin(admin.ModelAdmin):
    pass


@admin.register(models.RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    pass
