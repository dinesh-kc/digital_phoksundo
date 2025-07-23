# darta_chalani/urls.py
from django.urls import path
from . import views

app_name = 'darta_chalani' # Namespace for your app's URLs

urlpatterns = [
    # Darta (Incoming Documents) URLs
    path('darta/', views.darta_list, name='darta_list'),
    path('darta/add/', views.darta_add, name='darta_add'),
    path('darta/<int:pk>/', views.darta_detail, name='darta_detail'),
    path('darta/<int:pk>/edit/', views.darta_edit, name='darta_edit'),
    path('darta/<int:pk>/delete/', views.darta_delete, name='darta_delete'),

    # Chalani (Outgoing Documents) URLs
    path('chalani/', views.chalani_list, name='chalani_list'),
    path('chalani/add/', views.chalani_add, name='chalani_add'),
    path('chalani/<int:pk>/', views.chalani_detail, name='chalani_detail'),
    path('chalani/<int:pk>/edit/', views.chalani_edit, name='chalani_edit'),
    path('chalani/<int:pk>/delete/', views.chalani_delete, name='chalani_delete'),

    # Attachment URLs (e.g., for direct download, if needed, or handled via document detail)
    # path('attachment/<int:pk>/download/', views.attachment_download, name='attachment_download'),
]