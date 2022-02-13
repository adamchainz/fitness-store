from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class MealplansConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'store_project.mealplans'
    verbose_name = _("Meal plans")
