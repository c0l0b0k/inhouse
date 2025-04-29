from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


from .views import contact_view

urlpatterns = [
    path('', views.index, name='index'),

    path('catalog/<int:category_id>/', views.catalog, name='catalog'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('contact/', contact_view, name='contact_view'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)