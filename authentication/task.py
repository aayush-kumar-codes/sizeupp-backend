import requests
from apscheduler.schedulers.background import BackgroundScheduler
from django.utils import timezone
from .models import Order
from django.db.models import Q

def update_order_statuses():

    orders = Order.objects.filter(Q(airwaybilno__isnull=False) & Q(order_cancel=False) & ~Q(delivery_status='Delivered'))
    print(orders)
    for order in orders:
        try:
            url = f'https://api.instashipin.com/api/ilogix/track?api_key=656593e12539bf4b675d593c&airwaybilno={order.airwaybilno}'
            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()
                print(data)
                success = data['data']['success']
                print(success,"00000")

                if success:
                    print("=============")
                    shipment_latest_status= data['data']['response'][0]['scan_detail'][-1]['status']
                    print("-----------")
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
                    
                    if shipment_latest_status == 'PICKUP CANCELLED':
                        order.delivery_status='Cancelled'
                        
                    order.instaship_delivery_status =data['data']['response'][0]['scan_detail'][-1]['status']
                    try:
                        order.expected_date = data['data']['response'][0]['edd']
                    except:
                        pass

                    order.save()
                    print(order.id)
                    print(order.delivery_status)
                    print(order.instaship_delivery_status)

        except Exception as e:
            print(f"Error updating order status for order {order.id}: {e}")

# Create a scheduler


def traking_status():
    scheduler = BackgroundScheduler({'apscheduler.job_defaults.max_instances': 5})
    # scheduler.max_instances = 5
    # Add a job that runs the update_order_statuses function every 5 minutes
    scheduler.add_job(update_order_statuses, 'interval', seconds=30)

    # Start the scheduler
    scheduler.start()
