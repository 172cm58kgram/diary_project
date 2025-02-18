from rest_framework import generics
from .models import DiaryEntry, Tag, AccessLog
from .serializers import DiaryEntrySerializer, TagSerializer
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render, get_object_or_404, redirect
from .forms import DiaryEntryForm, TagForm, CustomUserCreationForm, EmailLoginForm
import datetime
from datetime import date, datetime
from django.utils.timezone import localdate
from django.contrib.auth.decorators import login_required
import calendar
import django
django.setup()
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.contrib import messages


class CustomLoginView(LoginView):
    authentication_form = EmailLoginForm

def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'diary/register.html', {'form': form})

def home(request):
    today = date.today()
    date_str = request.GET.get("date")

    if date_str:
        try:
            selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            selected_date = today  # 無効な日付が渡されたら今日にする
    else:
        selected_date = today

    # アクセス情報を取得
    ip = get_client_ip(request)
    user_agent = request.META.get("HTTP_USER_AGENT", "Unknown")
    referer = request.META.get("HTTP_REFERER", "")

    # ログインしているユーザーを記録
    user = request.user if request.user.is_authenticated else None

    # アクセスログを記録
    AccessLog.objects.create(ip_address=ip, user_agent=user_agent, referer=referer, user=user)

    # selected_date が定義された後に entries を取得する
    entries = DiaryEntry.objects.filter(date=selected_date).order_by("-date")

    return render(request, "diary/home.html", {
        "entries": entries,
        "selected_date": selected_date,
    })

def get_client_ip(request):
    """ リクエストのIPアドレスを取得する """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
    
# ユーザーのIPアドレスを取得する関数
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

@login_required
def new_entry(request):
    if request.method == "POST":
        form = DiaryEntryForm(request.POST, request.FILES)
        if form.is_valid():
            entry = form.save(commit=False)  # まだ保存しない
            entry.user = request.user  # ユーザーをセット
            entry.save()
            form.save_m2m()  # ManyToManyField の保存
            # 複数のタグを追加（最大20個）
            new_tag_names = request.POST.get('new_tag', '').split(',')
            new_tag_names = [tag.strip() for tag in new_tag_names if tag.strip()]  # 空白削除 & 空要素除外
            
            if len(new_tag_names) > 20:
                messages.error(request, "タグは最大20個までしか追加できません。")
            else:
                for tag_name in new_tag_names:
                    tag, created = Tag.objects.get_or_create(name=tag_name)
                    entry.tags.add(tag)
            messages.success(request, "日記が投稿されました！")
            return redirect('home')
    else:
        form = DiaryEntryForm()

    return render(request, 'diary/new_entry.html', {'form': form})

# 日記を編集@login_required
def edit_entry(request, pk):
    entry = get_object_or_404(DiaryEntry, pk=pk, user=request.user)
    
    if request.method == "POST":
        form = DiaryEntryForm(request.POST, request.FILES, instance=entry)
        new_tags = request.POST.get("new_tag", "").split(",")  # 新しいタグを取得
        remove_tags = request.POST.getlist("remove_tags")  # 削除するタグを取得
        
        if form.is_valid():
            entry = form.save()

            # 既存のタグを削除
            for tag_id in remove_tags:
                tag = get_object_or_404(Tag, id=tag_id)
                entry.tags.remove(tag)

            # 新しいタグを追加
            for tag_name in new_tags:
                tag_name = tag_name.strip()
                if tag_name:
                    tag, created = Tag.objects.get_or_create(name=tag_name)
                    entry.tags.add(tag)

            messages.success(request, "日記が更新されました！")
            return redirect('entry_detail', pk=entry.pk)
    else:
        form = DiaryEntryForm(instance=entry)
    
    return render(request, 'diary/edit_entry.html', {
        'form': form,
        'entry': entry,
        'existing_tags': entry.tags.all()
    })

# 日記を削除
@login_required
def delete_entry(request, pk):
    entry = get_object_or_404(DiaryEntry, pk=pk, user=request.user)
    if request.method == "POST":
        entry.delete()
        messages.success(request, "日記が削除されました！")
        return redirect('home')
    
    return render(request, 'diary/delete_entry.html', {'entry': entry})


def entry_detail(request, pk):
    entry = get_object_or_404(DiaryEntry, pk=pk)
    return render(request, 'diary/entry_detail.html', {'entry': entry})

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

def calendar_view(request):
    today = localdate()
    year, month = today.year, today.month
    month_days = calendar.monthcalendar(year, month)

    # データベースから該当する月の日記を取得
    entries = DiaryEntry.objects.filter(date__year=year, date__month=month)

    # 日記を日付ごとに辞書に整理
    entries_by_day = {entry.date.day: entry for entry in entries}

    return render(request, 'diary/calendar.html', {
        'year': year,
        'month': month,
        'month_days': month_days,
        'entries_by_day': entries_by_day,  # 正しく辞書形式で渡す
    })


def search_by_tags(request):
    query = request.GET.get("query", "")  # 検索クエリ（デフォルトは空）
    
    if query:
        tags = Tag.objects.filter(name__icontains=query)  # 部分一致検索
    else:
        tags = Tag.objects.all()  # クエリがない場合、全てのタグを表示

    return render(request, "diary/tag_search_form.html", {
        "tags": tags,
        "query": query,  # 検索クエリをフォームに保持
    })

def add_tag(request):
    if request.method == 'POST':
        form = TagForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('tag_list')  # タグ一覧ページにリダイレクト
    else:
        form = TagForm()

    return render(request, 'diary/add_tag.html', {'form': form})

def tag_list(request):
    tags = Tag.objects.all()
    return render(request, 'diary/tag_list.html', {'tags': tags})

def search_by_tags(request):
    query = request.GET.get("query", "")  # 検索フォームの入力値を取得
    
    if query:
        tags = Tag.objects.filter(name__icontains=query)  # 部分一致でタグを検索
    else:
        tags = Tag.objects.all()  # クエリがない場合は全タグを表示
    
    return render(request, "diary/tag_search_form.html", {
        "tags": tags,
        "query": query,  # フォームに現在の検索クエリを保持
    })
    
def entry_detail(request, pk):  # ✅ `pk` を受け取るように修正
    entry = get_object_or_404(DiaryEntry, pk=pk)
    return render(request, 'diary/entry_detail.html', {'entry': entry})

def entries_by_tag(request, tag_name):
    tag = get_object_or_404(Tag, name=tag_name)
    
    # 並び替えのオプション
    sort = request.GET.get("sort", "newest")  # デフォルトは新しい順
    
    if sort == "oldest":
        entries = DiaryEntry.objects.filter(tags=tag).order_by("date")
    elif sort == "popular":
        entries = DiaryEntry.objects.filter(tags=tag).order_by("-views_count")
    else:  # デフォルト（新しい順）
        entries = DiaryEntry.objects.filter(tags=tag).order_by("-date")

    return render(request, "diary/entries_by_tag.html", {
        "entries": entries,
        "tag": tag,
        "sort": sort
    })