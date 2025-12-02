from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.text import slugify
from django.db.models import Q
from django.contrib.auth import login
from .forms import UserRegisterForm, CommentForm
from .models import Movie, Category, Comment, Favorite

# ----------------------
# Movie Views
# ----------------------
class MovieListView(LoginRequiredMixin, ListView):
    model = Movie
    template_name = 'movies/movie_list.html'
    context_object_name = 'movies'
    paginate_by = 12


class MovieDetailView(LoginRequiredMixin, DetailView):
    model = Movie
    template_name = 'movies/movie_detail.html'
    context_object_name = 'movie'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = CommentForm()
        context['is_favorited'] = False
        user = self.request.user
        if user.is_authenticated:
            context['is_favorited'] = Favorite.objects.filter(user=user, movie=self.object).exists()
        return context


class MovieCreateView(LoginRequiredMixin, CreateView):
    model = Movie
    template_name = 'movies/movie_form.html'
    fields = ['title', 'poster', 'description', 'release_date', 'actors', 'rating', 'category', 'trailer_url']

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        if not form.instance.slug:
            form.instance.slug = slugify(form.instance.title)[:280]
        messages.success(self.request, 'Movie added successfully.')
        return super().form_valid(form)


class MovieOwnerMixin(UserPassesTestMixin):
    def test_func(self):
        obj = self.get_object()
        return obj.created_by == self.request.user


class MovieUpdateView(LoginRequiredMixin, MovieOwnerMixin, UpdateView):
    model = Movie
    template_name = 'movies/movie_form.html'
    fields = ['title', 'poster', 'description', 'release_date', 'actors', 'rating', 'category', 'trailer_url']

    def form_valid(self, form):
        messages.success(self.request, 'Movie updated successfully.')
        return super().form_valid(form)


class MovieDeleteView(LoginRequiredMixin, MovieOwnerMixin, DeleteView):
    model = Movie
    template_name = 'movies/movie_confirm_delete.html'
    success_url = reverse_lazy('movie_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Movie deleted successfully.')
        return super().delete(request, *args, **kwargs)


class MoviesByCategoryView(LoginRequiredMixin, ListView):
    model = Movie
    template_name = 'movies/movies_by_category.html'
    context_object_name = 'movies'
    paginate_by = 12

    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs.get('slug'))
        return Movie.objects.filter(category=self.category)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class SearchResultsView(LoginRequiredMixin, ListView):
    model = Movie
    template_name = 'movies/search_results.html'
    context_object_name = 'movies'
    paginate_by = 12

    def get_queryset(self):
        query = self.request.GET.get('q', '')
        return Movie.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(actors__icontains=query) |
            Q(category__name__icontains=query)
        ).distinct()


class UserMoviesView(LoginRequiredMixin, ListView):
    model = Movie
    template_name = 'movies/user_movies.html'
    context_object_name = 'movies'
    paginate_by = 12

    def get_queryset(self):
        return Movie.objects.filter(created_by__username=self.kwargs.get('username'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['viewed_user'] = self.kwargs.get('username')
        return context

# ----------------------
# Comment & Favorite Views
# ----------------------
@login_required
def add_comment(request, slug):
    movie = get_object_or_404(Movie, slug=slug)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.movie = movie
            comment.user = request.user
            comment.save()
            messages.success(request, 'Comment posted.')
        else:
            messages.error(request, 'Error with your comment.')
    return redirect(movie.get_absolute_url())


@login_required
def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    movie = comment.movie
    if comment.user != request.user and not request.user.is_staff:
        messages.error(request, "You don't have permission to delete this comment.")
        return redirect(movie.get_absolute_url())
    comment.delete()
    messages.success(request, 'Comment deleted.')
    return redirect(movie.get_absolute_url())


@login_required
def toggle_favorite(request, slug):
    movie = get_object_or_404(Movie, slug=slug)
    fav, created = Favorite.objects.get_or_create(user=request.user, movie=movie)
    if not created:
        fav.delete()
        messages.info(request, 'Removed from favorites.')
    else:
        messages.success(request, 'Added to favorites.')
    return redirect(movie.get_absolute_url())

# ----------------------
# Registration & Dashboard
# ----------------------
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome {user.username}, your account has been created!')
            return redirect('movie_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserRegisterForm()
    return render(request, 'movies/register.html', {'form': form})


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'movies/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['my_movies'] = Movie.objects.filter(created_by=user)
        context['favorites'] = Movie.objects.filter(favorited_by__user=user)
        context['recent_comments'] = Comment.objects.filter(user=user)[:10]
        return context
