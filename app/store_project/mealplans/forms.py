from django import forms

from store_project.mealplans.models import DailyNutrition, Recipe


class DailyNutritionForm(forms.ModelForm):

    class Meta:
        model = DailyNutrition
        fields = [
            "weight_kg",
            "height_cm",
            "age",
            "sex",
            "activity_level",
            "goal",
        ]


class RecipeLookupForm(forms.Form):
    recipe = forms.CharField(
        help_text="List each ingredient's quantity and name on separate lines. Use numbers for the amounts.",
        widget=forms.Textarea
    )
    servings = forms.IntegerField()


class RecipeCreateForm(forms.Form):
    name = forms.CharField(max_length=250)
    servings = forms.IntegerField()
    description = forms.CharField(
        max_length=500,
        widget=forms.Textarea
    )
    instructions = forms.CharField(
        max_length=1000,
        widget=forms.Textarea
    )
