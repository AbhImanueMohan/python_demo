from django.shortcuts import redirect
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

# Custom LoginView to redirect logged-in users
class CustomLoginView(auth_views.LoginView):
    template_name = 'login.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('movie_list')
        return super().dispatch(request, *args, **kwargs)


urlpatterns = [
    # Login page (first page)
    path('', CustomLoginView.as_view(), name='login'),

    # Registration
    path('register/', views.register, name='register'),

    # Logout (POST only)
# urls.py
path('logout/', auth_views.LogoutView.as_view(next_page='movie_list'), name='logout'),

    # Movie list (after login)
    path('movies/', views.MovieListView.as_view(), name='movie_list'),

    # Movie detail
    path('movie/<slug:slug>/', views.MovieDetailView.as_view(), name='movie_detail'),

    # Add / Edit / Delete Movie
    path('movie/add/', views.MovieCreateView.as_view(), name='movie_create'),
    path('movie/<slug:slug>/edit/', views.MovieUpdateView.as_view(), name='movie_update'),
    path('movie/<slug:slug>/delete/', views.MovieDeleteView.as_view(), name='movie_delete'),

    # Movies by Category
    path('category/<slug:slug>/', views.MoviesByCategoryView.as_view(), name='movies_by_category'),

    # Search
    path('search/', views.SearchResultsView.as_view(), name='search_results'),

    # User Movies
    path('user/<str:username>/', views.UserMoviesView.as_view(), name='user_movies'),

    # Comments
    path('movie/<slug:slug>/comment/add/', views.add_comment, name='add_comment'),
    path('comment/<int:pk>/delete/', views.delete_comment, name='delete_comment'),

    # Favorites
    path('movie/<slug:slug>/favorite/', views.toggle_favorite, name='toggle_favorite'),

    # Dashboard
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
]
