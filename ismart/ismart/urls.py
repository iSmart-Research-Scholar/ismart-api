from django.contrib import admin
from django.urls import path
from ismart.views import ranking,summarizer,summarizeView,authorProfiling,imgtotextView

urlpatterns = [
    path("admin", admin.site.urls),
    path('api/ranking', ranking.ranking),
    path('api/summarize',summarizeView.display_summary,name='summarizer'),
    path('api/authorProfiling', authorProfiling.authorProfiling),
    path('api/imgToText', imgtotextView.HomeRoute),
]