# -*- coding: utf-8 -*-

# Global Imports:
from django.conf.urls import include, url
from django.views.generic import TemplateView

# Local Imports:
from timeclockapp import views

urlpatterns = [
    ##
    # Static pages

    # Notes:
    url(r'^index/$',
        TemplateView.as_view(template_name='timeclock_index.html'),
        name='timeclock_index'),
    # About:
    url(r'^about/$',
        TemplateView.as_view(template_name='timeclock_about.html'),
        name='timeclock_about'),
]

