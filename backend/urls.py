"""backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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

from django.conf.urls.static import static
from django.urls import path, include
from django.contrib import admin
from django.conf import settings

from rest_framework import routers
from movie.views import (
    MovieViewSet,
    ContactViewSet,
    FeedbackViewSet,
    FeedbackSubjectViewSet,
    UserViewSet,
    UserActivityViewSet,
)

router = routers.DefaultRouter()
router.register(r"movies", MovieViewSet)
router.register(r"contact", ContactViewSet)
router.register(r"feedback", FeedbackViewSet)
router.register(r"feedback-subjects", FeedbackSubjectViewSet)
router.register(r"user", UserViewSet)
router.register(r"user-activity", UserActivityViewSet)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
