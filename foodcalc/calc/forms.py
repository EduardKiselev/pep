from django import forms
from calc.models import User, NutrientsName, Rations
from animal.models import Animal


class PetForm(forms.Form):
    chose_pet = forms.CharField(max_length=150)


class FoodForm(forms.Form):
    food = forms.CharField(max_length=150)


class RationCreateForm(forms.ModelForm):
    class Meta:
        model = Rations
        fields = ['ration_name', 'ration_comment']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        print(self.request.user)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(RationCreateForm, self).clean()
        print('sdfsdfsdfsdf', cleaned_data, self.request.user)
        ration_name = cleaned_data.get('ration_name')
        if Rations.objects.filter(ration_name=ration_name,
                                  owner=self.request.user).exists():
            raise forms.ValidationError(
                {'ration_name': 'У вас уже есть ацион с таким названием', })


class RemoveFoodForm(forms.Form):
    remove_food = forms.CharField(max_length=150)


class MassForm(forms.Form):
    mass = forms.FloatField()


class NutrinentForm(forms.Form):
    nutr_add = forms.CharField(max_length=50)


class RemoveNutrinentForm(forms.Form):
    remove_nutr = forms.CharField(max_length=50)


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']


class FoodNameForm(forms.Form):
    food_name = forms.CharField(max_length=50)


class FormNutrAdd(forms.Form):

    def __init__(self, *args, **kwargs):
        self.chooses = kwargs.pop('choses', None)
        super().__init__(*args, **kwargs)

    nutrient = forms.ModelChoiceField(queryset=NutrientsName.objects.none())
    amount = forms.FloatField()


class FormNutrRemove(forms.Form):
    nutrient = forms.ModelChoiceField(queryset=NutrientsName.objects.none(),)


class AnimalForm(forms.ModelForm):
    class Meta:
        model = Animal
        fields = ['name', 'type', 'nursing',
                  'sterilized', 'weight', 'birthday', ]

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        print(self.request.user)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('sterilized') and cleaned_data.get('nursing'):
            raise forms.ValidationError(
                {'nursing': '''Не возможно быть одновременно стерилизованным
                 и кормящим/беременным''',
                 'sterilized': '''Не возможно быть одновременно стерилизованным
                 и кормящим/беременным'''
                 })
        name = cleaned_data.get('name')
        if Animal.objects.filter(name=name, owner=self.request.user).exists():
            raise forms.ValidationError(
                {'name': 'У вас уже есть питомец с этим именем', })


class FoodCreateForm(forms.Form):
    description = forms.CharField(max_length=150, label='Введите имя продукта')
    based_on = forms.CharField(max_length=150, required=False)
    text = forms.CharField(max_length=300, required=False)


class FileForm(forms.Form):
    file_name = forms.CharField()


class RationCommentForm(forms.ModelForm):
    
    class Meta:
        model = Rations
        fields = ("ration_comment",)
