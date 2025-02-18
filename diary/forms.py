from django import forms
from .models import DiaryEntry, Tag
from datetime import date
from .models import CustomUser
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

class EmailLoginForm(AuthenticationForm):
    username = forms.EmailField(label="メールアドレス")

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['email']


class DiaryEntryForm(forms.ModelForm):
    new_tag = forms.CharField(
        max_length=50, required=False, label="新しいタグ"
    )  # 新しいタグを入力するフィールドを追加
    
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.none(),  # 初期値を空にする
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=False
    )  # ユーザーが過去の日付を選択できる
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tags'].queryset = Tag.objects.all()  # フォームの初期化時に設定
        
    class Meta:
        model = DiaryEntry
        fields = ['title','date', 'content', 'image', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'tags': forms.CheckboxSelectMultiple(),
        }
        
        def clean_tags(self):
            """ タグの制限を設定（20個まで）"""
            tags = self.cleaned_data.get('tags')
            if tags and len(tags) > 20:
                raise forms.ValidationError("タグは最大20個まで選択できます。")
            return tags
            
        def save(self, commit=True):
            entry = super().save(commit=False)
            if not entry.date:
                entry.date = date.today() # 日付が指定されていなければ当日にする
            if commit:
                entry.save()
                self.save_m2m()  # ManyToManyField の保存
            # 新しいタグが入力されている場合は作成する
            new_tag_name = self.cleaned_data.get('new_tag')
            if new_tag_name:
                tag, created = Tag.objects.get_or_create(name=new_tag_name)
                entry.save()  # 先に保存してから ManyToMany を追加
                entry.tags.add(tag)

            if commit:
                entry.save()
                self.save_m2m()  #  ManyToMany関係を保存
            
            return entry
        
        
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # ユーザー情報を取得
        super().__init__(*args, **kwargs)
    
    def save(self, commit=True):
        entry = super().save(commit=False)
        if self.user:
            entry.user = self.user  # フォーム送信時に user をセット
        if commit:
            entry.save()
            self.save_m2m()
        return entry

class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }