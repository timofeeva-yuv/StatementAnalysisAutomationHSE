from django.apps import AppConfig


class NavigationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'navigation'

    def ready(self):
        super().ready()
        self.create_menu_items()

    def create_menu_items(self):
        from .models import MenuItem

        MenuItem.objects.get_or_create(
            title='Пресеты',
            url='/alarms/',
            order=1
        )
        MenuItem.objects.get_or_create(
            title='Песочница',
            url='/sandbox/',
            order=2
        )
        MenuItem.objects.get_or_create(
            title='Дэшборды',
            url='/dashboard/',
            order=3
        )
        MenuItem.objects.get_or_create(
            title='База данных',
            url='/database/',
            order=3
        )

