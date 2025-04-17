from django.urls import path
from app2 import views
app_name = 'app2'

urlpatterns=[
    path('',views.home,name='home' ),
    path('cheesecake/',views.cheesecake,name='cheesecake'),
    path('party/',views.party,name='party'),
    path('maggie/',views.maggie,name='maggie'),
    path('pizza/',views.pizza,name='pizza'),
    path('recipes/',views.recipes,name='recipes'),
    path('logout/',views.logout_view,name='logout'),
    path('contact/',views.contact,name='contact' ),
    path('diet/',views.diet,name='diet'),
    path('mushroom/',views.mushroom,name='mushroom'),
   path('testimonials/', views.testimonials, name='testimonials'),
    path('testimonials/add/', views.add_testimonial, name='add_testimonial'),
    path('testimonials/edit/<int:pk>/', views.edit_testimonial, name='edit_testimonial'),
    path('testimonials/delete/<int:pk>/', views.delete_testimonial, name='delete_testimonial'),
    path('popular/', views.popular_recipes, name='popular_recipes'),
    path('recipes/popular/', views.popular_recipes, name='popular_recipes'),
    path('admin/recipes/', views.recipe_list, name='recipe_list'),
    path('admin/recipes/add/', views.recipe_create, name='recipe_create'),
    path('admin/recipes/edit/<int:pk>/', views.recipe_update, name='recipe_update'),
    path('admin/recipes/delete/<int:pk>/', views.recipe_delete, name='recipe_delete'),
    path('get-testimonial/<int:pk>/', views.get_testimonial, name='get_testimonial'),
    path('about/',views.about,name='about'),
    path('category/',views.category,name='category'),
    path('manage-users/', views.manage_users, name='manage_users'),
]