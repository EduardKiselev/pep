from django.urls import reverse_lazy, reverse
from animal.models import Animal
from django.views.generic import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from calc.forms import AnimalForm


class OnlyOwnerMixin(UserPassesTestMixin):
    def test_func(self):
        object = self.get_object()
        return object.owner == self.request.user


class AnimalCreateView(LoginRequiredMixin, CreateView):
    model = Animal
    form_class = AnimalForm
    template_name = 'animal/create.html'

    def get_form_kwargs(self, *args, **kwargs):
        form_kwargs = super().get_form_kwargs(*args, **kwargs)
        form_kwargs['request'] = self.request
        return form_kwargs

    def form_valid(self, form):
        form.instance.owner = self.request.user
        form.save()
        return super(AnimalCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('calc:profile', args=(self.request.user,))


class AnimalUpdateView(OnlyOwnerMixin, UpdateView):
    model = Animal
    form_class = AnimalForm
    template_name = 'animal/create.html'

    def get_success_url(self):
        return reverse_lazy('calc:profile',
                            args=(self.request.user,))


class AnimalDeleteView(OnlyOwnerMixin, DeleteView):
    model = Animal
    template_name = 'animal/create.html'

    def get_success_url(self):
        return reverse_lazy('calc:profile',
                            args=(self.request.user,))
