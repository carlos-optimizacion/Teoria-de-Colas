from django.contrib import admin
from .models import GameRun, SavedScenario, UserProgress

@admin.register(GameRun)
class GameRunAdmin(admin.ModelAdmin):
    list_display=("id","user","scenario","score","passed","created_at")
    list_filter=("scenario","passed","created_at")
    search_fields=("user__username","title")

@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display=("user","level","xp","coins","updated_at")

@admin.register(SavedScenario)
class SavedScenarioAdmin(admin.ModelAdmin):
    list_display=("name","user","scenario","updated_at")
