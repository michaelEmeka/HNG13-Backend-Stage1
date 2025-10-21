from django.contrib import admin
from django.urls import path
from . import views
urlpatterns = [
    path("strings/", views.CreateStringAnalysisView().as_view()),
    path("strings/<str:value>", views.GetStringAnalysis().as_view()),
]
