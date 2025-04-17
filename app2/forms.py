from django import forms
from .models import Testimonial
from .models import Recipe

class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = '__all__'
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'tags': forms.TextInput(attrs={'placeholder': 'Comma-separated tags'}),
        }
class TestimonialForm(forms.ModelForm):
    class Meta:
        model = Testimonial
        fields = ['user_title', 'content', 'rating']
        widgets = {
            'rating': forms.HiddenInput(),
        }