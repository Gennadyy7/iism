from django.conf import settings
from django.urls import NoReverseMatch, reverse
from django.views.generic import TemplateView


class IndexView(TemplateView):
    template_name = 'index.html'

    @staticmethod
    def get_lab_apps():
        """
        Dynamically discovers lab applications and their index URLs.
        Lab apps must follow naming convention: 'lab' + number (e.g., 'lab1', 'lab2')
        Each lab app must have 'index' named URL pattern.
        """
        lab_apps = []
        print(f'{settings.INSTALLED_APPS=}')
        for app_name in settings.INSTALLED_APPS:
            if app_name.startswith('lab'):
                try:
                    lab_number = int(app_name.replace('lab', ''))
                    display_name = f"Lab {lab_number}"
                except ValueError:
                    display_name = app_name
                print(f'{display_name=}')
                try:
                    url = reverse(f"{app_name}:index")
                    lab_apps.append({
                        'name': app_name,
                        'display_name': display_name,
                        'url': url
                    })
                except NoReverseMatch as e:
                    print(f'{e=}')
                    continue
        print(f'{lab_apps=}')
        return sorted(lab_apps, key=lambda x: x['name'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lab_apps'] = self.get_lab_apps()
        return context
