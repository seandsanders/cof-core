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
from django.contrib import admin
from cofouter import views

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
    url(r'^', include('core.urls', namespace='core')),
]
