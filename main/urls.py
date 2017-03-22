from django.conf.urls import patterns, url
from main import views


urlpatterns = patterns('',
		url(r'^$', views.main, name='main'),
		url(r'^contact/$', views.contact, name = 'contact'),
		url(r'^add_category/$', views.add_category, name = 'add_category'),
		url(r'^category/(?P<category_name_url>\w+)/$', views.category, name = 'category'),
		url(r'^category/(?P<category_name_url>\w+)/add_page/$', views.add_page, name='add_page'),
		url(r'^register/$', views.register, name='register'),
		url(r'^login/$', views.user_login, name='login'),
		url(r'^restricted/', views.restricted, name='restricted'),
		url(r'^logout/$', views.user_logout, name='logout'),
		url(r'^like_category/$', views.like_category, name='like_category'),
		url(r'^suggest_category/$', views.suggest_category, name='suggest_category'),


		)