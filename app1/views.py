from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
import requests
import json
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
# Get the custom User model
User = get_user_model()
# API Configuration
API_BASE_URL = 'http://127.0.0.1:5000/api'  # Update with your Flask server URL
SESSION_COOKIE_NAME = 'session'  # Should match Flask's session cookie name

def is_admin(user):
    return user.is_staff

class APIClient:
    def __init__(self, request=None):
        self.request = request
        self.session = requests.Session()
        
        if request:
            # Forward ALL cookies (not just session)
            for name, value in request.COOKIES.items():
                self.session.cookies.set(
                    name, 
                    value,
                    domain='127.0.0.1',  # Must match Flask
                    path='/'
                )
    def get_json(self, method, endpoint, data=None):
        response = self.make_request(method, endpoint, data)
        if response and response.status_code == 200:
            try:
                return response.json()
            except ValueError:
                return None
        return None
    def make_request(self, method, endpoint, data=None):
        headers = {'Content-Type': 'application/json'}
        url = f"{API_BASE_URL}{endpoint}"
        
        try:
            print(f"Making {method} request to {url}")  # Debug
            print(f"Cookies being sent: {self.session.cookies.get_dict()}")  # Debug
            
            if method == 'GET':
                response = self.session.get(url, headers=headers, params=data)
            elif method == 'POST':
                response = self.session.post(url, headers=headers, json=data)
            elif method == 'PUT':
                response = self.session.put(url, headers=headers, json=data)
            elif method == 'DELETE':
                response = self.session.delete(url, headers=headers)
            else:
                raise ValueError("Invalid HTTP method")
            
            print(f"Response status: {response.status_code}")  # Debug
            print(f"Response cookies: {response.cookies.get_dict()}")  # Debug
            print(f"Response content: {response.text}")  # Debug
            
            response.raise_for_status()
            return response
        
        except requests.exceptions.RequestException as e:
            print(f"API Error: {e}")
            if hasattr(e, 'response') and e.response:
                print(f"Error response: {e.response.text}")
            return None
        
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

@require_http_methods(["GET", "POST"])
def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        is_admin = request.POST.get('is_admin') == 'on'

        # Check if username or email exists locally first
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return render(request, 'signup.html')
            
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return render(request, 'signup.html')

        # Create user via API
        client = APIClient()
        response = client.make_request(
            'POST',
            '/signup',
            {
                'username': username,
                'email': email,
                'password': password,
                'is_admin': is_admin
            }
        )

        if response and response.status_code == 201:
            # Create local Django user (without password for security)
            User.objects.create_user(
                username=username,
                email=email,
                is_staff=is_admin
            )
            messages.success(request, "Account created successfully! Please log in.")
            return redirect('app1:login')
        
        error_msg = "Failed to create account. Please try again."
        if response and response.status_code == 409:
            error_msg = "User already exists with this username or email."
        messages.error(request, error_msg)
    
    return render(request, 'signup.html')

@require_http_methods(["GET", "POST"])
def login_page(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        
        # Authenticate via API
        client = APIClient()
        response = client.make_request(
            'POST',
            '/login',
            {'email': email, 'password': password}
        )
        
        if response and response.status_code == 200:
            data = response.json()
            user_data = data['user']
            
            # Get or create local user
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'is_staff': user_data['is_admin']
                }
            )
            
            # Authenticate locally (without password check)
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
            
            # Set session cookie from API response
            django_response = redirect('app1:home')
            if SESSION_COOKIE_NAME in response.cookies:
                django_response.set_cookie(
                    SESSION_COOKIE_NAME,
                    response.cookies[SESSION_COOKIE_NAME],
                    domain='localhost'
                )
            
            messages.success(request, f"Welcome, {user.username}!")
            return django_response
        
        messages.error(request, "Invalid email or password")
    
    return render(request, 'login.html')

def logout_view(request):
    # Logout from API
    client = APIClient(request)
    response = client.make_request('POST', '/logout')
    
    # Logout locally
    logout(request)
    
    # Clear session cookie
    django_response = redirect('app1:home')
    django_response.delete_cookie(SESSION_COOKIE_NAME)
    
    messages.info(request, "You have been logged out")
    return django_response

# ... (keep all your existing imports and configurations)

@login_required
@user_passes_test(is_admin)
def myrecipe(request):
    client = APIClient(request)
    response = client.get_json('GET', '/recipes')
    
    if response is None:
        messages.error(request, "Failed to fetch recipes from server")
        recipes = []
    else:
        recipes = response.get('recipes', [])
    
    return render(request, 'myrecipe.html', {
        'recipes': recipes,
        'username': request.user.username
    })

@login_required
@user_passes_test(is_admin)
def add_recipe(request):
    if request.method == 'POST':
        print("Raw POST data:", request.POST)  # Debug
        
        title = request.POST.get('title')
        ingredients = request.POST.get('ingredients')
        instructions = request.POST.get('instructions')
        
        if not all([title, ingredients, instructions]):
            messages.error(request, "All fields are required")
            return render(request, 'add_recipe.html')
        
        ingredients_list = [ing.strip() for ing in ingredients.split('\n') if ing.strip()]
        
        data = {
            'title': title,
            'ingredients': ingredients_list,
            'instructions': instructions,
            'user_id': request.user.username
        }
        
        print("Sending to API:", data)  # Debug
        
        client = APIClient(request)
        response = client.make_request('POST', '/recipes', data)
        
        if response:
            print("API Response:", response.status_code, response.text)  # Debug
            if response.status_code == 201:
                messages.success(request, "Recipe added successfully!")
                return redirect('app1:myrecipe')
        
        messages.error(request, f"Failed to add recipe. Status: {response.status_code if response else 'No response'}")
        return render(request, 'add_recipe.html')
    
    return render(request, 'add_recipe.html')
@login_required
def debug_session(request):
    """Debug view to check session status"""
    client = APIClient(request)
    response = client.make_request('GET', '/debug/session')
    
    if response:
        return HttpResponse(f"""
            <h1>Session Debug</h1>
            <h2>Django Session</h2>
            <pre>{dict(request.session)}</pre>
            <h2>Flask Session</h2>
            <pre>{response.text}</pre>
            <h2>Cookies Sent</h2>
            <pre>{client.session.cookies.get_dict()}</pre>
        """)
    return HttpResponse("Failed to connect to Flask API")

@login_required
@user_passes_test(is_admin)
def edit_recipe(request, id):
    client = APIClient(request)
    
    # Get current recipe details
    response = client.get_json('GET', f'/recipes/{id}')
    if not response:
        messages.error(request, "Recipe not found")
        return redirect('app1:myrecipe')
    
    if request.method == 'POST':
        # Validate form data
        title = request.POST.get('title')
        ingredients = request.POST.get('ingredients')
        instructions = request.POST.get('instructions')
        
        if not all([title, ingredients, instructions]):
            messages.error(request, "All fields are required")
            return render(request, 'edit_recipe.html', {'recipe': response})
        
        # Update via Flask API
        update_response = client.make_request(
            'PUT',
            f'/recipes/{id}',
            {
                'title': title,
                'ingredients': ingredients,
                'instructions': instructions,
                'user_id': request.user.id  # If your API needs user association
            }
        )
        
        if update_response and update_response.status_code == 200:
            messages.success(request, "Recipe updated successfully!")
            return redirect('app1:myrecipe')
        else:
            error_msg = "Failed to update recipe"
            if update_response:
                try:
                    error_data = update_response.json()
                    error_msg = f"{error_msg}: {error_data.get('error', 'Unknown error')}"
                    if update_response.status_code == 401:
                        error_msg += " (Not authenticated)"
                    elif update_response.status_code == 403:
                        error_msg += " (Permission denied)"
                except ValueError:
                    error_msg += f" (Status: {update_response.status_code})"
            messages.error(request, error_msg)
            return render(request, 'edit_recipe.html', {
                'recipe': response,
                'username': request.user.username
            })
    
    return render(request, 'edit_recipe.html', {
        'recipe': response,
        'username': request.user.username
    })

@login_required
@user_passes_test(is_admin)
def delete_recipe(request, id):
    client = APIClient(request)
    response = client.make_request('DELETE', f'/recipes/{id}')
    
    if response and response.status_code == 200:
        messages.success(request, "Recipe deleted successfully!")
    else:
        error_msg = "Failed to delete recipe"
        if response:
            try:
                api_error = response.json().get('error', '')
                if api_error:
                    error_msg = f"{error_msg}: {api_error}"
            except ValueError:
                pass
        messages.error(request, error_msg)
    
    return redirect('app1:myrecipe')

def dinner(request):
    return render(request, 'dinner.html', {
        'username': request.user.username if request.user.is_authenticated else None
    })

def breakfast(request):
    return render(request, 'breakfast.html', {
        'username': request.user.username if request.user.is_authenticated else None
    })

def lunch(request):
    return render(request, 'lunch.html', {
        'username': request.user.username if request.user.is_authenticated else None
    })

def aboutus(request):
    return render(request, 'About.html', {
        'username': request.user.username if request.user.is_authenticated else None
    })

def recipe(request):
    # Example static data - you could fetch from API if needed
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
            'video_url': 'https://youtu.be/EaljSnLJW8?si=BbtkQsKkhIEHP8y1'
        },
    ]
    
    return render(request, 'recipe.html', {
        'username': request.user.username if request.user.is_authenticated else None,
        'recipes': recipes
    })

@require_http_methods(["GET", "POST"])
def reset(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'reset_password.html')

        email = request.session.get('reset_email')
        if not email:
            messages.error(request, "Session expired or invalid access.")
            return redirect('app1:forgot')

        # Reset password via API
        client = APIClient()
        response = client.make_request(
            'POST',
            '/reset-password',
            {
                'email': email,
                'password': password
            }
        )
        
        if response and response.status_code == 200:
            messages.success(request, "Your password has been reset successfully!")
            return redirect('app1:login')
        
        messages.error(request, "Failed to reset password.")
        return redirect('app1:forgot')

    return render(request, 'reset_password.html')

@require_http_methods(["GET", "POST"])
def forgot(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        
        # Send forgot password request to API
        client = APIClient()
        response = client.make_request(
            'POST',
            '/forgot-password',
            {'email': email}
        )
        
        if response and response.status_code == 200:
            request.session['reset_email'] = email
            return redirect('app1:reset')
        
        messages.error(request, "Email not found.")
    
    return render(request, 'forgotPassword.html')

# API Views (optional - if you want to expose some endpoints through Django)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_user_profile(request):
    client = APIClient(request)
    response = client.get_json('GET', '/users')
    
    if not response:
        return Response(
            {'error': 'Failed to fetch user data from API'},
            status=status.HTTP_502_BAD_GATEWAY
        )
    
    return Response(response)