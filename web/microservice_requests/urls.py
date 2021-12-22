from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'microservice_requests'

router = DefaultRouter()

urlpatterns = [
    path('register-user/blog', views.ChatRegisterView.as_view(), name="blog"),
    path('categories/blog/', views.CategoriesListView.as_view(), name="categories"),
    path('categories/blog/<slug>/', views.CategoryChangeView.as_view(), name="categories-slug"),
]

urlpatterns += router.urls
