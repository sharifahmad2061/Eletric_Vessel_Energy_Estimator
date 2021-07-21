from django.urls import path, re_path
from .views import AboutView,   view_routes, getOutputData, getRoutes

from django.conf.urls import url
from RouteTracker import views
from django.views.generic import RedirectView


urlpatterns = [
    path('about/', AboutView.as_view(), name="about"),
    path('view/', view_routes, name="view"), 
    path('view/outputData', getOutputData, name='getOutputData'),   
    path('view/getRoutes', getRoutes, name='getRoutes'), 
    re_path(r'^.*/$', RedirectView.as_view(permanent=False, url="view/"))
   
]