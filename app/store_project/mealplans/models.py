"""
Ingredients
    comprise Recipes
        comprise Meals
            comprise MealPlanDays
                comprise MealPlanWeeks
"""

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from store_project.mealplans.spoonacular import Spoonacular


User = get_user_model()


class DailyNutrition(models.Model):

    class ActivityLevel(models.IntegerChoices):
        SEDENTARY = 0, _("Sedentary")
        LOWACTIVE = 1, _("Low active")
        ACTIVE = 2, _("Active")
        HIGHACTIVE = 3, _("High active")

    class Goal(models.IntegerChoices):
        FAT_LOSS = 0, _("Fat loss")
        MAINTENANCE = 1, _("Maintenance")
        MUSCLE_GAIN = 2, _("Muscle gain")

    class Sex(models.TextChoices):
        MALE = "M", _("Male")
        FEMALE = "F", _("Female")
    
    created = models.DateTimeField(_("Time created"), auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, null=True)
    weight_kg = models.PositiveSmallIntegerField(blank=False, null=False)
    height_cm = models.PositiveSmallIntegerField(blank=False, null=False)
    age = models.PositiveSmallIntegerField(blank=False, null=False)
    sex = models.CharField(
        max_length=1,
        choices=Sex.choices,
        blank=False,
        null=False
    )
    activity_level = models.IntegerField(
        choices=ActivityLevel.choices,
        blank=False,
        null=False
    )
    goal = models.IntegerField(
        choices=Goal.choices,
        blank=False,
        null=False
    )

    def __str__(self):
        return f"{self.get_kcals()} kcals for {self.get_goal_display()}"

    def get_macros(self) -> dict:
        """Macros based on goals and daily calories"""

        kcals = self.get_kcals()

        protein_g = self.weight_kg * 2.2
        protein_kcals = protein_g * 4
        fat_g = kcals / 3 / 9  # one-third of calories, 9 kcal/g of fat
        fat_kcals = fat_g * 9
        carbs_kcals = kcals - protein_kcals - fat_kcals
        carbs_g = carbs_kcals / 4

        macros = {
            "fat": fat_g,
            "carbs": carbs_g,
            "protein": protein_g,
        }
        
        return macros

    def get_kcals(self):
        """The Mifflin-St. Jeor equation"""

        # base
        kcals = (10 * self.weight_kg) + (6.25 * self.height_cm) - (5 * self.age)
        
        # sex mods
        if self.sex == "M":
            kcals += 5
        else:
            kcals -= 161

        # activity
        if self.activity_level == self.ActivityLevel.SEDENTARY:
            kcals *= 1.1
        elif self.activity_level == self.ActivityLevel.LOWACTIVE:
            kcals *= 1.375
        elif self.activity_level == self.ActivityLevel.ACTIVE:
            kcals *= 1.65
        elif self.activity_level == self.ActivityLevel.HIGHACTIVE:
            kcals *= 1.9

        # goals
        if self.goal == self.Goal.MAINTENANCE:
            pass
        elif self.goal == self.Goal.FAT_LOSS:
            kcals -= 500
        elif self.goal == self.Goal.MUSCLE_GAIN:
            kcals += 500

        return kcals

    def get_meals(self) -> dict:
        """Return nutrient requirements for all meals of the day"""

        meals = {}

        # get macros and kcals adjusted for goals
        macros = self.get_macros()
        macros["calories"] = self.get_kcals()

        # get postworkout shake
        pwoshake_protein: float = 0.0

        if self.weight_kg * 2.2 < 150:  # under 150 lbs
            pwoshake_protein = 22  # grams
            pwoshake_servings = 1
        elif (self.weight_kg * 2.2 >= 150) and (self.weight_kg < 200):  # 150-200 lbs
            pwoshake_protein = 33
            pwoshake_servings = 1.5
        else:  # above 200 lbs
            pwoshake_protein = 44
            pwoshake_servings = 2

        pwoshake_carbs = pwoshake_protein * 2
        pwoshake_fat = 0.0

        meals["post-workout shake"] = {
            "protein": pwoshake_protein,
            "net carbs": pwoshake_carbs,
            "fat": pwoshake_fat,
            "calories": (pwoshake_protein * 4) + (pwoshake_carbs * 4) + (pwoshake_fat * 9),
            "recipe": [
                {
                    "name": "Protein Powder",
                    "amount": pwoshake_servings,
                    "unit": "servings",
                },
                {
                    "name": "Chocolate Almond Milk",
                    "amount": pwoshake_carbs * 8 / 18,  # 18 g carbs in 8 oz of milk
                    "unit": "oz",
                }
            ]
        }

        # calculate protein per meal
        remaining_protein = macros["protein"] - pwoshake_protein
        meal_protein = remaining_protein / 3

        # calculate carbs per anytime meal
        anytime_meal_carbs = 0.0

        if self.weight_kg * 2.2 < 150:  # under 150 lbs
            anytime_meal_carbs = 30  # grams
        elif (self.weight_kg * 2.2 >= 150) and (self.weight_kg < 200):  # 150-200 lbs
            anytime_meal_carbs = 40
        else:  # above 200 lbs
            anytime_meal_carbs = 50

        # calculate carbs per post-workout meal
        postworkout_meal_carbs = macros["carbs"] - (pwoshake_carbs) - (anytime_meal_carbs * 2)

        # calculate fat per post-workout meal

        # based on chicken breast nutrient composition
        # spoonacular ID of skinless, boneless chicken breast = 1055062
        # CALORIC BREAKDOWN - 11.4 kcal in 10 g chicken
        ### 78.46% protein  - 2.12 g in 10 g chicken
        ### 21.52% fat      - 0.26 g in 10 g chicken
        ### 0.0% carbs

        # grams of chicken = meal protein * 10 g chicken / 2.12 g protein
        chicken_g: float = meal_protein * 10 / 2.12
        # fat = grams of chicken * 0.26 g fat / 10 g chicken
        postworkout_meal_fat: float = chicken_g * 0.26 / 10

        meals["post-workout meal"] = {
            "protein": meal_protein,
            "net carbs": postworkout_meal_carbs,
            "fat": postworkout_meal_fat,
            "calories": (meal_protein * 4) + (postworkout_meal_carbs * 4) + (postworkout_meal_fat * 9),
            "recipe": [
                {
                    "name": "Chicken Breast",
                    "amount": chicken_g,
                    "unit": "g",
                },
                {
                    "name": "White Rice (cooked)",
                    "amount": postworkout_meal_carbs * 100 / 28,  # 28 g carbs in 100 g of white rice
                    "unit": "g",
                },
            ]
        }

        # calculate fat in remaining anytime meals
        remaining_fat = macros["fat"] - pwoshake_fat - postworkout_meal_fat
        anytime_meal_fat = remaining_fat / 2

        meals["anytime meal 1"] = {
            "protein": meal_protein,
            "net carbs": anytime_meal_carbs,
            "fat": anytime_meal_fat,
            "calories": (meal_protein * 4) + (anytime_meal_carbs * 4) + (anytime_meal_fat * 9),
            "recipe": [
                {
                    "name": "Grapeseed Oil",
                    "amount": 1,  # 13.6 g fat
                    "unit": "tbsp",
                },
                {
                    "name": "Eggs (whole)",
                    "amount": (anytime_meal_fat - 13.6 - 9.4) / 4.8,  # 4.8 g fat, 6.3 g protein in 1 large egg
                    "unit": "eggs",
                },
                {
                    "name": "93% Lean Ground Turkey",
                    "amount": 4,  # 9.4 g fat, 21.2 g protein
                    "unit": "oz",
                },
                {
                    "name": "Baby Carrots",
                    "amount": 20,  # 19.3 g net carbs, 1.9 g protein
                    "unit": "carrots",
                },
            ]
        }
        
        meals["anytime meal 2"] = {
            "protein": meal_protein,
            "net carbs": anytime_meal_carbs,
            "fat": anytime_meal_fat,
            "calories": (meal_protein * 4) + (anytime_meal_carbs * 4) + (anytime_meal_fat * 9),
        }

        return meals


class Ingredient(models.Model):
    name = models.CharField(max_length=250)

    def __str__(self):
        return f"{self.name}"


class Recipe(models.Model):
    name = models.CharField(max_length=250)
    description = models.CharField(max_length=500, blank=True)
    instructions = models.CharField(max_length=1000, blank=True)
    servings = models.SmallIntegerField()
    ingredients = models.ManyToManyField(Ingredient, through="RecipeIngredient", related_name="recipes")
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('mealplans:recipe_detail', kwargs={'pk': self.pk})


class RecipeIngredient(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    amount = models.FloatField()
    unit = models.CharField(max_length=20)
    calories = models.FloatField()
    fat = models.FloatField()
    carbs = models.FloatField()
    protein = models.FloatField()

    def __str__(self):
        return f"{self.amount} {self.unit} {self.ingredient.name}"


# class Meal(models.Model):
#     pass


# class MealDay(models.Model):
#     pass


# class MealWeek(models.Model):
#     pass
