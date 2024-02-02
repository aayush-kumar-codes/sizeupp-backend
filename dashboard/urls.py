from django.urls import path
from dashboard import views
import functions
urlpatterns = [
    path('', views.dashboard,name="dashboard"),
    path('signin', views.signin,name="dashboard_signin"),
    path('logout', views.logout_user,name="logout"),
    path('products',views.Products_dashboard,name="products_dashboard"),
    path('media_dashboard',views.media_dashboard,name="media_dashboard"),
    path('scrolling-banner-images',views.scrolling_banner_images,name="scrolling_banner_images"),
    path('scrolling-text', views.scrolling_text, name="scrolling_text"),
    path('banner-images',views.banner_images,name="banner_images"),

    #
    path('img_products/<slug:id>',views.img_products,name="img_products"),



    path('category',views.category,name='category_dashboard'),
    path('category-crud/',views.category_crud,name='category_crud'),

    path('subcategory',views.subcategory,name='sub_category_dashboard'),
    path('subcategory-crud',views.subcategory_by_id,name='sub_category_crud'),
    
    
    path('sub-subcategory',views.sub_subcategory,name='sub_sub_category_dashboard'),
    path('sub-subcategory-crud',views.sub_subcategory_by_id,name='sub_sub_category_crud'),


    path('add-product',views.addproduct,name='addproduct'),
    path('add-product_crud/<slug:id>',views.addproduct_crud,name='addproduct_crud'),
    # path('sqp_list/',views.sqp_list,name="sqp_list"),
    path('sqp_crud',views.sqp_crud,name="sqp_crud"),
    # path('product/<uuid:id>/<str:slug>',views.product_by_id,name='product_crud'),


    #users List

    path('Users',views.users_list,name="users_list"),

    path('Colour-Family/',views.colour_family_dashboard,name="colour_family_dashboard"),

    path('coupons-List/',views.coupons_list,name="coupons_list"),
    path('coupons-crud/<slug:id>',views.coupons_crud,name="coupon_crud"),
    
    path('orders-list',views.order_list,name="order_list"),
    path('order-details/<slug:slug>',views.order_details,name="order_details"),
    path('order-tracking/<slug:slug>',views.order_tracking,name="order_tracking"),
    path('order-edit/<slug:id>',views.order_crud,name="order_crud"),


    path('product-reviews/',views.product_reviews,name="product_reviews"),
    path('discount-event',views.event_list,name="event_list"),


    path('All-Articles/',views.all_articles,name="all_articles"),


    path('pos/',views.pos,name='pos'),
    path('support-tickets/',views.support_tickets,name='support_tickets'),
    path('todolist',views.todoList_crud,name='todoList_crud'),
    path('revenue-data',views.revenue_data,name="revenue-data"),

    path('return-orders',views.return_orders_lst,name="return_order_list"),
    path('download-order-history',views.export_orders,name='export_orders'),


    path('promotional-message',views.promotional,name='promotional'),


]