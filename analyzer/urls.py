from django.contrib import admin
from django.urls import path
from . import views
urlpatterns = [
    path("strings", views.CreateStringAnalysisView().as_view()),
    path(
        "strings/filter-by-natural-language", views.NaturalLanguageFilterView.as_view()
    ),
    path("strings/<str:value>", views.Get_DeleteStringAnalysis().as_view()),
]
