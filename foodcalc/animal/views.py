from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect
from animal.models import Animal
from django.views.generic import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from calc.forms import AnimalForm
from pages.urls import csrf_failure


class OnlyOwnerMixin(UserPassesTestMixin):
    def test_func(self):
        object = self.get_object()
        return object.owner == self.request.user

    def handle_no_permission(self):
        if self.request.user.is_anonymous:
            login_url = reverse('login')
            return redirect(f'{login_url}?next={self.request.path}')

        return csrf_failure(
            self.request,
            reason='У вас нет прав для редактирования этого питомца')


class AnimalCreateView(LoginRequiredMixin, CreateView):
    model = Animal
    form_class = AnimalForm
    template_name = 'animal/create.html'

    def get_initial(self, *args, **kwargs):
        _dict = super().get_initial(*args, **kwargs)
        _dict['request'] = self.request
        return _dict

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

    def get_initial(self, *args, **kwargs):
        _dict = super().get_initial(*args, **kwargs)
        _dict['request'] = self.request
        return _dict

    def get_success_url(self):
        return reverse_lazy('calc:profile',
                            args=(self.request.user,))


class AnimalDeleteView(OnlyOwnerMixin, DeleteView):
    model = Animal
    template_name = 'animal/create.html'

    def get_success_url(self):
        return reverse_lazy('calc:profile',
                            args=(self.request.user,))
