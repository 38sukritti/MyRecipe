# from .forms import SignupForm, RecipeForm
from .models import  User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_http_methods
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Recipe, Testimonial
from .forms import RecipeForm, TestimonialForm
from django.utils import timezone
from datetime import timedelta
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied

def is_admin(user):
    return user.is_authenticated and (user.is_superuser or user.is_staff)

# Add these new views for recipes
@user_passes_test(is_admin)
def recipe_list(request):
    recipes = Recipe.objects.all()
    return render(request, 'recipe_list.html', {'recipes': recipes})

@user_passes_test(lambda u: u.is_staff)
def recipe_create(request):
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES)
        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.created_by = request.user
            recipe.is_approved = True  # Auto-approve admin-added recipes
            recipe.save()
            return redirect('app2:recipe_list')  # Or redirect to home if preferred
    else:
        form = RecipeForm()
    return render(request, 'recipe_form.html', {'form': form})

@user_passes_test(is_admin)
def recipe_update(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES, instance=recipe)
        if form.is_valid():
            form.save()
            return redirect('app2:recipe_list')
    else:
        form = RecipeForm(instance=recipe)
    return render(request, 'recipe_form.html', {'form': form})

@user_passes_test(is_admin)
def recipe_delete(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    if request.method == 'POST':
        recipe.delete()
        return redirect('app2:recipe_list')
    return render(request, 'recipe_confirm_delete.html', {'recipe': recipe})


def popular_recipes(request):
    # Get ALL approved recipes, ordered by newest first
    recipes = Recipe.objects.filter(is_approved=True).order_by('-created_at')[:6]  # Show 6 newest
    
    # Alternative: Mix of top-rated and new recipes
    # top_rated = Recipe.objects.filter(is_approved=True).order_by('-rating')[:3]
    # new_recipes = Recipe.objects.filter(is_approved=True).order_by('-created_at')[:3]
    # recipes = list(top_rated) + list(new_recipes)
    
    return render(request, 'home3.html', {
        'recipes': recipes,
        'now': timezone.now()  # Pass current time for "NEW" badge comparison
    })

def get_testimonial(request, pk):
    testimonial = get_object_or_404(Testimonial, pk=pk, user=request.user)
    data = {
        'user_title': testimonial.user_title,
        'content': testimonial.content,
        'rating': testimonial.rating
    }
    return JsonResponse(data)

def testimonials(request):
    # Show all testimonials from all users, ordered by newest first
    testimonials_list = Testimonial.objects.all().order_by('-created_at')
    
    if request.method == 'POST' and request.user.is_authenticated:
        form = TestimonialForm(request.POST)
        if form.is_valid():
            testimonial = form.save(commit=False)
            testimonial.user = request.user
            testimonial.save()
            return redirect('app2:testimonials')
    else:
        form = TestimonialForm()
    
    return render(request, 'home3.html', {
        'testimonials': testimonials_list,
        'form': form
    })
@login_required
def add_testimonial(request):
    if request.method == 'POST':
        form = TestimonialForm(request.POST)
        if form.is_valid():
            testimonial = form.save(commit=False)
            testimonial.user = request.user
            testimonial.save()
            return redirect('app2:testimonials')
    return redirect('app2:testimonials')

@login_required
def edit_testimonial(request, pk):
    testimonial = get_object_or_404(Testimonial, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = TestimonialForm(request.POST, instance=testimonial)
        if form.is_valid():
            form.save()
            return redirect('app2:home')
    else:
        form = TestimonialForm(instance=testimonial)
    
    # Render the same template but with the edit form
    testimonials_list = Testimonial.objects.all().order_by('-created_at')
    recipes = Recipe.objects.filter(is_approved=True).order_by('-created_at')[:6]
    return render(request, 'home3.html', {
        'testimonials': testimonials_list,
        'form': form,
        'editing_testimonial': testimonial,
        'recipes': recipes,
        'now': timezone.now()
    })

@login_required
def delete_testimonial(request, pk):
    testimonial = get_object_or_404(Testimonial, pk=pk)
    
    # Check if user is either the testimonial owner or a superuser
    if not (request.user == testimonial.user or request.user.is_superuser):
        raise PermissionDenied("You don't have permission to delete this testimonial")
    
    if request.method == 'POST':
        testimonial.delete()
        return redirect('app2:home')
    
    # Optional: Handle GET requests if needed (perhaps show confirmation page)
    return redirect('app2:home')

@login_required
def handle_testimonial(request):
    if request.method == 'POST':
        testimonial_id = request.POST.get('testimonial_id')
        if testimonial_id:  # Editing existing testimonial
            testimonial = get_object_or_404(Testimonial, pk=testimonial_id)
            # Only allow owner to edit
            if request.user != testimonial.user:
                raise PermissionDenied
            form = TestimonialForm(request.POST, instance=testimonial)
        else:  # Creating new testimonial
            form = TestimonialForm(request.POST)
        
        if form.is_valid():
            testimonial = form.save(commit=False)
            if not testimonial_id:  # New testimonial
                testimonial.user = request.user
            testimonial.save()
            return redirect('app2:home')
    else:
        # Handle GET requests
        pass
def home(request):
    # Show all testimonials from all users, ordered by newest first
    testimonials_list = Testimonial.objects.all().order_by('-created_at')
    recipes = Recipe.objects.filter(is_approved=True).order_by('-created_at')[:6]
    
    if request.method == 'POST' and request.user.is_authenticated:
        testimonial_id = request.POST.get('testimonial_id')
        
        if testimonial_id:  # Editing existing testimonial
            testimonial = get_object_or_404(Testimonial, pk=testimonial_id, user=request.user)
            form = TestimonialForm(request.POST, instance=testimonial)
            if form.is_valid():
                form.save()  # This updates the existing testimonial
                messages.success(request, "Testimonial updated successfully!")
                return redirect('app2:home')
        else:  # Creating new testimonial
            form = TestimonialForm(request.POST)
            if form.is_valid():
                testimonial = form.save(commit=False)
                testimonial.user = request.user
                testimonial.save()
                messages.success(request, "Testimonial added successfully!")
                return redirect('app2:home')
    else:
        form = TestimonialForm()
    
    return render(request, 'home3.html', {
        'testimonials': testimonials_list,
        'form': form,
        'recipes': recipes,
        'now': timezone.now()
    })
# Create your views here.
def about(request):
    return render(request,"aboutus.html")
def cheesecake(request):
    return render(request,"cheesecake.html")
def party(request):
    return render(request,'party.html')
def maggie(request):
    return render(request,'maggie.html')
def pizza(request):
    return render(request,'pizza.html')
def recipes(request):
    return render(request,'index2.html')
def contact(request):
    return render(request,'contactus.html')
def diet(request):
    return render(request,"diet.html")
def mushroom(request):
    return render(request,'mushroom.html')
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out")
    return redirect('app2:home')
def login_page(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        try:
            user = User.objects.get(email=email)
            user = authenticate(request, username=user.username, password=password)
            if user:
                login(request, user)
                messages.success(request, f"Welcome, {user.username}!")
                return redirect('app2:home')
        except User.DoesNotExist:
            pass
        messages.error(request, "Invalid email or password")
    return render(request, 'login.html')
def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        is_admin = request.POST.get('is_admin') == 'on'

        # Only superusers can create admin accounts
        if is_admin and not request.user.is_superuser:
            messages.error(request, "Only administrators can create admin accounts.")
            return redirect('app2:signup')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('app2:signup')

        user = User.objects.create_user(username=username, email=email, password=password)
        if is_admin and request.user.is_superuser:
            user.is_staff = True
            user.is_superuser = True
        user.save()

        messages.success(request, "Account created successfully!")
        return redirect('app2:login')

    return render(request, 'signup.html')
def category(request):
    return render(request,"categories.html")
@user_passes_test(lambda u: u.is_superuser)
def manage_users(request):
    users = User.objects.all().order_by('-date_joined')
    
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        action = request.POST.get('action')
        
        try:
            user = User.objects.get(id=user_id)
            if action == 'make_admin':
                user.is_staff = True
                user.save()
                messages.success(request, f"{user.username} is now an admin")
            elif action == 'remove_admin':
                user.is_staff = False
                user.is_superuser = False
                user.save()
                messages.success(request, f"Admin privileges removed from {user.username}")
            elif action == 'delete':
                if user != request.user:  # Prevent self-deletion
                    user.delete()
                    messages.success(request, f"User {user.username} deleted")
                else:
                    messages.error(request, "You cannot delete your own account")
        except User.DoesNotExist:
            messages.error(request, "User not found")
        
        return redirect('app2:manage_users')
    
    return render(request, 'manage_users.html', {'users': users})