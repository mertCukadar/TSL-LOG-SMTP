from django.shortcuts import render
from django.core.mail import send_mail
# Create your views here.




def send_email(request):
    subject = 'Test Email'
    message = 'Bu bir test e-postasıdır.'
    from_email = 'your_email@gmail.com'
    recipient_list = ['recipient@example.com']  # Alıcı e-posta adresleri

    send_mail(subject, message, from_email, recipient_list)
