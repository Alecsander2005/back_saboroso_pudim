from django.shortcuts import redirect, render


def login_view(request):
    return render(request, "admin_panel/login.html")


def dashboard_view(request):
    if not (
        request.user.is_authenticated
        and request.user.is_active
        and request.user.tipo_usuario == "admin"
    ):
        return redirect("admin-login")

    return render(request, "admin_panel/admin.html")