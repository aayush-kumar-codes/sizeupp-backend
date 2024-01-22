
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




# def trackorder(billno):
#     order = Order.objects.get(airwaybilno= billno)
#     url = f'https://api.instashipin.com/api/ilogix/track?api_key=6092655223372029e7404dc4&airwaybilno={billno}'
#     response = requests.get(url)
#     if response.status_code == 200:
#         data = response.json()
#         message = data
#         success = data['data']['success']
#         if success:
#             shipment_latest_status= data['data']['response']['shipment_latest_status']
#             if shipment_latest_status == 'PENDING PICKUP':
#                 order.delivery_status='Order Processing'
                
#             if shipment_latest_status == "Out for Pickup":
#                 order.delivery_status='Packed'
                
#             if shipment_latest_status == "PICKUP DONE":
#                 order.delivery_status='Shipped'
                
#             if shipment_latest_status == "IN-TRANSIT":
#                 order.delivery_status='In-Transit'
                
#             if shipment_latest_status == "OUT FOR DELIVERY":
#                 order.delivery_status='Out For Delivery'
            
#             if shipment_latest_status == "Delivered":
#                 order.delivery_status='Delivered'
            
#             if shipment_latest_status == 'PICKUP CANCELLED':
#                 order.delivery_status='Cancelled'
                
#             try:
#                 order.expected_date = data['data']['response']['edd']
#             except:
#                 pass
#             order.save()
 
 
 

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
    

    payment_method = order.payment_type
    cod_total = "0.00"
    if payment_method == "COD":
        cod_total = str(order.payment_amount)

 
    payload = {
        "token_id": token,

            "auto_approve": "true",
            "tracking_no": "",
            "order_number": order.id,
            "transaction_ref_no": order.id,
            "payment_method": payment_method,
            "discount_total": "0.00",
            "cod_shipping_charge": "00.00",
            "invoice_total": str(order.payment_amount),
            "cod_total": cod_total,
            "length": "10",
            "breadth": "10",
            "height": "10",
            "actual_weight": total_weight,
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
            "vendor_name": "Sizeupp",
            "address_1": "Sizeupp, F-72/73, Solaris 1 Indl Estate",
            "address_2": "Opp L & T Gate No.6, Saki Vihar Rd, Powai",
            "city": "Andheri",
            "state": "Maharashtra",
            "postcode": "400072",
            "country": "India",
            "phone": "7219795490"
            },
            "rto": {
            "vendor_name": "Sizeupp",
            "address_1": "Sizeupp, F-72/73, Solaris 1 Indl Estate",
            "address_2": "Opp L & T Gate No.6, Saki Vihar Rd, Powai",
            "city": "Andheri",
            "state": "Maharashtra",
            "postcode": "400072",
            "country": "India",
            "phone": "7219795490"
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
     
    

def returnDeliveryOrder(order_id,order_items):
    headers,token = generateToken()    
    url = f'https://api.instashipin.com/api/v2/courier-vendor/reverse-book'    
    order = Order.objects.get(id=order_id)
    total_weight = 0
    items = []
    total_price = 0
    order = Order.objects.get(id=order_id)
    total_weight = 0
    items = []
    total_price = 0

    for order_item in order_items:
    #    for sqp_data in order_item.get('sqp_code', []):
            # order_item = order.order_items.filter(sqp_code=sqp_data['id']).first()
            sqp_data = SizeQuantityPrice.objects.get(id=order_item['sqp_code'])
            if order_item:
                sqp_weight = float(sqp_data.weight)
                total_weight += round(sqp_weight, 2)
                unit_price = float(order_item['mrp'])
                quantity = int(order_item['quantity'])
                total_price += round(unit_price * quantity, 2)

                items.append({
                    "name": order_item['product']['name'],
                    "quantity": str(order_item['quantity']),
                    "sku": order_item['sqp_code'],
                    "unit_price": str(order_item['mrp']),
                    "actual_weight": str(sqp_weight),
                    "item_color": "",
                    "item_size": str(order_item['size']),
                    "item_category": "",
                    "item_image": "",
                    "item_brand": ""
                })
    invoice_total = round(total_price, 2)
    payload = {
        "token_id": token,
        "order_number": order.id,
        "transaction_ref_no": order.id,
        "invoice_total": str(invoice_total),
        "qc_pickup": "n",
        "length": "10",
        "breadth": "10",
        "height": "10",
        "actual_weight": "0.2",
        "volumetric_weight": "0.50",
        "shipping": {
            "vendor_name": "Sizeupp",
            "address_1": "Sizeupp, F-72/73, Solaris 1 Indl Estate",
            "address_2": "Opp L & T Gate No.6, Saki Vihar Rd, Powai",
            "city": "Andheri",
            "state": "Maharashtra",
            "postcode": "400072",
            "country": "India",
            "phone": "7219795490"
        },
        "line_items": items,
        "pickup": {
           "first_name": order.customer_name,
            "last_name": "",
            "address_1": str(order.address_line_1),
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


    order.shipping_message = str(data) + '-----'+ str('return')

    order.save()