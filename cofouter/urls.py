"""cofouter URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url, patterns
from django.conf import settings
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from cofouter import views
from wiki.urls import get_pattern as get_wiki_pattern
from django_nyt.urls import get_pattern as get_nyt_pattern

urlpatterns = [
    url(r'^$', views.landing, name="landing"),
    url(r'^register/$', views.register, name="register"),
    url(r'^about/$', views.about, name="about"),
    url(r'^evesso.*', views.ssologin, name="evesso"),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^applications/', include('applications.urls', namespace='applications')),
    url(r'^srp/', include('srp.urls', namespace='srp')),
    url(r'^reddit/', include('subreddit.urls', namespace='subreddit')),
    url(r'^hipchat/', include('hipchat.urls', namespace='hipchat')),
    url(r'^timerboard/', include('timerboard.urls', namespace='timerboard')),
    url(r'^corpmarket/', include('corpmarket.urls', namespace="corpmarket")),
    url(r'^helpdesk/', include('helpdesk.urls', namespace="helpdesk")),
    url(r'^skillchecker/', include('skillchecker.urls', namespace="skillchecker")),
    url(r'^wikinotifications/', get_nyt_pattern()),
    url(r'^wiki/', get_wiki_pattern()),
    url(r'^', include('core.urls', namespace='core')),
]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += patterns('',
                            url(r'^media/(?P<path>.*)$',
                                'django.views.static.serve',
                                {'document_root': settings.MEDIA_ROOT,
                                 }),
                            )