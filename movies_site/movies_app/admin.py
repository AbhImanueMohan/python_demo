from django.contrib import admin
from .models import Movie, Category, Comment, Profile, Favorite

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'created_by', 'release_date', 'rating')
    list_filter = ('category', 'created_by')
    search_fields = ('title', 'actors', 'description')
    prepopulated_fields = {'slug': ('title',)}

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'movie', 'created_at')
    list_filter = ('created_at', 'user')
    search_fields = ('content',)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio')

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'movie', 'created_at')
    list_filter = ('created_at', 'user', 'movie')