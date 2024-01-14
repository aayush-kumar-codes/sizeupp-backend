import requests


def smsGateway(status,order=None,user=None,otp=None,percentage= None):
    api_key = "d8dd3f-5440ad-b73fa9-23333c-80ab49"
    sender = "SZEUPP"
    if order :
        order_cancel_message = f'Dear {user.first_name}, your order {order.id} has been cancelled. If you need assistance, please contact our customer support team. Thank you for choosing Sizeupp!'
        order_return_message = f'Dear {user.first_name}, your return request for order {order.id} has been initiated. Our team will review it shortly. Thank you for choosing Sizeupp!'
        order_placed_message = f'Dear {user.first_name}, Your order ID {order.id} has been successfully placed. Thank you for choosing Sizeupp!'
        api_key = "aaad5c-efc2cd-0267d6-33bc16-c1994c"
        sender ="SZEUPP"
        
    account_created_message = f'Dear {user.first_name}, Welcome to Sizeupp! Your account has been successfully created. Start shopping now for the latest fashion trends. Thank You!'
    if otp :
        register_otp_message = f'Dear {user.first_name}, Welcome to Sizeupp! Your OTP for creating your account is: {otp}. Use it to verify your account. Happy shopping!'
        
    if percentage : 
        promotional = f'Introducing Sizeupp - Only Plus Size Fashion Brand offering UNBEATABLE QUALITY. Enjoy {percentage} off your first order! #SizeuppyourStyle https://www.sizeupp.com'
        api_key = "db481e-ee7e39-a98882-9b9a80-0ab6e4"
        sender= "584015"
        
    if status == "order cancel" :
        template = order_cancel_message
    elif status == 'order return' : 
        template = order_return_message
    elif status == 'order placed' : 
        template = order_placed_message
    elif status == "account created":
        template = account_created_message
    elif status == "register otp":
        template = register_otp_message
    elif status == "promotional" : 
        template = promotional
    
    
    
    # url = 'https://api.pinnacle.in/index.php/sms/urlsms?sender=123456&numbers=9082363252&messagetype=TXT&message=This is the test essage&response=Y&apikey=d8dd3f-5440ad-b73fa9-23333c-80ab49&dltentityid=12345&dlttempid=12345678901'

    url =f'https://api.pinnacle.in/index.php/sms/urlsms?sender={sender}&numbers={user.phone}&messagetype=TXT&message={template}&response=Y&apikey=Y&apikey={api_key}'

    headers = {
                'apikey':'d8dd3f-5440ad-b73fa9-23333c-80ab49',
                'Content-Type': 'application/x-www-form-urlencoded',
            }

    respose = requests.get(url,headers=headers)

    print(respose.json())
    
    
