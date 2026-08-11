"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from calendars import urls as cal_urls
from clubs import urls as clb_urls
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from users.views import RegisterView, EmailTokenObtainPairView
from .views import redirect_frontend
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("", redirect_frontend, name="frontend_redirect"),
    path('api/admin/', admin.site.urls),
    path("api/calendar/", include("calendars.urls")),
    path("api/club/", include("clubs.urls")),
    path("api/register", RegisterView.as_view(), name="register"),
    path("api/token/", EmailTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("api/management/", include("management.urls")),
]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
