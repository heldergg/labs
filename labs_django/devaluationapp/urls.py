# -*- coding: utf-8 -*-

# Global Imports:
from django.conf.urls import include, url
from django.views.generic import TemplateView

# Local Imports:
from devaluationapp import views

urlpatterns = [
    # Calculate the exchange rates
    url(r'^$', views.devaluation_calc, name='devaluation_calc'),

    ##
    # Static pages

    # Notes:
    url(r'^notes/$',
        TemplateView.as_view(template_name='devaluation_notes.html'),
        name='devaluation_notes'),
    # About:
    url(r'^about/$',
        TemplateView.as_view(template_name='devaluation_about.html'),
        name='devaluation_about'),
]
