from django.contrib import admin
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('',views.home,name="home"),
    path('about/',views.about,name="about"),
    path('register/',views.register,name="register"),
    path('login/',views.signin,name="login"),
    path('logout/',views.signout,name="logout"),
    path('offences/',views.offences,name="offences"),
    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
