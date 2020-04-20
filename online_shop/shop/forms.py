from django.core.exceptions import ValidationError
from django import forms
from .models import User, Review, CartFullness, Product, Paper
from django.contrib.auth.forms import UserCreationForm
from ckeditor.widgets import CKEditorWidget


class PaperAdminForm(forms.ModelForm):
    text = forms.CharField(widget=CKEditorWidget(), label='Текст')

    class Meta:
        model = Paper
        fields = ['title', 'text', 'products', 'categories']


class ProductAdminForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorWidget(), label='Описание')

    class Meta:
        model = Product
        fields = ['name', 'price', 'quantity', 'category', 'description', 'image']


class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('email', 'password1', 'password2',)

    def clean(self):
        email = self.cleaned_data.get('email')
        user = User.objects.filter(username=email) or None
        if user:
            raise ValidationError('Такой e-mail уже зарегистрирован')
        return super().clean()


class ReviewForm(forms.ModelForm):
    text = forms.CharField(widget=forms.Textarea, label='Отзыв')

    class Meta(object):
        model = Review
        fields = ['id', 'user', 'product', 'text', 'rating']
        exclude = ('id', 'user', 'product')
        widgets = {
            'rating': forms.RadioSelect()
        }


class NumberForm(forms.Form):
    quantity = forms.IntegerField(widget=forms.NumberInput, label='Количество')

    def clean(self):
        count = self.cleaned_data.get('quantity')
        if count < 1:
            raise ValidationError('Некорректное количество товара')
        return super().clean()
