from django.urls import path
from .views import *
urlpatterns = [
    path('<slug:slug>/',product_inside,name="product_inside"),
    path('all-products',allproducts,name="allproducts"),
  


    
    #API for category list
    path('category-details',cat_list,name="cat_list"),
    path('discount-events',discountevents),
    path('discount-coupons',discount_coupon),


    path('review_post',review_post,name="review_post"),
    path('filter',productfilter,name="productfilter"),
    
      path('export-excel', DownloadProductDetailsView.as_view(), name='export_excel'),


    path('upload',upload,name='upload_file'),
    path('colorfamily',colorfamily,name="colorfamily"),
    path('getdata', getdata, name="getdata"),
    path('getstate', getstate, name="getstatelist"),
    path('getcities/<str:state_code>', getcities, name="getcitieslist"),
    
    ]