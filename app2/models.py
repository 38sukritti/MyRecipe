from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Testimonial(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    user_title = models.CharField(max_length=100)
    content = models.TextField()
    rating = models.PositiveSmallIntegerField(default=5)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Testimonial by {self.user.username}"

class Recipe(models.Model):
    CATEGORY_CHOICES = [
        ('vegetarian', 'Vegetarian'),
        ('italian', 'Italian'),
        ('breakfast', 'Breakfast'),
        ('dessert', 'Dessert'),
        ('other', 'Other'),
    ]
    
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    
    title = models.CharField(max_length=100)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    preparation_time = models.PositiveIntegerField(help_text="Time in minutes")
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)
    tags = models.CharField(max_length=200, blank=True)
    image = models.ImageField(upload_to='recipes/')
    rating = models.FloatField(default=0)
    review_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    is_approved = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Recipe"
        verbose_name_plural = "Recipes"
        ordering = ['-rating', '-created_at']
    
    def __str__(self):
        return self.title
    
    def get_category_color(self):
        color_map = {
            'vegetarian': 'success',
            'italian': 'primary',
            'breakfast': 'warning',
            'dessert': 'danger',
            'other': 'secondary'
        }
        return color_map.get(self.category, 'secondary')  