from django.shortcuts import render


def login_view(request):
    return render(request, "admin_panel/login.html")


def dashboard_view(request):
    return render(request, "admin_panel/admin.html")