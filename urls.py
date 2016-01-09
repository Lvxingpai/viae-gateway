from django.conf.urls import url

from app.views import tasks

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = [
    url(r'^tasks/?$', tasks)
]

