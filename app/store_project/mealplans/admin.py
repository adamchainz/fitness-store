from django.contrib import admin

from store_project.mealplans.models import BMR


@admin.register(BMR)
class BMRAdmin(admin.ModelAdmin):
    """BMR admin view"""

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
        return obj.get_mifflin()
