from django.urls import path

from . import views

urlpatterns = [
    path('researches/', views.ResearchListView.as_view(), name='dataset-list'),
    path('researches/<int:pk>/', views.DatasetListView.as_view(), name='research-datasets'),
    # path('dataset/<int:pk>/', views.DatasetDetailView.as_view(), name='dataset-details'),
    path('dataset/calculate/<int:pk>', views.AnalyseData.as_view(), name='calculate-data'),
]