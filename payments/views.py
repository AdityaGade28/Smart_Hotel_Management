from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
import razorpay
from bookings.models import Booking
from .models import Payment

# Initialize Razorpay Client
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

@login_required
def checkout(request, booking_pk):
    booking = get_object_or_404(Booking, pk=booking_pk, customer=request.user)

    if hasattr(booking, 'payment') and booking.payment.status == 'completed':
        messages.info(request, 'This booking is already paid.')
        return redirect('bookings:booking_detail', pk=booking.pk)

    # 1. Create/Get Payment Object
    payment, created = Payment.objects.get_or_create(
        booking=booking,
        defaults={'amount': booking.total_price, 'status': 'pending'}
    )

    # 2. Create Razorpay Order
    amount_in_paise = int(booking.total_price * 100)
    razorpay_order = razorpay_client.order.create({
        'amount': amount_in_paise,
        'currency': 'INR',
        'payment_capture': '1'
    })
    
    payment.razorpay_order_id = razorpay_order['id']
    payment.save()

    context = {
        'booking': booking, 
        'payment': payment,
        'razorpay_order_id': razorpay_order['id'],
        'razorpay_merchant_key': settings.RAZORPAY_KEY_ID,
        'razorpay_amount': amount_in_paise,
        'callback_url': request.build_absolute_uri('/payments/verify-payment/')
    }
    return render(request, 'payments/checkout.html', context)


@login_required
@csrf_exempt
def verify_payment(request):
    if request.method == "POST":
        razorpay_payment_id = request.POST.get('razorpay_payment_id', '')
        razorpay_order_id = request.POST.get('razorpay_order_id', '')
        razorpay_signature = request.POST.get('razorpay_signature', '')
        
        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }

        try:
            # Verify the signature
            razorpay_client.utility.verify_payment_signature(params_dict)
            
            # Signature matches - complete the payment
            payment = Payment.objects.get(razorpay_order_id=razorpay_order_id)
            payment.status = 'completed'
            payment.razorpay_payment_id = razorpay_payment_id
            payment.razorpay_signature = razorpay_signature
            payment.save()
            
            booking = payment.booking
            booking.status = 'confirmed'
            booking.save()
            booking.room.is_available = False
            booking.room.save()
            
            messages.success(request, "Payment successful! Your booking is confirmed.")
            return redirect('payments:payment_success', pk=payment.pk)
        except Exception as e:
            # Signature verification failed or other error
            payment = Payment.objects.filter(razorpay_order_id=razorpay_order_id).first()
            if payment:
                payment.status = 'failed'
                payment.gateway_response = str(e)
                payment.save()
            
            messages.error(request, "Payment verification failed. Please contact support.")
            if payment:
                return redirect('payments:payment_failed', pk=payment.pk)
            return redirect('bookings:my_bookings')
    
    return redirect('bookings:my_bookings')


@login_required
def payment_success(request, pk):
    payment = get_object_or_404(Payment, pk=pk, booking__customer=request.user)
    return render(request, 'payments/payment_success.html', {'payment': payment})


@login_required
def payment_failed(request, pk):
    payment = get_object_or_404(Payment, pk=pk, booking__customer=request.user)
    return render(request, 'payments/payment_failed.html', {'payment': payment})


@login_required
def payment_history(request):
    if request.user.is_admin_user():
        payments = Payment.objects.select_related('booking__customer', 'booking__room__hotel').all()
    else:
        payments = Payment.objects.filter(
            booking__customer=request.user
        ).select_related('booking__room__hotel')
    return render(request, 'payments/payment_history.html', {'payments': payments})
