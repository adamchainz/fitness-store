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


User = get_user_model()


class BMR(models.Model):

    class Sex(models.TextChoices):
        MALE = "M", _("Male")
        FEMALE = "F", _("Female")

    class ActivityLevel(models.IntegerChoices):
        SEDENTARY = 0, _("Sedentary")
        LOWACTIVE = 1, _("Low active")
        ACTIVE = 2, _("Active")
        HIGHACTIVE = 3, _("High active")
    
    created = models.DateTimeField(_("Time created"), auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False)
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

    def __str__(self):
        return f"BMR for {self.user.name}"

    def get_mifflin(self):
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

        return kcals


# class Ingredient(models.Model):
#     pass


# class Recipe(models.Model):
#     pass


# class Meal(models.Model):
#     pass


# class MealDay(models.Model):
#     pass


# class MealWeek(models.Model):
#     pass
