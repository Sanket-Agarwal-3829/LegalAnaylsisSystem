from django.contrib import admin
from .models import judgements, SearchFolders, SearchJudgement
# Register your models here.

admin.site.register(judgements)
admin.site.register(SearchJudgement)
admin.site.register(SearchFolders)