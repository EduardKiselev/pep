from django import forms
from calc.models import User


class PetForm(forms.Form):
    chose_pet = forms.CharField(max_length=150)


class FoodForm(forms.Form):
    food = forms.CharField(max_length=150)


class RemoveFoodForm(forms.Form):
    remove_food = forms.CharField(max_length=150)


class MassForm(forms.Form):
    mass = forms.IntegerField()


class NutrinentForm(forms.Form):
    nutr_add = forms.CharField(max_length=50)


class RemoveNutrinentForm(forms.Form):
    remove_nutr = forms.CharField(max_length=50)


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']

