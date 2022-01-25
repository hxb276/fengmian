"""fengmianapi URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from fengmian import views
from fengmian.views import AdCityView
urlpatterns = [
    path('admin/', admin.site.urls),
    path(r'fengmian/',views.IndexView.as_view(),name='index'),
    path(r'cityad/',AdCityView.as_view(),name='ad'),
    path(r'pdd-video/',views.PddVideoview.as_view(),name='pdd'),
    path(r'xuliehao/',views.FormatXuliehao.as_view(),name='format')

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
