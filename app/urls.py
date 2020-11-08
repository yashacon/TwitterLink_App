from django.urls import path,include
from . import views
urlpatterns = [
    path('',views.homelogin,name='Homelogin'),
    path('login',views.login,name='Login'),
    path('logout',views.logout,name='Logout'),
    path('callback/', views.callback, name='callback'), 
    path('home',views.home,name='Home'),
    path('all_t',views.all_twt,name='All_Tweets'),
    path('link_t',views.link_twt,name='Link_Tweets'),
    path('top_user',views.top_user,name='Top_User'),
    path('top_domain',views.top_domain,name='Top_Domain'),
]
