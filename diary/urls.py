from rest_framework import generics
from .models import DiaryEntry, Tag
from .serializers import DiaryEntrySerializer, TagSerializer
from rest_framework.permissions import IsAuthenticated
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import register , CustomLoginView
from django.contrib.auth.views import LoginView


class DiaryEntryListCreateView(generics.ListCreateAPIView):
    serializer_class = DiaryEntrySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return DiaryEntry.objects.filter(user=self.request.user).order_by('-date')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class DiaryEntryRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DiaryEntrySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return DiaryEntry.objects.filter(user=self.request.user)

class TagListView(generics.ListAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

urlpatterns = [
    path('', views.home, name='home'),
    path('entry/<int:pk>/', views.entry_detail, name='entry_detail'), 
    path('new/', views.new_entry, name='new_entry'),
    path('calendar/', views.calendar_view, name='calendar'),
    path('search/', views.search_by_tags, name='search_by_tags'),
    path('login/', auth_views.LoginView.as_view(template_name='diary/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('add_tag/', views.add_tag, name='add_tag'),  # タグ追加ページ
    path("tags/", views.tag_list, name="tag_list"),
    path("search_by_tags/", views.search_by_tags, name="search_by_tags"),
    path("tags/<str:tag_name>/", views.entries_by_tag, name="entries_by_tag"),
    path("entry/<int:entry_id>/", views.entry_detail, name="entry_detail"), 
    path('entry/<int:pk>/edit/', views.edit_entry, name='edit_entry'),  # 編集ページ
    path('entry/<int:pk>/delete/', views.delete_entry, name='delete_entry'),  # 削除ページ
]

urlpatterns += [
    path('register/', register, name='register'),
    path('login/', CustomLoginView.as_view(template_name='diary/login.html'), name='login'),
]