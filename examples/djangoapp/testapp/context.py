from django.conf import settings


def context(request):
    return {"ASSETS": settings.BASE_DIR / "../../node_modules/"}
