# -*- coding: utf-8 -*-

# Global Imports:
from django.conf.urls import include, url
from django.views.generic import TemplateView

urlpatterns = [
    # Index:
    url(r'^$',
        TemplateView.as_view(template_name='index.html'),
        name='index'),

    # hcapp
    url(r'^hc/', include('hcapp.urls')),

    # exchangeapp
    url(r'^exchange/', include('exchangeapp.urls')),

    # devaluationapp
    url(r'^devaluation/', include('devaluationapp.urls')),

    # About:
    url(r'^about/$',
        TemplateView.as_view(template_name='about.html'),
        name='about'),
]
