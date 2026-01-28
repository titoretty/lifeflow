from django.urls import path
from . import views   # <-- correct

urlpatterns = [
    path('', views.landing, name='landing'),
    path('welcome/', views.welcome, name='welcome'),
 path('gallery/', views.gallery, name='gallery'),
    path('index', views.index, name='index'),
    path('about/', views.about, name='about'),
    path("slogan/", views.slogan, name="slogan"),
    path('logout/', views.logout_view, name='logout'),
    path('header/', views.header, name='header'),
    path('contact/', views.contact, name='contact'),
   #user
    path('user_register', views.user_register, name='user_register'),
    path("user_login/", views.user_login, name="user_login"),
    path('register/', views.register, name='register'),
    path("Donate_blood/<int:hospital_id>/", views.Donate_blood, name="Donate_blood"),

path('camp_announce/', views.camp_announce, name='camp_announce'),

    #hospital
    path('hos_register', views.hos_register, name='hos_register'),
    path('hos_login', views.hos_login, name='hos_login'),
    path('hos_index', views.hos_index, name='hos_index'),
    path('donate', views.donate, name='donate'),
    path("hospital_list", views.hospital_list, name="hospital_list"),
    path('donate_request/', views.donate_request, name='donate_request'),
    # Approve / Reject donation requests
    path('approve-request/<int:donation_id>/', views.approve_request, name='approve_request'),

    path('hospital/reject/<int:donation_id>/', views.reject_request, name='reject_request'),
    path('blood_camp', views.blood_camp, name='blood_camp'),
    path('user/dashboard/', views.user_dashboard, name='user_dashboard'),
    path('hospital_dashboard/',views.hospital_dashboard,name='hospital_dashboard'),
    path('hospital/camps/', views.hospital_camps, name='hospital_camps'),
    path('hospital/complete-camp/<int:camp_id>/', views.complete_camp, name='complete_camp'),

    path('stock/',views.stock,name='stock'),
    path('hospital/complete-camp/<int:camp_id>/', views.complete_camp, name='complete_camp'),
    path('hospital/see-camp/', views.see_camp, name='see_camp'),
    path('notifications',views.notifications,name='notifications'),
    path('donation_history',views.donor_history,name='donation_history'),
#receiver
    path('search-blood/', views.search_blood, name='search_blood'),
    path('request-blood/<int:hospital_id>/', views.request_blood, name='request_blood'),
    path('approve-receiver/<int:request_id>/', views.approve_receiver_request, name='approve_receiver'),
    path('reject-receiver/<int:request_id>/', views.reject_receiver_request, name='reject_receiver'),
    path('receiver/history/', views.receiver_history, name='receiver_history'),

    path('hospital/receiver-requests/', views.receiver_requests, name='receiver_requests'),
    path('donors_list',views.donors_list,name='donors_list'),
    path('add_stock',views.add_stock,name='add_stock'),
    path('profile/', views.profile, name='profile'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    #admin
    path('dashboard',views.dashboard,name='dashboard'),
    # path('request_blood',views.request_blood,name='request_blood'),
    path('emergency/', views.emergency, name='emergency'),
    path( 'hospital/donations/',views.approve_list,name='approve_list' ),
    # Mark donation page (form + submit)
    path( 'hospital/mark-donation/<int:donate_id>/', views.mark_donation,name='mark_donation'  ),
    path('eligibility/', views.eligibility_status, name='eligibility_status'),
    path('emergency/request/<int:donor_id>/', views.send_emergency_request, name='send_emergency_request'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/approve-hospital/<int:hospital_id>/', views.approve_hospital, name='approve_hospital'),
    path('dashboard/reject-hospital/<int:hospital_id>/', views.reject_hospital, name='reject_hospital'),
    #Admin
    path('admin_login/', views.admin_login, name='admin_login'),
    path('admin_logout/', views.admin_logout, name='admin_logout'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin_users/', views.admin_users, name='admin_users'),
    path('admin_hospitals/', views.admin_hospitals, name='admin_hospitals'),
    path('admin_header/', views.admin_header, name='admin_header'),

    

]
