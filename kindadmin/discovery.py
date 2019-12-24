from django.conf import settings

def autoDiscoveryAdmin():
    for app in settings.INSTALLED_APPS:
        try:
            module = __import__('%s.kindadmin' % app)
            print(module.kindadmin)
        except Exception as e:
            print(e)
            pass