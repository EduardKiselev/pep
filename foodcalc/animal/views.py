from django.urls import reverse_lazy, reverse
from animal.models import Animal
from django.views.generic import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django import forms
from calc.forms import AnimalForm
from django.shortcuts import redirect


class OnlyOwnerMixin(UserPassesTestMixin):
    def test_func(self):
        object = self.get_object()
        return object.owner == self.request.user


class AnimalCreateView(LoginRequiredMixin, CreateView):
    model = Animal
    fields = ['name', 'type', 'nursing', 'sterilized', 'weight', 'birthday']
    template_name = 'animal/create.html'

    def form_valid(self, form):
        self.object = form.save(commit=False)
        sterilized = form.cleaned_data.get('sterilized')
        nursing = form.cleaned_data.get('nursing')
        if sterilized*nursing:
            form.add_error('nursing', forms.ValidationError(
                '''не возможно быть одновременно стерилизованным
                и кормящим/беременным'''))
            return super().form_invalid(form)

        name = form.cleaned_data.get('name')
        if len(Animal.objects.filter(name=name, owner=self.request.user)) == 1:
            form.add_error('name',
                           forms.ValidationError('''У вас уже есть питомец
                                                 с этим именем'''))
            return super().form_invalid(form)

        form.instance.owner = self.request.user
        self.object.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('calc:profile', args=(self.request.user,))


class AnimalUpdateView(OnlyOwnerMixin, UpdateView):
    model = Animal
    form_class = AnimalForm
    template_name = 'animal/create.html'

    def form_valid(self, form):
        self.object = form.save(commit=False)

        sterilized = form.cleaned_data.get('sterilized')
        nursing = form.cleaned_data.get('nursing')
        if sterilized*nursing:
            form.add_error('nursing',
                           forms.ValidationError(
                               '''не возможно быть одновременно стерилизованным
                                                 и кормящим/беременным'''))
            return super().form_invalid(form)

        form.instance.owner = self.request.user
        self.object.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('calc:profile',
                            args=(self.request.user,))


class AnimalDeleteView(OnlyOwnerMixin, DeleteView):
    model = Animal
    template_name = 'animal/create.html'

    def get_success_url(self):
        return reverse_lazy('calc:profile',
                            args=(self.request.user,))
