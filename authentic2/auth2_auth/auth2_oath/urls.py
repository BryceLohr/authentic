from django.conf.urls import patterns
import views

urlpatterns = patterns('',
        (r'^new_totp_secret$', views.new_totp_secret),
        (r'^delete_totp_secret$', views.delete_totp_secret))
