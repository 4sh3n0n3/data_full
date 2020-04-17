from django.urls import path

from . import views

urlpatterns = [
    path('researches/', views.ResearchGroupsList.as_view(), name='research-list'),
    path('researches/<int:pk>/', views.ResearchDetailView.as_view(), name='research-detail'),
    path('dataset/add/', views.CreateDatasetView.as_view(), name='create_dataset'),
    path('research/add/', views.CreateResearchView.as_view(), name='create_research'),
    path('dataset/upload/<int:pk>', views.UploadDataToDatasetView.as_view(), name='upload_data_to_dataset'),
    path('dataset/set_header_types/<int:pk>', views.SetHeaderTypesView.as_view(),
         name='set_dataset_headers_types'),
]
