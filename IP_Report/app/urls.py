from django.urls import path
from . import views
from django.conf.urls import url


urlpatterns = [

    url(r'^$', views.index , name="index"),
    url(r'^image_index/', views.image_index , name="image_index"),
    url(r'^result/', views.result , name="result"),
    url(r'^image_extractor/', views.image_extractor , name="image_extractor"),
    url(r'^download_images/', views.download_images, name= "download_images"),
    url(r'^login/', views.login , name="login"),

]

