from django.contrib import admin

from .models import Favorite, Follow, Purchase


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe', 'date_added')
    list_select_related = True
    list_filter = ('user__username',)
    search_fields = ('user__username',)


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'author', 'subscription_date')
    list_select_related = True
    list_filter = ('user__username',)
    search_fields = ('user__username',)


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe', 'date_added')
    list_select_related = True
    list_filter = ('user__username',)
    search_fields = ('user__username',)
