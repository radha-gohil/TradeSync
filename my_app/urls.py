from django.contrib import admin
from django.urls import path,include
from my_app import views
from .views import marketnews,user_logout
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("1",views.logo_page,name="logo"),
    path("signup",views.signup,name='signup'),
    path("",views.dashboard2,name='dashboard2'),
    path("login",views.login,name='login'),
    path("dashboard/",views.dashboard,name="dashboard"),
    path("live-stock-prices", views.live_stock_prices, name="live_stock_prices"),
    path("logout",views.logout,name="logout"),
    path("searchstock",views.searchstock,name="searchstock"),
    path("stockprediction",views.stockprediction,name="stockprediction"),
    path("get_stock_datas/", views.get_stock_datas, name="get_stock_datas"),
    path("predict_stock/", views.predict_stock, name="predict_stock"),
    path("trading_bot",views.trading_bot,name="trading_bot"),
    path('marketnews',views.marketnews,name="marketnews"),
    path('top_movers',views.top_movers,name="top_movers"),
    path("market-news/", views.market_news_view, name="market_news"),
    path("dashboard_slider",views.dashboard_slider,name="dashboard_slider"),
    path("signup", views.psignup, name="psignup"),
    path("k", views.plogin, name="plogin"),
    path("plogout", user_logout, name="plogout"),
    path("pdashboard", views.pdashboard, name="pdashboard"),
    path("portfolio", views.portfolio, name="portfolio"),
    path("add_stock", views.add_stock, name="add_stock"),
    path("delete_stock/<int:stock_id>/",views.delete_stock,name="delete_stock"),
    path("buy_sell",views.buy_sell,name="buy_sell"),
    path("buy_stock",views.buy_stock,name="buy_stock"),
    path("sell_stock",views.sell_stock,name="sell_stock"),
    path('get_stock_chart_data/', views.get_stock_chart_data, name='get_stock_chart_data'),
    path("transactions_history",views.transactions_history,name="transactions_history"),
    path("setting",views.setting,name="setting"),
    path("delete_account",views.delete_account,name="delete_account"),
    path("porfolio_history",views.porfolio_history,name="porfolio_history"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

