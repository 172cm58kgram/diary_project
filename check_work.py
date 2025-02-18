from django.apps import apps
import django
from diary.models import DiaryEntry, Tag
django.setup()
apps.get_app_config('diary')
exit()