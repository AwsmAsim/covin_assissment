from django.shortcuts import render

def home_page(request):
    return render(request, 'templates/index.html', {'fact': 'Yo !'});

def events_page(request):
    return render(request, 'templates/events_page.html', {'fact': 'Yo !'});
