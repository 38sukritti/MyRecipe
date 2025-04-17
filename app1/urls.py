from django.urls import path
from . import views
# from django.contrib import admin
app_name = 'app1'

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_page, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('myrecipe/', views.myrecipe, name='myrecipe'),
    path('add/', views.add_recipe, name='add_recipe'),
    path('edit/<int:id>/', views.edit_recipe, name='edit_recipe'),
    path('delete/<int:id>/', views.delete_recipe, name='delete_recipe'),
    path('dinner/', views.dinner, name='dinner'),
    path('breakfast/', views.breakfast, name='breakfast'),
    path('lunch/', views.lunch, name='lunch'),
    path('aboutus/', views.aboutus, name='aboutus'),
    path('recipe/', views.recipe, name='recipe'),
    path('reset/',views.reset,name='reset'),
    path('forgot/',views.forgot,name='forgot')
]

