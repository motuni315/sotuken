from django.apps import AppConfig


class SotukenConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sotuken'

    def ready(self):
      import sotuken.signals  # シグナルを登録
