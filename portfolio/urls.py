from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns

from . import views
from django.urls import path

app_name = 'portfolio'
urlpatterns = [

    path('', views.home, name='home'),
    path('home/', views.home, name='home'),
    path('customer/', views.customer_list, name='customer_list'),
    path('customer/<int:pk>/delete/', views.customer_delete, name='customer_delete'),
    path('customer/<int:pk>/edit/', views.customer_edit, name='customer_edit'),
    path('investment/', views.investment_list, name='investment_list'),
    path('investment/<int:pk>/delete/', views.investment_delete, name='investment_delete'),
    path('investment/<int:pk>/edit/', views.investment_edit, name='investment_edit'),
    path('investment/create/', views.investment_new, name='investment_new'),
    path('stock/', views.stock_list, name='stock_list'),
    path('stock/<int:pk>/delete/', views.stock_delete, name='stock_delete'),
    path('stock/<int:pk>/edit/', views.stock_edit, name='stock_edit'),
    path('stock/create/', views.stock_new, name='stock_new'),
    path('customer/<int:pk>/portfolio/', views.portfolio, name='portfolio'),
    path('customer/<int:pk>/portfolio/pdf/', views.generate_pdf_view, name='generate_pdf_view'),

]
urlpatterns=format_suffix_patterns(urlpatterns)
