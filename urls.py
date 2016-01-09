from django.conf.urls import patterns, url, include
from app.views import tasks, start_polling

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = [
    url(r'^tasks/?$', tasks),
    url(r'^polling/?$', start_polling)
]

