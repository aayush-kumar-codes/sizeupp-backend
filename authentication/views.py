from django.shortcuts import render, redirect,get_object_or_404,HttpResponseRedirect
from authentication.models import *
from product.models import *
from django.contrib.auth import authenticate, login
import random
from django.contrib.auth import logout
from django.views.decorators.http import require_GET
from functions import *
from django.contrib import messages
from django.db.models import Q
# from django.utils.timezone import datetime
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.decorators.csrf import csrf_protect
from rest_framework.decorators import api_view, permission_classes,authentication_classes
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from dashboard.models import HomeBannerImages,HomeBannerScrolling , HomeTextScrolling
from product.models import Product
from product import serializers
from product.serializers import product_serializer
from dashboard.models import *
import paypalrestsdk
from django.db.models import Sum
from django.contrib.auth.hashers import check_password
from django.shortcuts import render, redirect
from taggit.models import Tag
from rest_framework.authtoken.models import Token
import requests
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.authentication import TokenAuthentication
from .serializer import *
from SizeUpp import settings
from datetime import datetime
from .deliveryApi import *
from .smsgateway import *

@api_view(['GET'])
def banner_scrolling(request):
    banner = HomeBannerScrollingSerializer(HomeBannerScrolling.objects.all()[::-1],many=True).data
    return Response(banner,status=status.HTTP_200_OK)


@api_view(['GET'])
def text_scrolling(request):
    text = HomeTextScrollingSerializer(HomeTextScrolling.objects.last()).data
    return Response(text, status=status.HTTP_200_OK)

@api_view(['GET'])
def validate_pincode(request,slug):
    url = 'https://api.instashipin.com/api/v1/tenancy/authToken'
    payload ={
        "api_key": 
            "6092655223372029e7404dc4"
        }
    headers = {
            'Content-Type': 'application/json',
        }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
            data = response.json()
            token = data['data']['response']['token_id']    
            settings.SHIPING_TOKEN = token

        
    url = 'https://api.instashipin.com/api/v1/courier-vendor/check-pincode'

    payload = {
        "token_id": settings.SHIPING_TOKEN,
        "pincode": slug,
      
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        # Request was successful
        data = response.json()
        message = data['data']['response']['message']
        return Response({'message':message},status=status.HTTP_200_OK)



 
            
@api_view(['GET','POST'])
def home(request):
    if request.method == 'POST':
        email =request.data.get('email')
        if request.user.is_authenticated:
            
            if request.user.newsletter == True:
                message='Already Subscribed to Newsletter!!'
                return Response({'message':message},status=status.HTTP_502_BAD_GATEWAY)

            elif request.user.email == email:
                user = User.objects.get(email=email)
                user.newsletter =True
                user.save()
                message='Thank You Subscribing to Our Newsletter'
                return Response({'message':message},status=status.HTTP_200_OK)


            elif Newsletter.objects.filter(email=email).exists():
                            message='Already Subscribed to Newsletter !!'
                            return Response({'message':message},status=status.HTTP_502_BAD_GATEWAY)

            else:
                Newsletter.objects.create(email=email).save()

                message='Thank You Subscribing to Our Newsletter'
                return Response({'message':message},status=status.HTTP_200_OK)
            
        else:
                    return Response({'message':"Authentication Required"},status=status.HTTP_407_PROXY_AUTHENTICATION_REQUIRED)


    products = Product.objects.all().order_by('created_at').reverse()[:10]
    serializer = serializers.product_serializer(products,many=True)
    products=serializer.data

    # sale_on_product = DiscountOnProducts.objects.filter(active=True).order_by('created_at').reverse()[:2]


    #topselling products 
    top_selling_products = Product.objects.filter(
        orderitem__isnull=False  # Only consider products that have associated order items
    ).annotate(
        total_quantity=Sum('orderitem__quantity')  # Calculate the total quantity sold
    ).order_by(
        '-total_quantity'  # Order by total quantity in descending order
    )[:12]
    
    cntx={
        'title': 'Size Upp | Home',
        'img':HomeBannerImages.objects.first(),
        'images':HomeBannerScrolling.objects.all(),
        'products':products,
        # 'sale_on_product':sale_on_product,
        'top_selling_products':top_selling_products
    }
    return Response( cntx,status=status.HTTP_200_OK)



@api_view(['POST'])
# @authentication_classes([TokenAuthentication])
# @permission_classes([IsAuthenticated])
def validate_token(request):
    token = request.data.get('token')
    if Token.objects.filter(key = token).exists():    
        return Response({'message':'Token Accepted'},status=status.HTTP_200_OK)
    else:
        return Response({'message':"Invalid Token"},status=status.HTTP_502_BAD_GATEWAY)


@csrf_protect
@api_view(['POST'])
def signup(request):
    if request.user.is_authenticated:
        return Response( status=status.HTTP_407_PROXY_AUTHENTICATION_REQUIRED)
    
    else:
        if request.method == 'POST':
            first_name = request.data.get('first_name')
            last_name = request.data.get('last_name')
            email = request.data.get('email')
            phone = request.data.get('phone')
            password1 = request.data.get('password')
            newsletter = request.data.get('newsletter')
            # newsletter = True/False
            if newsletter == "on":
                newsletter = True
            else:
                newsletter = False

            if not email  or not phone or not password1:
                message='Require fileds'
                return Response( {'message':message},status=status.HTTP_208_ALREADY_REPORTED)
            
            if User.objects.filter(username=email).exists():
                message='Email Alrady Registered !!'
                return Response( {'message':message},status=status.HTTP_208_ALREADY_REPORTED)
            
            if User.objects.filter(email=email).exists():
                message='Email Alrady Registered !!'
                return Response( {'message':message},status=status.HTTP_208_ALREADY_REPORTED)
            
            if User.objects.filter(phone=phone).exists():
                message='Phone numeber is already registered !!'
                return Response( {'message':message},status=status.HTTP_208_ALREADY_REPORTED)
            

            user = User.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=email,
                phone=phone,
                newsletter=newsletter,
            )
            user.set_password(password1)
            user.save()
            user = authenticate(request, username=email, password=password1)

            login(request, user)

            # send_welcome_email(user)
            token, created = Token.objects.get_or_create(user=user)
            
            # send otp to mobile
            
            # send_welcome_email(user)
            return Response({
                        'message': 'Login successful.',
                        'user_verified': user.is_verified,
                        'token': token.key,  # Include the token in the response
                    }, status=status.HTTP_200_OK)

        else:
            return Response( status=status.HTTP_502_BAD_GATEWAY)
        
        

        
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def logout_view(request):
    if request.user.is_authenticated:
        Token.objects.get(user=request.user).delete()
        logout(request)
        return Response({'message': 'Logout successful.'}, status=status.HTTP_200_OK)
    else:
        return Response({'message': 'User is not authenticated.'}, status=status.HTTP_400_BAD_REQUEST)


@csrf_protect
@api_view(['POST'])
def signin(request):
        if request.user.is_authenticated:
            return redirect('home')     
        
        if request.method == 'POST':
            email = request.data.get('email')
            password = request.data.get('password')
            
            try:    
                user = User.objects.get(email=email)
                if check_password(password, user.password):
                    login(request, user)
                    token, created = Token.objects.get_or_create(user=user)

                    return Response({
                        'message': 'Login successful.',
                        'user_verified': user.is_verified,
                        'token': token.key,  # Include the token in the response
                    }, status=status.HTTP_200_OK)
                else:
                        return Response({'message': 'Invalid Password.'}, status=status.HTTP_502_BAD_GATEWAY)
            except:
                        
                        return Response({'message': 'Email Not Exist.'}, status=status.HTTP_502_BAD_GATEWAY)
      


# @api_view(['POST'])
# def forgot_password(request):
    

#     if request.method == 'POST':
#         email = request.data.get('email')
#         # Check if the user exists
#         if  User.objects.filter(email=email).exists():
#             return Response({'message': 'Email Exist'}, status=status.HTTP_200_OK)
        

#         else:
#             # Handle the case where the user does not exist
#             message='Email Not Exist!!'
#             return Response({'message': message}, status=status.HTTP_502_BAD_GATEWAY)
     
#     # If it's a GET request, render the empty form


@api_view(['POST','GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def otp(request):
    if request.user.is_authenticated:
        if request.user.is_verified :   
            return Response({'message': 'Verified','user_verified':request.user.is_verified}, status=status.HTTP_200_OK)

            
    if not request.user.is_verified:

        email = request.user.email
        user = User.objects.get(email=email)
        
        if request.method == 'POST':
            otp = request.data.get('otp')
         
            otp = str(otp['1']) + str(otp['2'])+ str(otp['3']) + str(otp['4'])
            if int(user.otp) == int(otp):
                
                user.is_verified = True
                user.otp = ''
                user.save()

                login(request, user)
                smsGateway("account created",user=user)
                return Response({'message': 'Verification Done','user_verified':user.is_verified}, status=status.HTTP_200_OK)
                            
            else:
                message="OTP Invalid"
                return Response({'message': message}, status=status.HTTP_502_BAD_GATEWAY)
            
        if request.method == 'GET':  
            # if user.otp == '':
                otp = random.randint(1000, 9999)
                user.otp = otp
                user.save()
                # send opt to email
                send_email_otp(user=user,otp=otp)
                smsGateway("register otp",user = user,otp= otp)
                return Response({'message': 'OTP sent on Email','user_email':user.email}, status=status.HTTP_200_OK)
            # return Response({'message': 'OTP Already sent on Email','user_email':user.email}, status=status.HTTP_200_OK)


     
@api_view(['POST'])
def otp_forgot_pass(request):
        
        if request.method == 'POST':
            email = request.data.get('email')
            pass1 = request.data.get('password')
            if User.objects.filter(email=email).exists():
                user = User.objects.get(email=email)
            else:
                return Response({'message':'Email not  resgister !'},status=status.HTTP_502_BAD_GATEWAY)
            
            
            otp = request.data.get('otp')

            if otp:
                otp = str(otp['1']) + str(otp['2'])+ str(otp['3']) + str(otp['4'])
                if user.otp == otp:
                    user.is_verified = True
                    user.otp = ''
                    user.set_password(pass1)
                    user.save()

                    return Response({'message': 'Verification Done','user_verified':user.is_verified}, status=status.HTTP_200_OK)
                            
                else:
                    message="OTP Invalid"
                    return Response({'message': message}, status=status.HTTP_502_BAD_GATEWAY)
            
            
            else:           
                otp = random.randint(1000, 9999)
                user.otp = otp
                user.save()
                # send opt to email
                send_email_otp(user=user,otp=otp)
                smsGateway("register otp",user = user,otp = otp)
                message= 'OTP sent on email'
                return Response({'message': message}, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def userprofile(request):
    if not request.user.is_authenticated:
        return Response({'message':'Login Required'}, status=status.HTTP_502_BAD_GATEWAY)
    
    elif not request.user.is_verified :
            return Response({'message':'Email Not Verified','user_verified':request.user.is_verified}, status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
    
    
    
    print(Address.objects.filter(user=request.user))
    address = AddressSerializer(Address.objects.filter(user=request.user),many=True)
    orders = OrderserSerializer(Order.objects.filter(customer_email = request.user.email)[::-1],many =True)
    
    
    
    return Response({'user_info':UserSerialize(request.user).data,'addresses':address.data,'orders':orders.data}, status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def address(request):
    user = User.objects.get(email=request.user.email)
    if not request.user.is_authenticated:
        return Response({'message':'Login Required'}, status=status.HTTP_502_BAD_GATEWAY)
    
    elif not user.is_verified :
            return Response({'message':'Email Not Verified','user_verified':user.is_verified}, status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
    
    if request.method == 'POST':
            print(request.user.email)
            user = User.objects.get(id=request.user.id)
            address_line_1 = request.data.get('address_line_1')
            address_line_2 = request.data.get('address_line_2')
            city = request.data.get('city')
            postal_code = request.data.get('postal_code')
            country = request.data.get('country','India')
            state = request.data.get('state')
         
            addresses = Address.objects.filter(user=request.user)
            if addresses:
                for address in addresses:
                    address.is_default = False
                    address.save()


            address = Address.objects.create(
                user = user,
                address_line_1 = address_line_1,
                address_line_2 = address_line_2,
                city = city,
                postal_code = postal_code,
                country = country,
                state = state,
                is_default = True,
            )
            address.save()
            message= "Address Added Successfully"
            return Response({'message': message}, status=status.HTTP_200_OK)
    
    



@api_view(['PUT','DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])      
def address_by_id(request,slug):

    if not request.user.is_authenticated:
        return redirect('signin')
    
    elif not request.user.is_verified :
            request.session['signup_email'] = request.user.email
            return redirect('otp')
    
    if request.method == 'PUT':
                address_id = slug
                address_line_1 = request.data.get('address_line_1')
                address_line_2 = request.data.get('address_line_2')
                state = request.data.get('state')
                city = request.data.get('city')
                country = request.data.get('country')
                postal_code = request.data.get('postal_code')
                
                address = Address.objects.get(id=address_id)
               
                addresses = Address.objects.filter(user=request.user)
                for old_address in addresses:
                        old_address.is_default = False
                        old_address.save()
                        
                if address_line_1:
                    
                    address.address_line_1 = address_line_1
                if address_line_2:
                    address.address_line_2 = address_line_2
                if city:
                    address.city = city
                if postal_code:
                    address.postal_code = postal_code
                if country:
                    address.country = country
                if state:
                    address.state = state
                    
                address.is_default = True
                address.save()
                message= "Address Updated Successfully"
                return Response({'message': message}, status=status.HTTP_200_OK)
        
    
        
    if request.method == 'DELETE':
        address_id =slug
        address = Address.objects.get(id=address_id)
        address.delete()
        if Address.objects.filter(user=request.user).exists():
            addresses = Address.objects.filter(user=request.user)
            for old_address in addresses:
                        old_address.is_default = False
                        old_address.save()
            address = Address.objects.filter(user=request.user).first()
            address.is_default = True
            address.save()
        return Response({'message': "Deleted Successfully"}, status=status.HTTP_200_OK)
    

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated]) 
def updateCart(request,slug):
    product = get_object_or_404(Product,id=slug)
    cart = Cart.objects.get(user=request.user,product=product)
    
    if request.method == 'POST':
        qty= request.data.get('qty',None)
        status_ = request.data.get('status')

        sqp_id = request.data.get('sqp_id',None)
        
        
        if status_:
            if status_ == 'add':
                if  int(SizeQuantityPrice.objects.get(id=cart.size_quantity_price).quantity) < (int(cart.quantity) +1):
                    return Response({'message':'Out of Stock'},status=status.HTTP_502_BAD_GATEWAY)
                cart.quantity = int(cart.quantity) + 1
            elif status_ == 'subtract':
                if int(cart.quantity) == 1:
                    cart.delete()
                    return Response({'message':'Cart Deleted'},status=status.HTTP_200_OK)
                cart.quantity = int(cart.quantity) - 1
                
        if qty:
            if  int(SizeQuantityPrice.objects.get(id=cart.size_quantity_price).quantity) < (int(qty)):
                    return Response({'message':'Out of Stock'},status=status.HTTP_502_BAD_GATEWAY)
                
            cart.quantity = int(qty) 
            # if status_ == 'subtract':
            
        
        cart.save()
        
        cart.sub_total = round((float(cart.quantity)*float(cart.mrp)),2)
        cart.save()

        if cart.discount_on_price != 0:
                cart.total_price =round(float(cart.sub_total)-(float(cart.quantity)*float(cart.discount_on_price)),2)   
        else:
            cart.total_price = round((float(cart.quantity)*float(cart.mrp)),2)
            
        if sqp_id:
            sqp = SizeQuantityPrice.objects.get(id=sqp_id)
            cart.size_quantity_price = sqp
        
        cart.save()
        return Response({'message':'Cart is Updated'},status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])    
def Add_Cart(request,slug):

    if request.user.is_authenticated:
        

        if request.method == 'POST':
            qty= request.data.get('qty',1)
            sqp_id = request.data.get('sqp_id')
            
        user = get_object_or_404(User,id=request.user.id)
        pro = get_object_or_404(Product,id=slug)
        size_quantity_price = get_object_or_404(SizeQuantityPrice,id=sqp_id)
        

        sub_total = (float(qty)*float(pro.mrp))
        
        
        
        if pro.discount == True:
            discount_on_price = round(float(pro.mrp) - float(pro.discounted_price),2)
            
            total_price =round((float(qty)*float(pro.discounted_price)),2)
            
        else: 
            discount_on_price = 0
            total_price=sub_total

        
        if Cart.objects.filter(user=request.user,product=pro,size_quantity_price =size_quantity_price ).exists():
            return Response({'Message':'Already In Cart'},status=status.HTTP_208_ALREADY_REPORTED)
        
        if int(size_quantity_price.quantity) >= int(qty):
            
            cart_item = Cart.objects.create(user=user,product=pro,quantity=qty,size_quantity_price=size_quantity_price,mrp=pro.mrp,total_price=total_price ,sub_total=sub_total,discount_on_price=discount_on_price)
        else:
            return Response({'message':'Out of Stock'},status=status.HTTP_502_BAD_GATEWAY)
        
        cart_item.save()
    
        message="Added to cart"
        return Response({'message':message,'cart_id':cart_item.id},status=status.HTTP_201_CREATED)
   

        # if status == 'UPDATE':
        #     cart_item=Cart.objects.get(user=user,product=pro)

        #     cart_item.total_price = total_price
        #     cart_item.quantity = qty
        #     cart_item.save()
        #     messages.success(request,'Cart is Updated Successfully!!')
        #     return redirect('updateCart')

        # if Cart.objects.filter(user=user,product=pro):


        #     messages.error(request,"Already In cart")
        #     return redirect('product_inside',pro.id)





@api_view(['POST','GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])    
def show_Cart(request):
    # try:
        if request.user.is_authenticated:
        
            cart_items = Cart.objects.filter(user=request.user)
            if not cart_items:
                return Response({'message':"Empty Cart"},status=status.HTTP_200_OK)
            code=None
            
            # pincode = Address.objects.get(user=request.user,is_default=True).postal_code
            # if pincode:

            #         # deliveryCharges = checkDelivery(pincode)
            # else:
            deliveryCharges = 0
                    
            if request.method == 'POST':
                code = request.data.get('code')
                    
                if code and DiscountCoupon.objects.filter(code=code).exists():
                        
                    discountcoupon=DiscountCoupon.objects.get(code=code)
                    if not Order.objects.filter(customer_email = request.user.email).exists():
                        
                        if discountcoupon.end_date > timezone.now():
                            coupon = 'active'
                            coupon_message = 'Successfully Applied'
                        else: 
                            coupon_message = 'Coupon is expired'
                            coupon = 'deactive'
                    else:
                        coupon_message = 'Coupon Already Applied'
                        coupon = 'deactive'

                else:
                    coupon_message = 'No coupon'
                    coupon = 'deactive'
            else:
                coupon_message = 'No coupon'

                coupon = 'deactive'
            
            products_list =[ ]
            total_price = 0
            mrp_price = 0
            sub_total=0
            discount_on_price = 0
            
            if cart_items.count() != 0:
                for item in cart_items:
                    mrp_price = round((mrp_price + (float(item.product.mrp)*int(item.quantity))),2)
                    
                    
                    sub_total = round(float(item.total_price)+ sub_total, 2)
                    if item.discount_on_price:
                        discount_on_price = discount_on_price + round((float(item.discount_on_price)*int(item.quantity)),2)
                    products_list.append({'qty':item.quantity,'cart':CartSerializer(item).data})
            else:
                return Response({'message':'Cart is Empty'},status=status.HTTP_400_BAD_REQUEST)  
            
            
            
            if coupon == 'active':
                if discountcoupon.percentage:
                    coupon_discount =  round(float(discountcoupon.percentage),2)*0.01
                if discountcoupon.price:
                    coupon_discount =  float(discountcoupon.price)

                cupon_discount = round(coupon_discount *sub_total,2)
            else:
                cupon_discount = 0
            
            total_price = round(sub_total + float(deliveryCharges),2)
            if cupon_discount !=0:
                total_price = round(sub_total - round(coupon_discount *sub_total,2) ,2)

                
            cntx={
                    'products':products_list,
                    'title':'My Cart',
                    'total_price':total_price,
                    'sub_total':sub_total,
                    'delivery_charges':deliveryCharges,
                    'coupon':coupon,
                    'cupon_discount':cupon_discount,
                    'mrp_price':mrp_price,
                    'discount_on_price':discount_on_price,
                    'coupon_message':coupon_message,
                    
                }

            
            return Response(cntx,status =status.HTTP_200_OK)
        
        
    # except Exception as e:
    #     return Response({"e":e}, status=status.HTTP_502_BAD_GATEWAY)
            
@api_view(['DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])    
def del_cart(request, slug):
    if request.user.is_authenticated:
        
        # product = Product.objects.get(id=slug)
        if Cart.objects.filter(id= slug).exists():
            cart = Cart.objects.get(id=slug)
            cart.delete()
            message="Deleted"
        else:
            message = "Not Found"
        cart= CartSerializer(Cart.objects.filter(user=request.user),many=True).data
        return Response({'message':message,'cart':cart},status=status.HTTP_200_OK)
   
from .ccavutil import encrypt,decrypt
# from .Responsehandle import res
from string import Template
from pay_ccavenue import CCAvenue
from django.http import HttpResponse 

def ccavResponseHandler():
    pass
def ccavRequestHandler(request,slug):
            order = Order.objects.get(id=slug)
            accessCode = 'AVYQ44KL42CE38QYEC'
            workingKey = '33BA817A5AB3463BFDEF2658EC1ADC0A'
            p_merchant_id = '3134871'
            p_order_id = order.id
            p_currency = 'INR'
            p_amount = str(order.payment_amount)
            p_redirect_url = 'https://www.sizeupp.com'
            p_cancel_url = 'https://www.sizeupp.com'
            p_language = 'EN'
            p_billing_name = order.customer_name
            p_billing_address = order.address_line_1 + order.address_line_2
            p_billing_city = order.city
            p_billing_state = order.state
            p_billing_zip = order.postal_code
            p_billing_country = 'India'
            p_billing_tel = order.customer_contact
            p_billing_email = order.customer_email
            p_delivery_name = order.customer_name
            p_delivery_address = order.address_line_1 + order.address_line_2
            p_delivery_city = order.city
            p_delivery_state = order.state
            p_delivery_zip = order.postal_code
            p_delivery_country ='India'
            p_delivery_tel =order.customer_contact
            
            
            p_merchant_param1 = ''
            p_merchant_param2 = ''
            p_merchant_param3 = ''
            p_merchant_param4 = ''
            p_merchant_param5 = ''
            p_promo_code = ''
            p_customer_identifier = order.customer_email
            
            

            merchant_data='merchant_id='+p_merchant_id+'&'+'order_id='+p_order_id + '&' + "currency=" + p_currency + '&' + 'amount=' + p_amount+'&'+'redirect_url='+p_redirect_url+'&'+'cancel_url='+p_cancel_url+'&'+'language='+p_language+'&'+'billing_name='+p_billing_name+'&'+'billing_address='+p_billing_address+'&'+'billing_city='+p_billing_city+'&'+'billing_state='+p_billing_state+'&'+'billing_zip='+p_billing_zip+'&'+'billing_country='+p_billing_country+'&'+'billing_tel='+p_billing_tel+'&'+'billing_email='+p_billing_email+'&'+'delivery_name='+p_delivery_name+'&'+'delivery_address='+p_delivery_address+'&'+'delivery_city='+p_delivery_city+'&'+'delivery_state='+p_delivery_state+'&'+'delivery_zip='+p_delivery_zip+'&'+'delivery_country='+p_delivery_country+'&'+'delivery_tel='+p_delivery_tel+'&'+'merchant_param1='+p_merchant_param1+'&'+'merchant_param2='+p_merchant_param2+'&'+'merchant_param3='+p_merchant_param3+'&'+'merchant_param4='+p_merchant_param4+'&'+'merchant_param5='+p_merchant_param5+'&'+'promo_code='+p_promo_code+'&'+'customer_identifier='+p_customer_identifier+'&'
            
            # mechant_data ='merchant_id=3134871&order_id=SZ-68914&currency=INR&amount=7498.00&redirect_url=https://www.sizeupp.com&cancel_url=https://www.sizeupp.com&language=EN&billing_name=KushalBauskar&billing_address=Sk road, RegencyRegency Anantam&billing_city=Araria&billing_state=Bihar&billing_zip=421202&billing_country=India&billing_tel=8433771414&billing_email=kbauskar07@gmail.com&delivery_name=KushalBauskar&delivery_address=Sk road, RegencyRegency Anantam&delivery_city=Araria&delivery_state=Bihar&delivery_zip=4212'
            
            
            encryption = encrypt(merchant_data,workingKey)

            html = '''\
                        <html>
			<head>
				<title>Sub-merchant checkout page</title>
				<script src="http://ajax.googleapis.com/ajax/libs/jquery/1.10.2/jquery.min.js"></script>
			</head>
			<body>
			<form id="nonseamless" method="post" name="redirect" action="https://test.ccavenue.com/transaction/transaction.do?command=initiateTransaction" > 
					<input type="hidden" id="encRequest" name="encRequest" value=$encReq>
					<input type="hidden" name="access_code" id="access_code" value=$xscode>
					<script language='javascript'>document.redirect.submit();</script>
			</form>    
			</body>
			</html>
                        '''
            fin = Template(html).safe_substitute(encReq=encryption,xscode=accessCode)

            # return Response({'fin':fin},status=status.HTTP_200_OK)
            return HttpResponse(merchant_data)
        
        
        


paypalrestsdk.configure({
    "mode": "sandbox",  # or "live"
    "client_id": "AW51S_03IaBs6Kc-6UqkuAqLq9VzcjASJtDuTtwJlHkZAOsjBuZI0qXiobIHptNyDkUFEFEY9mcE0APm",
    "client_secret": "EAq19jPmNnIL07UjfpfXow80Y_luf3Zubd6Z2U74duLn2zuqwS4FR0K-JDK9azi2d2dFy1Ht1SP3IkQ6"
})













@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])    
def create_order(request):
        if request.method == 'POST':
            # address_id = request.data.get('address_id')
            if not request.user.is_verified :
                return Response({'message':"Email Not verified"},status=status.HTTP_406_NOT_ACCEPTABLE)
            
            
            mrp_price = float(request.data.get('mrp_price', 0))
            sub_total = float(request.data.get('sub_total', 0))
            cupon_discount = float(request.data.get('cupon_discount', 0))
            total_price = float(request.data.get('total_price', 0))
            # cupon_discount = float(request.data.get('cupon_discount',0))
            
            coupon = request.data.get('coupon',None)
            payment_type = request.data.get('payment_type','COD')
            
            
            
            # if not address_id:
            #     message='Please Add/select Address'
            #     return Response({'message':message},status=status.HTTP_502_BAD_GATEWAY)

            address = Address.objects.get(user = request.user,is_default=True )
            
            
            order = Order.objects.create(
                customer_name = request.user.first_name + '' + request.user.last_name,
                customer_email = request.user.email,
                customer_contact = request.user.phone,
                address_line_1 = address.address_line_1,
                address_line_2 = address.address_line_2,
                city = address.city,
                postal_code = address.postal_code,
                country = address.country,
                state = address.state,
                
                payment_type = payment_type,
                payment_status = "Pending",
                payment_id = None,
                payment_amount = None, 
            )        
            
            # try :
            delivery_charges = checkDelivery(address.postal_code)
            # except Exception as e:
                # delivery_charges = 0

            order.payment_amount = total_price
            order.deliveryCharges = delivery_charges
            order.mrp_price = mrp_price            
            order.sub_total = round(sub_total,2)
            
            if coupon:
                order.cupon_discount = round(cupon_discount,2)
                
            order.coupon = coupon
            order.save()
            
            for cart in Cart.objects.filter(user=request.user):
                sqp = SizeQuantityPrice.objects.get(id=cart.size_quantity_price.id)
                
                if int(sqp.quantity) < int(cart.quantity) : 
                    return Response({'message':'Out Of Stock'},status=status.HTTP_502_BAD_GATEWAY)
                
                order_item = OrderItem.objects.create(
                        product = cart.product,
                        quantity = cart.quantity,
                        size = cart.size_quantity_price.size,
                        mrp = cart.mrp,
                        color = cart.product.color,
                        sub_total=cart.sub_total,
                        sqp_code=cart.size_quantity_price.id,
                    )
                
                order_item.save()
                order.order_items.add(order_item)
                order.save()
                
                
                
                sqp.quantity = int(sqp.quantity) - int(cart.quantity)
                sqp.save()
                
                cart.delete()
                
                
            
            if payment_type == 'COD':
                placeDelivery(order.id)
                
                # return redirect('ccav_request_handler',order.id)
                return Response({'message':'Order Created'},status=status.HTTP_200_OK)
            if payment_type == 'PPD' : 
                # accessCode = 'AVYQ44KL42CE38QYEC' 	
                # workingKey = '33BA817A5AB3463BFDEF2658EC1ADC0A'
                accessCode = settings.ACCESSCODE	
                workingKey = settings.WORKINGKEY
                merchant_data=f'merchant_id=3134871&order_id={str(order.id)}&currency=INR&amount={str(order.payment_amount)}&redirect_url=https://dashboard.sizeupp.com/api/payment-status&cancel_url=https://dashboard.sizeupp.com/api/payment-status&language=en&billing_name={order.customer_name}&billing_address={str(order.address_line_1) + str(order.address_line_2) }&billing_city={order.city}&billing_state={order.state}&billing_zip={order.postal_code}&billing_country={order.country}&billing_tel={order.customer_contact}&billing_email={order.customer_email}'
                # &delivery_name='+p_delivery_name+'&'+'delivery_address='+p_delivery_address+'&'+'delivery_city='+p_delivery_city+'&'+'delivery_state='+p_delivery_state+'&'+'delivery_zip='+p_delivery_zip+'&'+'delivery_country='+p_delivery_country+'&'+'delivery_tel='+p_delivery_tel+'&'+'merchant_param1='+p_merchant_param1+'&'+'merchant_param2='+p_merchant_param2+'&'+'merchant_param3='+p_merchant_param3+'&'+'merchant_param4='+p_merchant_param4+'&'+'merchant_param5='+p_merchant_param5+'&'+'integration_type='+p_integration_type+'&'+'&'+'customer_identifier='+p_customer_identifier+'&'
                
                # if coupon:
                #     merchant_data = merchant_data + '&promo_code='+ coupon
	
                encryption = encrypt(merchant_data,workingKey)
                html = f"https://secure.ccavenue.com/transaction/transaction.do?command=initiateTransaction&merchant_id=3134871&encRequest={encryption}&access_code={accessCode}"

                return Response({"redirect_url" : html},status = status.HTTP_200_OK)
        



@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])   
def order_detail(request,slug):
    order = Order.objects.get(id=slug)
    
    # if order.delivery_status != 'Cancel':
    #     trackorder(order.airwaybilno)
    
    order =OrderserSerializer(order).data
    return Response({'order':order},status=status.HTTP_200_OK)





@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])    
def update_order(request,uuid):
    order = Order.objects.get(id=uuid)
    if order.payment_type != 'COD':
        
        payment_status = request.data.get('payment_status',None)
        payment_id = request.data.get('payment_id',None)
        # delivery_status = request.data.get('payment_status',None)
        # payment_status = request.data.get('payment_status',None)
        order.payment_status = payment_status
        order.payment_id = payment_id
        if payment_status == 'Completed':
            order.delivery_status = "Order Processing"

            #ship-delite integration
            
            
    return Response({'message':'Order Updated'},status=status.HTTP_200_OK)









# Navigations pages
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])    
def contactus(request):
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        email = request.data.get('email')
        phone_number =request.data.get('phone_number')
        issue = request.data.get('issue')
        message = request.data.get('message')

        enquiry = SupportTickets.objects.create(name=first_name, email=email,number=phone_number,issue=issue,
                                        message=message)
        enquiry.save()
        message='Support Tickets Generated Successfully'
        return Response({'message':message},status=status.HTTP_200_OK)
        
    


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])    
def wishlist(request):
    if request.user.is_authenticated:
        wishlist = WishList.objects.filter(user=request.user)
        # cart_items_lis = Cart.objects.filter(user=request.user)

        # cart_items=[]
        # if wishlist:
        #     for item in wishlist:
        #         for citem in cart_items_lis:
        #             pro = get_object_or_404(Product,id=item.product.id)
        #             product =product_serializer(pro).data
        #             if citem.product.id == item.product.id:
        #                 product['cart'] = True
        #             else:
        #                 product['cart'] = True
        #             cart_items.append(product)
        cntx={
                'wishlist':WishListSerializer(wishlist,many=True).data,
            }
        return Response(cntx,status=status.HTTP_200_OK)

    


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])    
def add_wishlist(request,slug):
    if request.user.is_authenticated:
        try:
            pro = get_object_or_404(Product,id=slug)
            WishList.objects.create(user=request.user,product=pro).save()

            return Response({'message':"Added to wishlist"},status=status.HTTP_200_OK)
        except:
             message='Already in wishlist'
             return Response({'message':message},status=status.HTTP_208_ALREADY_REPORTED)

    else:
        return redirect('signin')


@api_view(['DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])  
def remove_wishlist(request,slug):
    #  if request.user.is_authenticated:
    #     product = get_object_or_404(Product,id=slug)
    #     if WishList.objects.filter(product=product).exists():
    #         WishList.objects.get(product=product).delete()

    #     wishlist = WishListSerializer(WishList.objects.filter(user=request.user),many=True).data
    #     return Response({'wishlist':wishlist},status=status.HTTP_200_OK)
    
    
    if request.user.is_authenticated:
        product = get_object_or_404(Product, id=slug)
        wishlists = WishList.objects.filter(user=request.user, product=product)

        if wishlists.exists():
            wishlists.delete()

        updated_wishlist = WishListSerializer(WishList.objects.filter(user=request.user), many=True).data

        return Response({'wishlist': updated_wishlist}, status=status.HTTP_200_OK)    



def Track_order(request):
     if not request.user.is_authenticated:
            return redirect('signin')
     
     id = request.GET.get('id')
     if id:
            order = Order.objects.get(id=id)
     else:       
        try:
             
            order = Order.objects.filter(user=request.user).order_by('-id')[0]
        except :
             order =None

     return render(request,"user_profile/order-tracking.html",{'title':'Order Tracking','order':order})



@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])  
def Update_Profile(request):
    if  request.method == 'POST':
         first_name = request.data.get('first_name')
         last_name = request.data.get('last_name')
         contact = request.data.get('contact')
         gender = request.data.get('gender')
         new_email =request.data.get('new_email')
         user = User.objects.get(id = request.user.id)

         
         
         if User.objects.filter(phone=contact).exists():
                message = 'Phone numeber is already registered !!'
                return Response({"message":"Mobile Number Already Register"},status=status.HTTP_502_BAD_GATEWAY)

         if first_name:
            user.first_name = first_name
         if last_name:
            user.last_name = last_name
         if  contact:
            user.phone = contact
         if gender:
            user.gender = gender
            
         user.save()

         if new_email:
                if User.objects.filter(email=new_email).exists():
                    message='Email Alrady Registered !!'
                    return Response({'message':message},status=status.HTTP_502_BAD_GATEWAY)
                
                user.email = new_email
                user.is_verified = False

                user.save()
                
                return Response({'message':"Profile Updated",'user_verified':request.user.is_verified},status=status.HTTP_200_OK)

         return Response({'message':"Profile Updated"},status=status.HTTP_200_OK)

    




@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])  
def return_product(request):
     
     if request.method == 'POST':
            order_id = request.data.get('id')
            issue = request.data.get('issue')
            customer_name =request.data.get('customer_name')
            bank_name =request.data.get('bank_name')
            ifsc =request.data.get('ifsc')
            account_no =request.data.get('account_no')
            products =request.data.get('products')
            
            
            order = Order.objects.get(id =order_id)
            if ReturnOrders.objects.filter(order = order).exists():
                message = "Return Order Already Initiated !!"
                return Response({'message':message},status=status.HTTP_502_BAD_GATEWAY)
            else:
                 if order.delivery_status in ['Order Processing','Delivered','Cancelled' , 'Order Return']:
                    
                    return_order = ReturnOrders.objects.create(
                        order =order,
                        issue=issue,
                        customer_name=customer_name,
                        bank_name=bank_name,
                        ifsc=ifsc,
                        account_no=account_no,
                    )
                    return_order.save()
                    for product in products:
                        # order_item = OrderItem.objects.get(order=order,product =product)
                        return_order.order_item.add(product['id'])
                        return_order.save()
                    
                        
                        
                    message="Return Order Initiated !!"
                    if order.delivery_status == 'Order Processing':
                        cancelDelivery(order.airwaybilno,order.id)
                        order.order_cancel = True
                        order.delivery_status = 'Cancelled'
                        order.save()
                        smsGateway("order cancel",order=order,user=request.user)
                        
                    
                    if  order.delivery_status == 'Delivered':
                        
                        returnDeliveryOrder(order_id,products)
                        smsGateway("order return",order=order,user=request.user)
                        
                    return Response({'message':message},status=status.HTTP_200_OK) 

                 else:
                    return Response({'message':"cant't cancel Order Now."},status=status.HTTP_502_BAD_GATEWAY)
                
                
                
                
from django.db.models import Sum
from django.utils import timezone
from decimal import Decimal
@api_view(['GET'])
def SapAllOrders(request):
    # Get today's date
    today = timezone.now().date()

    # Query today's orders
    todays_orders = Order.objects.filter(created_at__date=today)

    # Calculate tax percentage
    tax_percentage = Decimal('12')

    # Prepare the response data
    response_data = []

    for order in todays_orders:
        order_data = {
            "OrderType": "Online",
            "DocDate": str(order.created_at.date()),
            "DeliveryDate": str(order.expected_date),
            "CustRefNumber": order.id,
            "AssValue": f"{order.sub_total}",
            "DeliveryStatus" : f"{order.delivery_status}",
            "Discount": f"{order.cupon_discount}",
            "TotTaxAmt": f"{order.payment_amount * (tax_percentage / 100)}",
            "TotOrderVal": f"{order.payment_amount}",
            "ShipToAdd": [
                {
                    "AddressLineName": order.customer_name,
                    "AddressLine1": order.address_line_1,
                    "AddressLine2": order.address_line_2,
                    "City": order.city,
                    "ZipCode": order.postal_code,
                    "State": order.state,
                    "Country": order.country
                }
            ],
            "BillToAdd": [
                {
                    "AddressLineName": order.customer_name,
                    "AddressLine1": order.address_line_1,
                    "AddressLine2": order.address_line_2,
                    "City": order.city,
                    "ZipCode": order.postal_code,
                    "State": order.state,
                    "Country": order.country
                }
            ],
            "LineItem": []
        }

        # Line items
        no = 1
        for item in order.order_items.all():
            if int(item.sub_total) > 1000:
                tax = round(item.sub_total * (12/100),2)
            else:
                tax = round(item.sub_total * (5/100),2)
            line_item = {
                "SrNo": no,
                "ItemCode": item.product.id,
                "Quantity": str(item.quantity),
                "MRP": f"{item.mrp}",
                "DiscountAmt": 0,
                "TotAfterDisc": item.sub_total,
                "COUPDiscAmt": "",
                "FinalPriceAfterDisc": item.sub_total,
                "GSTRate": "12",
                "IgstAmt": "",
                "CgstAmt": tax/2,
                "SgstAmt": tax/2,
                "TotTaxAmt": tax,
                "TotalLC": round((item.sub_total - tax),2),
                "TotAmt": item.sub_total    
            }
            order_data["LineItem"].append(line_item)

        response_data.append({"Data": [order_data]})

    return Response({'response_data':response_data},status=status.HTTP_200_OK)

@api_view(['GET'])
def fetch_new_orders(request):
    orders = OrderserSerializer(Order.objects.filter(order_cancel=False,order_return=False),many=True).data
    
    return Response({'orders':orders},status=status.HTTP_200_OK)




# @api_view(['POST'])
# @permission_classes(['AllowAny'])
from django.views.decorators.csrf import csrf_exempt
from urllib.parse import parse_qs
import json

@csrf_exempt
def payment_status(request):
    if request.method == 'POST':
        accessCode = settings.ACCESSCODE	
        workingKey = settings.WORKINGKEY
        
        merchant_data = request.POST.get('encResp')
        order_id = request.POST.get('orderNo')
        encryption = decrypt(merchant_data,workingKey)
        parsed_data = parse_qs(encryption)
        order_id = parsed_data['order_id'][0]
        tracking_id = parsed_data['tracking_id'][0]
        order_status = parsed_data['order_status'][0]
        amount = parsed_data['amount'][0]
        if order_status =='Success':
            customer_details = {
                'order_id': parsed_data.get('order_id', [])[0],
                'billing_name': parsed_data.get('billing_name', [])[0],
                'billing_address': parsed_data.get('billing_address', [])[0],
                'billing_city': parsed_data.get('billing_city', [])[0],
                'billing_state': parsed_data.get('billing_state', [])[0],
                'billing_zip': parsed_data.get('billing_zip', [])[0],
                'billing_country': parsed_data.get('billing_country', [])[0],
                'billing_tel': parsed_data.get('billing_tel', [])[0],
                'billing_email': parsed_data.get('billing_email', [])[0],
                'delivery_name': parsed_data.get('delivery_name', [])[0],
                'delivery_address': parsed_data.get('delivery_address', [])[0],
                'delivery_city': parsed_data.get('delivery_city', [])[0],
                'delivery_state': parsed_data.get('delivery_state', [])[0],
                'delivery_zip': parsed_data.get('delivery_zip', [])[0],
                'delivery_country': parsed_data.get('delivery_country', [])[0],
                'delivery_tel': parsed_data.get('delivery_tel', [])[0]
            }
 
            customer_json = json.dumps(customer_details, indent=2)

            
            order =Order.objects.get(id=order_id)
            order.payment_status = 'Completed'
            order.payment_id = tracking_id
            order.payment_amount = float(amount)
            order.payment_details = customer_json
            order.save()
            

            placeDelivery(order.id)
            send_email_receipt(request,order.id,User.objects.get(email=order.customer_email))
            smsGateway("order placed",order = order,user= User.objects.get(email=order.customer_email))
            
            
            return redirect(f'https://www.sizeupp.com/payment-success?order_id={order_id}&status={order_status}')
        else:
            order =Order.objects.get(id=order_id)
            order.payment_status = 'Failed'
            order.payment_id = tracking_id
            order.delivery_status = 'Cancelled'
            order.save()
            
            return redirect(f'https://www.sizeupp.com/payment-failed?order_id={order_id}&status={order_status}&tracking_id={tracking_id}')




