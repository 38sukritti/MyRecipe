from django.shortcuts import render, redirect, get_object_or_404
from .forms import SignupForm, RecipeForm
from .models import Recipe, User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_http_methods
def is_admin(user):
    return user.is_staff

def home(request):
    categories = [
        ('Breakfast', 'breakfast.jpg', 'breakfast'),
        ('Lunch', 'lunch.webp', 'lunch'),
        ('Dinner', 'dinner.jpg', 'dinner'),
        ('Soups', 'soups.jpg', None),
        ('Desserts', 'desserts.jpg', None)
    ]
    cuisines = [
        ('American', 'american.jpg'),
        ('Italian', 'italian.jpg'),
        ('Asian', 'asian.jpg'),
        ('Mexican', 'mexican.jpg'),
        ('Southern & Soul Food', 'south indian.jpg'),
        ('Korean', 'korean.jpg')
    ]
    return render(request, 'index.html', {
        'categories': categories,
        'cuisines': cuisines
    })
def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        is_admin = request.POST.get('is_admin') == 'on'

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('app1:signup')

        user = User.objects.create_user(username=username, email=email, password=password)
        if is_admin:
            user.is_staff = True
            user.is_superuser = True
        user.save()

        messages.success(request, "Account created successfully!")
        return redirect('app1:login')

    return render(request, 'signup.html')

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
                return redirect('app1:home')
        except User.DoesNotExist:
            pass
        messages.error(request, "Invalid email or password")
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out")
    return redirect('app1:home')

@login_required
@user_passes_test(is_admin)
def myrecipe(request):
    recipes = Recipe.objects.all()
    return render(request, 'myrecipe.html', {'recipes': recipes, 'username': request.user.username})

@login_required
@user_passes_test(is_admin)
def add_recipe(request):
    if request.method == 'POST':
        form = RecipeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('app1:myrecipe')
    else:
        form = RecipeForm()
    return render(request, 'add_recipe.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def edit_recipe(request, id):
    recipe = get_object_or_404(Recipe, id=id)
    if request.method == 'POST':
        form = RecipeForm(request.POST, instance=recipe)
        if form.is_valid():
            form.save()
            return redirect('app1:myrecipe')
    else:
        form = RecipeForm(instance=recipe)
    return render(request, 'edit_recipe.html', {'form': form, 'recipe': recipe})

@login_required
@user_passes_test(is_admin)
def delete_recipe(request, id):
    recipe = get_object_or_404(Recipe, id=id)
    recipe.delete()
    return redirect('app1:myrecipe')

def dinner(request):
    return render(request, 'dinner.html', {'username': request.user.username if request.user.is_authenticated else None})

def breakfast(request):
    return render(request, 'breakfast.html', {'username': request.user.username if request.user.is_authenticated else None})

def lunch(request):
    return render(request, 'lunch.html', {'username': request.user.username if request.user.is_authenticated else None})

def aboutus(request):
    return render(request, 'About.html', {'username': request.user.username if request.user.is_authenticated else None})

def recipe(request):
    recipes = [
        {
            'title': 'Pasta Alfredo',
            'description': 'Creamy and delicious Alfredo Pasta.',
            'ingredients': '250g fettuccine, 2 tbsp butter, 1 cup cream, 1 cup Parmesan...',
            'instructions': 'Cook pasta & drain. Melt butter, sauté garlic, add cream...',
            'image': 'images/pasta.jpg',
            'video_url': 'https://youtu.be/XsipAaImDVc?si=U23TDhfWlvgB6i6X'
        },
        {
            'title': 'Chocolate Cake',
            'description': 'Rich and moist chocolate cake.',
            'ingredients': '1½ cups flour, 1 cup sugar, ½ cup cocoa...',
            'instructions': 'Preheat oven to 180°C. Mix dry & wet ingredients...',
            'image': 'images/chocolate cake.jpg',
            'video_url': 'https://youtu.be/EaljSnLrJW8?si=BbtkQsKkhIEHP8y1'
        },
        # Add more recipes similarly...
    ]
    
    return render(request, 'recipe.html', {'username': request.user.username if request.user.is_authenticated else None,'recipes': recipes})

def reset(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('reset')

        email = request.session.get('reset_email')
        if not email:
            messages.error(request, "Session expired or invalid access.")
            return redirect('app1:forgot')

        try:
            user = User.objects.get(email=email)
            user.set_password(password)
            user.save()
            messages.success(request, "Your password has been reset successfully.")
            return redirect('app1:login')
        except User.DoesNotExist:
            messages.error(request, "User not found.")
            return redirect('forgot')

    return render(request, 'reset_password.html')

@require_http_methods(["GET", "POST"])
def forgot(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            request.session['reset_email'] = email  # Store email in session
            return redirect('app1:reset')
        except User.DoesNotExist:
            messages.error(request, "Email not found.")
            return redirect('app1:forgot')

    return render(request, 'forgotPassword.html')

# def forgot_password(request):
#     if request.method == "POST":
#         email = request.POST.get('email')
#         try:
#             user = User.objects.get(email=email)
#             request.session['reset_email'] = email
#             return redirect('reset_password')  # name of the URL pattern for reset_password view
#         except User.DoesNotExist:
#             messages.error(request, "Email not found")
#             return redirect('forgot_password')

#     return render(request, "forgotPassword.html")