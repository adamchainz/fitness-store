from django.urls import path

from store_project.mealplans import views


app_name = "mealplans"
urlpatterns = [
    path("calculate/", views.daily_nutrition, name="daily_nutrition"),
    path("recipes/<int:pk>/", views.recipe_detail, name="recipe_detail"),
    path("recipes/lookup/", views.recipe_lookup, name="recipe_lookup"),
    path("recipes/", views.recipe_list, name="recipe_list"),
    path("modal/", views.modal, name="modal"),
    path("", views.index, name="index"),
]