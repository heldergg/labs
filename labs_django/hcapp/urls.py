# -*- coding: utf-8 -*-

# Global Imports:
from django.conf.urls import include, url
from django.views.generic import TemplateView

# Local Imports:
from hcapp import views

urlpatterns = [
    # Create the requested hemicycle
    url(r'^svg/$', views.svg_hemicycle, name='svg_hemicycle'),

    # Show election results
    url(r'^$', views.results, name='hc_results'),

    ##
    # Static pages

    # About:
    url(r'^about/$',
        TemplateView.as_view(template_name='hc_about.html'),
        name='hc_about'),

    # Notes:
    url(r'^notes/$',
        TemplateView.as_view(template_name='hc_notes.html'),
        name='hc_notes'),

    # Law:
    url(r'^law/$',
        TemplateView.as_view(template_name='hc_law.html'),
        name='hc_law'),
]
