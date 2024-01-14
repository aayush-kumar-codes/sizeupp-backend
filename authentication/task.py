import requests
from apscheduler.schedulers.background import BackgroundScheduler
from django.utils import timezone
from .models import Order

def update_order_statuses():
    print('Checking ')
    orders = Order.objects.filter(airwaybilno__isnull=False,order_cancel=False,delivery_status='Delivered')

    for order in orders:
        try:
            url = f'https://api.instashipin.com/api/ilogix/track?api_key=656593e12539bf4b675d593c&airwaybilno={order.airwaybilno}'
            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()
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
                    
                    if shipment_latest_status == 'PICKUP CANCELLED':
                        order.delivery_status='Cancelled'
                        
                    order.instaship_delivery_status =data['data']['response']['shipment_latest_status']
                    try:
                        order.expected_date = data['data']['response']['edd']
                    except:
                        pass

                    order.save()

        except Exception as e:
            print(f"Error updating order status for order {order.id}: {e}")

# Create a scheduler


def traking_status():
    scheduler = BackgroundScheduler()
    # Add a job that runs the update_order_statuses function every 5 minutes
    scheduler.add_job(update_order_statuses, 'interval', seconds=10)

    # Start the scheduler
    scheduler.start()
