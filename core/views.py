from django.http import JsonResponse
from django.contrib.auth import get_user_model

def force_create_admin(request):
    User = get_user_model()

    if User.objects.filter(username="admin").exists():
        return JsonResponse({"status": "admin already exists"})

    user = User.objects.create_superuser(
        username="admin",
        email="admin@example.com",
        password="Admin123!",
    )

    return JsonResponse({
        "status": "admin created",
        "username": user.username
    })
