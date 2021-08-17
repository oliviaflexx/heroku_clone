from os import name
from django.db.models.query import QuerySet, Prefetch
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from .models import or_ingredients, recipe_ingredients3, recipes3, ingredients3, genres3, user_recipes, grocery_list
from django import template
from .funky import add_up, sub_out
from django.core.paginator import Paginator
import json

def checky(request):
    if request.POST.get('action') == 'post':
        id = request.POST.get('postid')
        grocery = grocery_list.objects.get(pk=id)
        if grocery.checked == True:
            grocery.checked = False
            grocery.save()
            checked = 'no'
        else:
            grocery.checked = True
            grocery.save()
            checked = 'yes'

        return JsonResponse({'id': id, 'checked': checked})

def add_ingredient(request):
    print("yes")
    if request.POST.get('action') == 'post':
        id = request.POST.get('postid')
        ingredient_list = []
        ingredient = ingredients3.objects.get(pk=id)
        if request.user not in ingredient.checked.all():
            print("action to check")
            ingredient.checked.add(request.user)
            ingredient_list.append(ingredient)
            if or_ingredients.objects.filter(in_name=ingredient).exists():
                print('exists')
                for or_name in or_ingredients.objects.filter(in_name=ingredient):  
                    thing = ingredients3.objects.get(name=or_name.or_name)
                    thing.checked.add(request.user)
                    ingredient_list.append(thing)

            for sel_ing in ingredient_list:
                recipes = recipe_ingredients3.objects.select_related('recipe').filter(ingredient = sel_ing)
                for recipe in recipes:
                    total = recipe.recipe.ingredients.all().count()
                    print(recipe.recipe.name)
                    print(total)
                    percent = (1 / total) * 100
                    percent = round(percent, 0)
                    entry, created = user_recipes.objects.get_or_create(recipe = recipe.recipe, user = request.user)
                    if created:
                        entry.percent = 0
                    print(f'before percent:', entry.percent)
                    entry.percent = entry.percent + percent
                    entry.save()
                    print(f'after percent:', entry.percent)
        else:
            print('action to not check')
            ingredient.checked.remove(request.user)
            ingredient_list.append(ingredient)
            if or_ingredients.objects.filter(in_name=ingredient).exists():
                print('exists')
                for or_name in or_ingredients.objects.filter(in_name=ingredient):  
                    thing = ingredients3.objects.get(name=or_name.or_name)
                    thing.checked.remove(request.user)
                    ingredient_list.append(thing)

            for sel_ing in ingredient_list:
                recipes = recipe_ingredients3.objects.select_related('recipe').filter(ingredient = sel_ing)
                for recipe in recipes:
                    total = recipe.recipe.ingredients.all().count()
                    print(f'NEW RECIPE:', recipe.recipe.name)
                    print(f'Total ingredients:', total)
                    percent = (1 / total) * 100
                    percent = round(percent, 0)
                    entry, created = user_recipes.objects.get_or_create(recipe = recipe.recipe, user = request.user)
                    if created:
                        entry.percent = 0
                    print(f'before percent:', entry.percent)
                    entry.percent = entry.percent - percent
                    entry.save()
                    print(f'after percent:', entry.percent)

        return JsonResponse({'id': id})

def index(response):
    return render(response, "main/home.html")

def showmore(request):
    if request.POST.get('action') == 'post':
        id = int(request.POST.get('postid'))
        recipe = recipes3.objects.get(id=id)

        calories = str(recipe.calories) + ' Calories'
        time = str(recipe.time) + ' Minutes'

        genres = ''
        for genre in recipe.genre.all():
            if genres == '':
                genres = str(genre)
            else:
                genres = genres + ' ,' + str(genre)

        print(recipe.name)
        print(calories)
        print(genres)
        return JsonResponse({'id': recipe.id, 'calories': calories, 'time': time, 'genres': genres })

def like(request):
    if request.POST.get('action') == 'post':
        id = int(request.POST.get('postid'))
        recipe = recipes3.objects.get(id=id)
        if request.user in recipe.liked.all():
            print('unliked')
            result = 'unliked'
            recipe.liked.remove(request.user)
        else:
            if request.user in recipe.disliked.all():
                recipe.disliked.remove(request.user)
            result = 'liked'
            print('liked')
            recipe.liked.add(request.user)
        return JsonResponse({'id': recipe.id, 'result': result})

def dislike(request):
    if request.POST.get('action') == 'post':
        id = int(request.POST.get('postid'))
        recipe = recipes3.objects.get(id=id)
        if request.user in recipe.disliked.all():
            print('undisliked')
            result = 'undisliked'
            recipe.disliked.remove(request.user)
        else:
            if request.user in recipe.liked.all():
                recipe.liked.remove(request.user)
            recipe.disliked.add(request.user)
            result = 'disliked'
            print('disliked')

        return JsonResponse({'result': result, 'id': id})


def add_recipe(request):
    if request.POST.get('action') == 'post':
        id = request.POST.get('postid')
        recipe = recipes3.objects.get(id=id)

        if request.user in recipe.checked.all():
            result = 'unchecked'
            sub_out(recipe, request.user)
            print(result)
        else:
            result = 'checked'
            add_up(recipe, request.user)
            print(result)

        return JsonResponse({'result': result, 'id':id})

def allRecipes(response):
    if response.user.is_authenticated:
        orderby = meal_type = veggie = vegan = gluten_free = 'none'
        if response.method == 'POST':
            print(response.POST)
            posts = recipes3.objects.prefetch_related('checked', 'liked', 'disliked').order_by('name')
            if response.POST.get('save'):
                genres = genres3.objects.all()
                if response.POST.__contains__('meal_type'):
                    meal0 = response.POST.get('meal_type')
                    if meal0 =='lunch':
                        breakfast = genres.get(name='breakfast')
                        dessert = genres.get(name='dessert')
                        posts = posts.exclude(genre=breakfast).exclude(genre=dessert)
                        meal_type = 'lunch'
                    else:
                        # meal = genres3.objects.get(name=meal0)
                        meal = genres.get(name=meal0)
                        posts = posts.filter(genre=meal.id)
                        meal_type = meal0

                if response.POST.__contains__('restrict'):
                    restricts = response.POST.getlist('restrict')
                    for restrict in restricts:
                        if restrict == 'gluten':
                            restrict = 'gluten free'
                            gluten_free = restrict
                            print('GLUTEN')
                        if restrict == 'vegeterian':
                            veggie = restrict
                            print('VEGGIE')
                            print(veggie)
                        if restrict == 'vegan':
                            vegan = restrict
                            print(vegan)
                        restricter = genres.get(name=restrict)
                        posts = posts.filter(genre=restricter)

                if response.POST.__contains__('orderby'):
                    order = response.POST.get('orderby')
                    orderby = order
                    if order == 'calories':
                        posts = posts.exclude(calories=0).order_by('calories')
                    else:
                        posts = posts.exclude(time=0).order_by('time')
                else:
                    posts = posts.order_by('name')

            paginator = Paginator(posts, 25)
            page = response.GET.get('page')
            posts = paginator.get_page(page)

            return render(response, "main/allrecipes.html", {'posts':posts, 'orderby': orderby, 'meal_type': meal_type, 'veggie':veggie, 'vegan':vegan, 'gluten_free': gluten_free})
        
        else:
            posts = recipes3.objects.prefetch_related('checked', 'liked', 'disliked').order_by('name')
            paginator = Paginator(posts, 25)
            page = response.GET.get('page')
            posts = paginator.get_page(page)
            
            return render(response, "main/allrecipes.html", {'posts':posts, 'user': response.user, 'orderby': orderby, 'meal_type': meal_type, 'veggie':veggie, 'vegan':vegan, 'gluten_free': gluten_free})
    else:
        return render(response, "main/allrecipes.html")


def ingredientPicker(response):
    if response.user.is_authenticated:
        if response.method == 'POST':
            print(response.POST)
            if response.POST.get('save') == 'select':
                non_ors = response.user.ing_checked.exclude(or_ing=True)
                return render(response, "main/ingredient.html", {'non_ors': non_ors, 'selected': 'no selected', 'user': response.user})
            elif response.POST.get('save') == 'no select':
                non_ors = ingredients3.objects.prefetch_related('checked').exclude(or_ing=True).order_by('name')
                return render(response, "main/ingredient.html", {'non_ors': non_ors, 'selected': 'show selected', 'user': response.user})
        else:
            # ingredients = ingredients3.objects.all()
            # for ingredient in ingredients:
                # if ingredient.or_ingredient.exists():
                    # ingredient.or_ing = True
                    # ingredient.save()
            ingredients = ingredients3.objects.prefetch_related('checked').exclude(or_ing=True).order_by('name')
            
            return render(response, "main/ingredient.html", {'non_ors': ingredients, 'selected': 'show selected', 'user': response.user})
    else:
        return render(response, "main/ingredient.html")

def myrecipes(response):
    
    if response.user.is_authenticated:
        orderby = meal_type = veggie = vegan = gluten_free = 'none'
        if response.method == 'POST':
            print(response.POST)
            posts = response.user.recipes.select_related('recipe').exclude(percent=0).order_by('-percent')
            if response.POST.get('save'):
                genres = genres3.objects.all()
                if response.POST.__contains__('meal_type'):
                    meal0 = response.POST.get('meal_type')
                    if meal0 =='lunch':
                        breakfast = genres.get(name='breakfast')
                        dessert = genres.get(name='dessert')
                        posts = posts.exclude(recipe__genre=breakfast).exclude(recipe__genre=dessert)
                        meal_type = 'lunch'
                    else:
                        # meal = genres3.objects.get(name=meal0)
                        meal = genres.get(name=meal0)
                        posts = posts.filter(recipe__genre=meal.id)
                        meal_type = meal0

                if response.POST.__contains__('restrict'):
                    restricts = response.POST.getlist('restrict')
                    for restrict in restricts:
                        if restrict == 'gluten':
                            restrict = 'gluten free'
                            gluten_free = restrict
                            print('GLUTEN')
                        if restrict == 'vegeterian':
                            veggie = restrict
                            print('VEGGIE')
                            print(veggie)
                        if restrict == 'vegan':
                            vegan = restrict
                            print(vegan)
                        restricter = genres.get(name=restrict)
                        posts = posts.filter(recipe__genre=restricter)

                if response.POST.__contains__('orderby'):
                    order = response.POST.get('orderby')
                    orderby = order
                    if order == 'calories':
                        posts = posts.exclude(recipe__calories=0).order_by('recipe__calories')
                    else:
                        posts = posts.exclude(recipe__time=0).order_by('recipe__time')
                else:
                    posts = posts.order_by('recipe__name')


            paginator = Paginator(posts, 25)
            page = response.GET.get('page')
            posts = paginator.get_page(page)

            return render(response, "main/selected_recipes.html", {'posts':posts, 'user': response.user, 'orderby': orderby, 'meal_type': meal_type, 'veggie':veggie, 'vegan':vegan, 'gluten_free': gluten_free})

        else:
        # user_recipe0 = user_recipes.objects.filter(percent > 0)
            posts = response.user.recipes.select_related('recipe').exclude(percent=0).order_by('-percent')
            paginator = Paginator(posts, 25)
            page = response.GET.get('page')
            posts = paginator.get_page(page)

            return render(response, 'main/selected_recipes.html', {'posts':posts, 'user': response.user, 'orderby': orderby, 'meal_type': meal_type, 'veggie':veggie, 'vegan':vegan, 'gluten_free': gluten_free})
    else:
        return render(response, 'main/selected_recipes.html')

def liked_recipes(response):
    if response.user.is_authenticated:
        recipes = response.user.liked.all()
        print(recipes)
        return render(response, 'main/liked.html', {'recipes': recipes, 'user': response.user})
    else:
        return render(response, 'main/liked.html')

def groceryList(response):
    # grocery_list.objects.all().delete()
    if response.user.is_authenticated:
        return render(response, 'main/grocery_list.html', {'ingredients': grocery_list.objects.filter(user=response.user).order_by('name__name'), 'recipes': response.user.checked.all()})
    else:
        return render(response, 'main/grocery_list.html')