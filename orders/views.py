from articles.models import *
from articles.forms import *
from django.db import transaction
from django.utils import timezone
from django.contrib import messages
from .models import Order, CartItem
from django.http import JsonResponse
from .forms import CartForm, OrderCreateForm
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from accounts.decorators import artist_required

User = get_user_model()


# Create your views here.

@login_required
def info(request, art_pk):
    art = Art.objects.get(pk=art_pk)
    cart_form = CartForm()
    cart = CartItem.objects.filter(user_id=request.user.pk).filter(art_id=art_pk)
    
    
    offer_form = OfferForm()
    context = {
        "art": art,
        "cart_form": cart_form,
        "cart": cart,
        "content": "결제 정보 페이지",
        "offer_form": offer_form,
    }
    return render(request, "orders/info.html", context)

@login_required
# 장바구니
def mycart(request):
    cart_items = CartItem.objects.filter(user_id=request.user.pk)

    # 장바구니 총 금액
    total_price = 0
    for item in cart_items:
        total_price += item.art.price
        
    context = {
        "cart_items": cart_items,
        "total_price": total_price,
    }

    return render(request, "orders/mycart.html", context)

@login_required
# 장바구니 추가
def add_cart(request, art_pk):
    # 장바구니 담기
    art = Art.objects.get(pk=art_pk)
    try:
        cart = CartItem.objects.get(art__pk=art.pk, user__id=request.user.pk)
        # 장바구니에 해당 작품이 있으면 삭제
        if cart:
            if cart.art.title == art.title:
                cart.delete()
                in_cart = False
                
    except CartItem.DoesNotExist:
        user = User.objects.get(pk=request.user.pk)
        cart = CartItem(
            user=user,
            art=art,
        )
        cart.save()
        in_cart = True

    # context = {
    #     "in_cart": in_cart,
    #     "cart_length": cart.count(),
    # }

    return redirect("orders:mycart")

@login_required
# 장바구니 삭제
def delete_cart(request, art_pk):
    my_pick = Art.objects.get(pk=art_pk)
    my_cart = CartItem.objects.filter(user__id=request.user.pk)
    if request.method == "POST":
        target = my_cart.get(art__pk=my_pick.pk)
        target.delete()
        
        total_price_after_delete = 0
        for item in my_cart:
            total_price_after_delete += item.art.price
        
        context = {
            "artPk": art_pk,
            "total_price_after_delete" : total_price_after_delete,
        }
        return JsonResponse(context)
    else:
        messages.error(request.user.nickname, "님의 장바구니를 지울 수 없어요!")
        return redirect("orders:mycart")

@login_required
# 주문 생성
def payment(request):
    # 사용자 정보 가져오기
    data = {
        "username": request.user.nickname,
        "email": request.user.email,
        "address": request.user.location,
        "address_detail": request.user.location_detail,
    }
    # 사용자 정보 From
    payment_form = OrderCreateForm(initial=data)
    if payment_form.is_valid():
        payment_form.save()
        print(payment_form)

    
    # 장바구니 가져오기
    cart_items = CartItem.objects.filter(user_id=request.user.pk)

    # 장바구니 총 금액
    total_price = 0
    if cart_items:
        for item in cart_items:
            total_price += item.art.price

    # 배송비
    if total_price >= 30000:
        delivery_fee = 0
    else:
        delivery_fee = 3000

    billing_amount = total_price + delivery_fee
    # 주문서
    context = {
        "payment_form": payment_form,
        "cart_items": cart_items,
        "total_price": total_price,
        "delivery_fee": delivery_fee,
        "billing_amount": billing_amount,
        "data": data,
    }
    
    return render(request, "orders/payment.html", context)

@login_required
# 주문 완료
def complete(request):
    # order_pk = Order.objects.get(pk=pk)
    if request.method == 'POST':
        cart_items = CartItem.objects.filter(user__id=request.user.pk)
        # 장바구니 총 금액
        total_price = 0
        if cart_items:
            for item in cart_items:
                total_price += item.art.price

        # 배송비
        if total_price >= 30000:
            delivery_fee = 0
        else:
            delivery_fee = 3000

        billing_amount = total_price + delivery_fee

        order_form = OrderCreateForm(request.POST)
        if order_form.is_valid():
            order = order_form.save(commit = False)

        # 주문 1 : 그림 1 -> 주문 1 : 그림 N
        # 1. 주문을 먼저 생성
        # 2. 1 에서 생성한 주문(order)를 가지고(외래키), cart_items에 있는 art들을 생성
        for cart_item in cart_items:
            art = cart_item.art
            
            with transaction.atomic():
                order.user = request.user
                order.username = request.user.nickname
                order.email = request.user.email
                order.address = request.user.location
                order.address_detail = request.user.location_detail
                order.total_price = billing_amount
                order.save()
                
                art.soldout = True
                art.order = order
                art.save()
        
        
        cart_items.delete()
    else:
        pass

    order = Order.objects.last()
    art = Art.objects.filter(order__id=order.pk)
    print(art)
    context = {
        "order": order,
        "art": art,
    }
    return render(request, "orders/complete.html", context)

# 배송상태
def delivery(request, order_pk):
    order = Order.objects.get(pk=order_pk)
    order.created_at = timezone.now()
    order.order_status = "배송 준비중"
    order.save()
    return redirect("orders:order_list")


def delivery_complete(request, order_pk):
    order = Order.objects.get(pk=order_pk)
    order.created_at = timezone.now()
    order.order_status = "배송완료"
    order.save()
    return redirect("orders:order_list")

@login_required
# 주문 취소
def order_delete(request, order_pk):
    # 주문 가져오기
    order = Order.objects.get(pk=order_pk)
    # 상품 가져오기
    art = Art.objects.get(pk=order.art.pk)
    # 주문 생성 시간을 취소시간으로 업데이트
    order.created_at = timezone.now()
    with transaction.atomic():
        # soldout 표시 제거
        art.soldout = False
        art.save()

        # 배송상태 변경
        order.order_status = "취소주문"
        order.save()

        return redirect("accounts:index", request.user.pk)

@login_required
# 주문 내역 리스트
def order_list(request):
    # 결제 완료
    complete_orders = Order.objects.filter(order_status="결제완료").order_by("-created_at")
    # 취소한 주문
    cancel_orders = Order.objects.filter(order_status="취소주문").order_by("-created_at")
    # 배송 준비중
    delivery_orders = Order.objects.filter(order_status="배송 준비중").order_by(
        "-created_at"
    )
    # 배송 완료
    delivery_complete_orders = Order.objects.filter(order_status="배송완료").order_by(
        "-created_at"
    )

    context = {
        "complete_orders": complete_orders,
        "cancel_orders": cancel_orders,
        "delivery_orders": delivery_orders,
        "delivery_complete_orders": delivery_complete_orders,
    }
    return render(request, "orders/order_list.html", context)

@login_required
# 약관 동의
def agree(request):
    print(request.POST["is_checked"])
    if request.POST["is_checked"] == "true":
        is_agreed = True
    else:
        is_agreed = False
    context = {
        "is_agreed": is_agreed,
    }
    return JsonResponse(context)

@login_required
def offer(request):
    # 해당유저 정보
    user = get_user_model().objects.get(id=request.user.pk)
    # 가격제안들
    offers = Offer.objects.filter(user_id=user)

    context = {
        "offers": offers,
    }
    return render(request, "orders/offer.html", context)

@login_required
def offer_create(request, art_pk):
    art = Art.objects.get(pk=art_pk)

    if request.method == "POST":
        offer_form = OfferForm(request.POST)
        if offer_form.is_valid():
            offer = offer_form.save(commit=False)
            offer.art_id = art.pk
            offer.user = art.artist
            offer.save()

    return redirect("orders:info", art_pk)

@login_required
@artist_required
def offer_accept(request, offer_pk):
    offer_accept = get_object_or_404(Offer, pk=offer_pk)
    if int(request.POST["note_pk"]) == offer_pk:
        art_price = Art.objects.get(pk=offer_accept.art.pk)
        art_price.price = offer_accept.offer_price
        art_price.save()
    
    return redirect("orders:offer")