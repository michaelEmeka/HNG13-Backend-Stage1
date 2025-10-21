from django.contrib import admin
from django.urls import path, include
import analyzer.urls as analyzer_urls

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include(analyzer_urls))
    ]
