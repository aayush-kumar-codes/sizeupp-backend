
import requests
from SizeUpp import settings
from .models import Order, OrderItem
from product.models import SizeQuantityPrice,Product

def generateToken():
    url = 'https://api.instashipin.com/api/v1/tenancy/authToken'
    payload ={
        "api_key": 
            "656593e12539bf4b675d593c"
        }
    headers = {
            'Content-Type': 'application/json',
        }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
            data = response.json()
            token = data['data']['response']['token_id']
        
    return headers, token

def checkDelivery(pincode): 
    headers,token = generateToken()
            
    url = 'https://api.instashipin.com/api/v1/courier-vendor/freight-calculator'
    payload = {
        "token_id": settings.SHIPING_TOKEN,
        "fm_pincode": "400072",
        "lm_pincode": pincode,
        "weight": "0.5",
        "payType": "PPD",
        "collectable": ""
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        # Request was successful
        data = response.json()
        deliveryCharges = data['data']['response']['total_freight']
        return deliveryCharges
    else:
        return None




def trackorder(billno):
    order = Order.objects.get(airwaybilno= billno)
    url = f'https://api.instashipin.com/api/ilogix/track?api_key=6092655223372029e7404dc4&airwaybilno={billno}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        message = data
        success = data['data']['success']
        if success:
            shipment_latest_status= data['data']['response']['shipment_latest_status']
            if shipment_latest_status == 'PENDING PICKUP':
                order.delivery_status='Order Processing'
                
            if shipment_latest_status == "Out for Pickup":
                order.delivery_status='Packed'
                
            if shipment_latest_status == "PICKUP DONE":
                order.delivery_status='Shipped'
                
            if shipment_latest_status == "IN-TRANSIT":
                order.delivery_status='In-Transit'
                
            if shipment_latest_status == "OUT FOR DELIVERY":
                order.delivery_status='Out For Delivery'
            
            if shipment_latest_status == "Delivered":
                order.delivery_status='Delivered'
            
            if shipment_latest_status == 'PENDING PICKUP':
                order.delivery_status='Cancel'
                
            try:
                order.expected_date = data['data']['response']['edd']
            except:
                pass
            order.save()
 
 
 

def placeDelivery(order_id):
    
    
    headers,token = generateToken()    
    order = Order.objects.get(id=order_id)
    url = 'https://api.instashipin.com/api/v2/courier-vendor/external-book'
    total_weight = 0
    items = []

    for orderitem in order.order_items.all():
        sqp = SizeQuantityPrice.objects.get(id=orderitem.sqp_code)
        total_weight = round(total_weight + float(sqp.weight), 2)
        items.append(
            {
                "name": orderitem.product.name,
                "quantity": str(orderitem.quantity),
                "sku": orderitem.sqp_code,
                "unit_price": str(orderitem.mrp),  # Convert Decimal to string
                "actual_weight": str(orderitem.size),  # Convert Decimal to string
                "item_color": "",
                "item_size": str(orderitem.size),  # Convert Decimal to string
                "item_category": "",
                "item_image": "",
                "item_brand": ""
            }
        )

 
    payload = {
        "token_id": token,

            "auto_approve": "true",
            "tracking_no": "",
            "order_number": order.id,
            "transaction_ref_no": order.id,
            "payment_method": "COD",
            "discount_total": "0.00",
            "cod_shipping_charge": "00.00",
            "invoice_total": str(order.payment_amount),
            "cod_total": str(order.payment_amount),
            "length": "10",
            "breadth": "10",
            "height": "10",
            "actual_weight": "0.2",
            "volumetric_weight": "0.50",
            "shipping": {
            "first_name": order.customer_name,
            "last_name": "",
            "address_1": order.address_line_1,
            "address_2": order.address_line_2,
            "city": order.city,
            "state": order.state,
            "postcode": order.postal_code,
            "country": "India",
            "phone": order.customer_contact,
            "cust_email": order.customer_email
            },
            "line_items": items,
            "pickup": {
            "vendor_name": "Test Vendor",
            "address_1": "Demo Address, do not pick",
            "address_2": "",
            "city": "Gurgaon",
            "state": "Haryana",
            "postcode": "122016",
            "country": "India",
            "phone": "8104739401"
            },
            "rto": {
            "vendor_name": order.customer_name,
            "address_1": str(order.address_line_1)+ "Do not pick",
            "address_2": str(order.address_line_2),
            "city": order.city,
            "state": order.state,
            "postcode": order.postal_code,
            "country": "India",
            "phone": order.customer_contact
            },
            "gst_details": {
            "gst_number": "",
            "cgst": "",
            "igst": "",
            "sgst": "",
            "hsn_number": "",
            "ewaybill_number":""
            }
                }
                

    response = requests.post(url, json=payload, headers=headers)
   
    if response.status_code == 200:
        # Request was successful
        data = response.json()
        message = data
        success = data['data']['success']
        if success :
            
            airwaybilno = data['data']['response']['airwaybilno']
            courier = data['data']['response']['courier']
            dispatch_label_url = data['data']['dispatch_label_url']
            order.airwaybilno = airwaybilno
            order.courier = courier
            order.dispatch_label_url = dispatch_label_url
            # order.delivery_status= 'Order Processing'
        
        order.shipping_message = message
        order.save()
    


def cancelDelivery(billno,order_id):
    order = Order.objects.get(id=order_id)
    headers,token = generateToken()    
            # settings.SHIPING_TOKEN = token
        

    url = f'https://api.instashipin.com/api/ilogix/cancelshipment'    

    payload = {
        'token_id': token,
        'airwaybilno': billno,
        "action":"cancel"

    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        data = response.json()
        message = data['data']['success']
        if message == 'true':
            
            order.airwaybilno = ''
            order.courier = ''
            order.dispatch_label_url = ''
            order.save()
        
    order.shipping_message =  data['data']['response']
    order.save()
     
    

def returnDeliveryOrder(order_id,products):
    headers,token = generateToken()    
    url = f'https://api.instashipin.com/api/v2/courier-vendor/reverse-book'    
    order = Order.objects.get(id=order_id)
    total_weight = 0
    items = []
    total_price = 0
    for orderitem in order.order_items.filter(product__id__in = products):
        sqp = SizeQuantityPrice.objects.get(id=orderitem.sqp_code)
        total_weight = round(total_weight + float(sqp.weight), 2)
        total_price = round((float(orderitem.mrp) + total_price),2)
        items.append(
            {
                "name": orderitem.product.name,
                "quantity": str(orderitem.quantity),
                "sku": orderitem.sqp_code,
                "unit_price": str(orderitem.mrp),  # Convert Decimal to string
                "actual_weight": str(sqp.weight),  # Convert Decimal to string
                "item_color": "",
                "item_size": str(orderitem.size),  # Convert Decimal to string
                "item_category": "",
                "item_image": "",
                "item_brand": ""
            }
        )

 
    payload = {
        "token_id": token,

            "order_number": order.id,
            "transaction_ref_no": order.id,
            "invoice_total": total_price,
             "qc_pickup": "n",

            "length": "10",
            "breadth": "10",
            "height": "10",
            "actual_weight": "0.2",
            "volumetric_weight": "0.50",
            "shipping": {
            "first_name": order.customer_name,
            "last_name": "",
            "address_1": order.address_line_1,
            "address_2": order.address_line_2,
            "city": order.city,
            "state": order.state,
            "postcode": order.postal_code,
            "country": "India",
            "phone": order.customer_contact,
            "cust_email": order.customer_email
            },
            "line_items": items,
          
            "pickup": {
            "vendor_name": order.customer_name,
            "address_1": str(order.address_line_1)+ "Do not pick",
            "address_2": str(order.address_line_2),
            "city": order.city,
            "state": order.state,
            "postcode": order.postal_code,
            "country": "India",
            "phone": order.customer_contact
            },
                }
                
    response = requests.post(url, json=payload, headers=headers)
   
    if response.status_code == 200:
        # Request was successful
        data = response.json()

        success = data['data']['success']
        if success :
            
            airwaybilno = data['data']['response']['airwaybilno']
            courier = data['data']['response']['courier']
            order.airwaybilno = airwaybilno
            order.courier = courier
            order.dispatch_label_url = ''
            order.delivery_status = 'Order Return'
            order.order_return = True

        order.shipping_message = data['data']

        order.save()