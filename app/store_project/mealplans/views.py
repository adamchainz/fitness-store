from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import redirect, render

from store_project.mealplans.forms import DailyNutritionForm, RecipeCreateForm, RecipeLookupForm
from store_project.mealplans.models import DailyNutrition, Ingredient, Recipe, RecipeIngredient
from store_project.mealplans.spoonacular import Spoonacular


@login_required()
def daily_nutrition(request):

    if request.method == "POST":
        form = DailyNutritionForm(request.POST)
        if form.is_valid():
            if request.user.is_authenticated:
                instance = form.save(commit=False)
                instance.user = request.user
                instance.save()
                messages.success(request, "Form saved successfully")
    else:
        form = DailyNutritionForm()
    
    context = {
        "form": form,
        "macros": DailyNutrition.objects.filter(user=request.user).last(),
    }
            
    return render(request, "mealplans/daily_nutrition_form.html", context)


@login_required()
def index(request):

    macros = DailyNutrition.objects.filter(user=request.user).last()

    return render(request, "mealplans/index.html", {
        "macros": macros,
        "meals": macros.get_meals(),
    })


@login_required()
def recipe_lookup(request):
    
    if request.method == "POST":
        form = RecipeLookupForm(request.POST)
        if form.is_valid():
            spoon = Spoonacular()
            ingredients = spoon.parse_ingredients(
                form.cleaned_data["recipe"],
                form.cleaned_data["servings"]
            )
            
            total = {
                "Calories": {
                    "amount": 0,
                    "unit": "kcal",
                },
                "Fat": {
                    "amount": 0,
                    "unit": "g",
                },
                "Net Carbohydrates": {
                    "amount": 0,
                    "unit": "g",
                },
                "Protein": {
                    "amount": 0,
                    "unit": "g",
                },
            }

            for ingredient in ingredients:
                for nutrient in ingredient["nutrition"]["nutrients"]:
                    if nutrient["name"] in total.keys():
                        total[nutrient["name"]]["amount"] += nutrient["amount"]

            request.session["ingredients"] = ingredients
            request.session["total"] = total

            context = {
                "ingredients": ingredients,
                "total": total,
            }

            return render(request, "mealplans/nutrition_label.html", context)
    else:
        form = RecipeLookupForm()
    
    context = {
        "lookup_form": form,
    }
    
    return render(request, "mealplans/recipe_lookup.html", context)


def recipe_detail(request, pk):
    recipe = Recipe.objects.get(pk=pk)
    ingredients = RecipeIngredient.objects.filter(recipe=recipe)
    return render(request, "mealplans/recipe_detail.html", {
        "recipe": recipe,
        "ingredients": ingredients,
    })


def recipe_list(request):
    recipes = Recipe.objects.all()
    return render(request, "mealplans/recipe_list.html", {"recipes": recipes})


@login_required()
def modal(request):

    ingredients = request.session.get("ingredients", None)
    total = request.session.get("total", None)

    if request.method == "POST":
        form = RecipeCreateForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                recipe = Recipe.objects.create(
                    name=form.cleaned_data["name"],
                    description=form.cleaned_data["description"],
                    instructions=form.cleaned_data["instructions"],
                    servings=form.cleaned_data["servings"],
                    author=request.user,
                )

                ingredient_objs = []
                for ingredient in ingredients:
                    ingredient_obj = Ingredient.objects.create(name=ingredient["originalName"])
                    fields = {
                        "ingredient": ingredient_obj,
                        "recipe": recipe,
                        "amount": ingredient["amount"],
                        "unit": ingredient["unit"],
                    }
                    for nutrient in ingredient["nutrition"]["nutrients"]:
                        if nutrient["name"] in total.keys():
                            fields[nutrient["name"]] = nutrient["amount"]

                    fields["carbs"] = fields.pop("Net Carbohydrates")
                    fields["fat"] = fields.pop("Fat")
                    fields["protein"] = fields.pop("Protein")
                    fields["calories"] = fields.pop("Calories")
                    RecipeIngredient.objects.create(**fields)

            messages.success(request, f"Successfully saved Recipe: {recipe.name}")
            return redirect("mealplans:recipe_lookup")

    else:
        form = RecipeCreateForm()

    context = {
        "create_form": form,
        "ingredients": ingredients,
        "total": total,
    }

    return render(request, "mealplans/modal.html", context)
