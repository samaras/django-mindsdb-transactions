from django.urls import path
from . import views

app_name = 'finance'

urlpatterns = [
    path('', views.index, name='index'),
    path('mindsdb/', views.mindsdb_dashboard, name='mindsdb_dashboard'),
    path('api/clients/', views.api_clients, name='api_clients'),
    path('api/cards/', views.api_cards, name='api_cards'),
    path('api/transactions/', views.api_transactions, name='api_transactions'),
    path('api/mindsdb/wealthy-clients/', views.api_mindsdb_wealthy_clients, name='api_mindsdb_wealthy_clients'),
    path('api/mindsdb/travel-expenses/', views.api_mindsdb_travel_expenses, name='api_mindsdb_travel_expenses'),
    path('api/mindsdb/online-shopping/', views.api_mindsdb_online_shopping, name='api_mindsdb_online_shopping'),
    path('api/mindsdb/suspicious-transactions/', views.api_mindsdb_suspicious_transactions, name='api_mindsdb_suspicious_transactions'),
    path('api/mindsdb/unusual-spending/', views.api_mindsdb_unusual_spending, name='api_mindsdb_unusual_spending'),
    path('api/mindsdb/custom-search/', views.api_mindsdb_custom_search, name='api_mindsdb_custom_search'),
    path('api/mindsdb/stats/', views.api_mindsdb_stats, name='api_mindsdb_stats'),
    path('api/mindsdb/execute-query/', views.api_mindsdb_execute_query, name='api_mindsdb_execute_query'),
] 