"""
Connect with spoonacular.com API

Each request requires:
- apiKey: from the spoonacular.com user console

Each response comes with:
- X-API-Quota-Request: The number of points used by the request.
- X-API-Quota-Used: The number of points used in total today.
- X-API-Quota-Left: The number of points left today.
"""

import os
import requests


class Spoonacular:
    def __init__(self):
        try:
            self.apikey = os.environ.get("SPOONACULAR_API_KEY")
        except KeyError:
            raise KeyError("SPOONACULAR_API_KEY environment variable not set")

    def compute_ingredient_amount(
        self, ingredient_id, nutrient: str, target_amount: int, target_unit: str = "oz"
    ) -> dict:
        """Compute the amount you need of a certain ingredient for a certain nutritional goal.

        For example, how much pineapple do you have to eat to get 10 grams of protein?"""

        endpoint = (
            f"https://api.spoonacular.com/food/ingredients/{ingredient_id}/amount"
        )
        params = {
            "apiKey": self.apikey,
            "nutrient": nutrient,
            "target": target_amount,
            "unit": target_unit,
        }
        r = requests.get(endpoint, params=params)
        return r.json()

    def get_anytime_meals(self, num_of_results=2) -> list[dict]:
        """Search for meals with carbs < 50g and protein > 30g"""

        endpoint = "https://api.spoonacular.com/recipes/findByNutrients"
        params = {
            "apiKey": self.apikey,
            "maxCarbs": 50,
            "minProtein": 30,
            "maxFat": 30,
            "number": num_of_results,
            "random": True,
        }
        r = requests.get(endpoint, params=params)
        return r.json()

    def get_postworkout_meals(self, num_of_results=1) -> list[dict]:
        """Search for meals with carbs > 50g and protein > 30g"""

        endpoint = "https://api.spoonacular.com/recipes/findByNutrients"
        params = {
            "apiKey": self.apikey,
            "minCarbs": 50,
            "minProtein": 30,
            "maxFat": 30,
            "number": num_of_results,
            "random": True,
        }
        r = requests.get(endpoint, params=params)
        return r.json()

    def ingredient_search(self, query, num_of_results=1) -> list:
        """Search for a list of ingredients"""

        endpoint = "https://api.spoonacular.com/food/ingredients/search"
        params = {
            "apiKey": self.apikey,
            "query": query,
            "number": num_of_results,
            "metaInformation": True,
        }
        r = requests.get(endpoint, params=params)
        return r.json()["results"]

    def nutrition_of(self, ingredient_id, amount, unit) -> list:
        """Get nutrition facts for a food"""

        endpoint = (
            f"https://api.spoonacular.com/food/ingredients/{ingredient_id}/information"
        )
        params = {
            "apiKey": self.apikey,
            "amount": amount,
            "unit": unit,
        }
        r = requests.get(endpoint, params=params)
        return r.json()["nutrition"]["nutrients"]

    def recipe_info(self, recipe_id) -> dict:
        """Get recipe steps, ingredients, nutrition facts, and more"""

        endpoint = f"https://api.spoonacular.com/recipes/{recipe_id}/information"
        params = {
            "apiKey": self.apikey,
            "includeNutrition": True,
        }
        r = requests.get(endpoint, params=params)
        return r.json()

    def recipe_info_bulk(self, recipe_ids: list) -> list[dict]:
        """Get recipe steps, ingredients, nutrition facts, and more"""

        endpoint = "https://api.spoonacular.com/recipes/informationBulk"
        params = {
            "apiKey": self.apikey,
            "ids": ",".join(recipe_ids),
            "includeNutrition": True,
        }
        r = requests.get(endpoint, params=params)
        return r.json()

    def search_grocery_products(self, query, num_of_results=1) -> list:
        """What does the store have?"""

        endpoint = "https://api.spoonacular.com/food/products/search"
        params = {
            "apiKey": self.apikey,
            "query": query,
            "number": num_of_results,
            "addProductInformation": True,
        }
        r = requests.get(endpoint, params=params)
        return r.json()["products"]

    def calc_protein_for_meal(self, query: str, target) -> dict:
        """
        # find ingredient
        spoon.ingredient_search(query)

        # find volume based on remaining macros and number of meals
        spoon.compute_ingredient_amount(id, nutrient, target)

        # get nutrition facts
        spoon.nutrition_of(id, amount, unit)
        """

        # find ingredient
        protein: dict = self.ingredient_search(query)[0]  # assuming one accurate result

        # find volume based on remaining macros and number of meals
        protein["serving_size"]: dict = self.compute_ingredient_amount(protein["id"], "protein", target)

        # get nutrition facts
        nutrients = self.nutrition_of(protein["id"], protein["serving_size"]["amount"], protein["serving_size"]["unit"])

        protein["nutrients"] = {}
        nutrients_of_interest = ["Calories", "Fat", "Net Carbohydrates", "Protein"]

        for n in nutrients:
            if n["name"] in nutrients_of_interest:
                protein["nutrients"][n["name"]] = n["amount"]

        return protein

    def recipe_search(self, query: str, num_of_results: int=10) -> dict:
        """Find a recipe from the internet"""

        endpoint = "https://api.spoonacular.com/recipes/complexSearch"
        params = {
            "apiKey": self.apikey,
            "query": query,
            "intolerances": "gluten,dairy",
            "number": num_of_results,
            "minCalories": 200,
            "maxCalories": 350,
            "minProtein": 15,
        }
        r = requests.get(endpoint, params=params)
        return r.json()

    def parse_ingredients(self, ingredient_list, servings) -> list:

        endpoint = "https://api.spoonacular.com/recipes/parseIngredients"
        params = {
            "apiKey": self.apikey,
        }
        data = {
            "ingredientList": ingredient_list,
            "servings": servings,
            "includeNutrition": True,
        }
        r = requests.post(endpoint, data=data, params=params)
        return r.json()
