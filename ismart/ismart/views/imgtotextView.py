from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from ismart.views.tecessaract import tecessaract


def HomeRoute(request):
    value = tecessaract.teserract(r"https://cdn.shopify.com/s/files/1/0070/7032/files/Fearless_Motivational_Quote_Desktop_Wallpaper_1.png?format=jpg&quality=90&v=1600450412")
    print(value)
    return JsonResponse({'text': value})