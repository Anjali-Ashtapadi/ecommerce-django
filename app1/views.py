from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Category,Cart,CartItem, Variation
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import EmptyPage,PageNotAnInteger,Paginator
from django.db.models import Q
# Create your views here.

def homepage(request):
    products=Product.objects.all().filter(is_available=True)
    context={
        'products':products
    }
    return render(request,'homepage.html',context)

def store(request,category_slug=None):
    categories  = None
    products    = None
    if category_slug != None:
        categories    = get_object_or_404(Category,slug=category_slug)
        products      = Product.objects.filter(category=categories, is_available=True)
        paginator = Paginator(products,3)
        page=request.GET.get('page')
        paged_products=paginator.get_page(page)
        product_count =products.count()
    else:
        products=Product.objects.all().filter(is_available=True).order_by('id')
        paginator = Paginator(products,3)
        page=request.GET.get('page')
        paged_products=paginator.get_page(page)
        product_count=products.count()
    context={
        'products':paged_products,
        'product_count':product_count
        }
    return render(request,'store.html',context)

def product_detail(request,category_slug,product_slug):
    try:
        single_product=Product.objects.get(category__slug=category_slug,slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id = _cart_id(request),product=single_product).exists()
        # return HttpResponse(in_cart)
    except Exception as e:
        raise e
    context={
        'single_product':single_product,
        'in_cart':in_cart
    }
    return render(request,'product_detail.html',context)


def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def add_to_cart(request, product_id):
    product_variation=[]
    product = Product.objects.get(id=product_id)

    if request.method == 'POST':
        for item in request.POST:
            key = item
            value = request.POST[key]
            try:
                variation = Variation.objects.get(
                    product=product,
                    variation_category__iexact=key,
                    variation_values__iexact=value
                )
                product_variation.append(variation)
            except:
                pass

    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id=_cart_id(request))
    cart.save()

    is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()
    if is_cart_item_exists:
        cart_item = CartItem.objects.filter(product=product, cart=cart)
        ex_var_list = []
        product_ids = []
        for item in cart_item:
            existing_variations = item.variations.all()
            ex_var_list.append(list(existing_variations))
            product_ids.append(item.id)

        if product_variation in ex_var_list:
            index = ex_var_list.index(product_variation)
            item_id = product_ids[index]
            item = CartItem.objects.get(product=product, id=item_id)
            item.quantity += 1
            item.save()
        else:
            item = CartItem.objects.create(product=product, cart=cart, quantity=1)
            if len(product_variation) > 0:
                item.variations.clear()
                item.variations.add(*product_variation)
            item.save()
    else:
        item = CartItem.objects.create(product=product, cart=cart, quantity=1)
        if len(product_variation) > 0:
            item.variations.clear()
            item.variations.add(*product_variation)
        item.save()

    return redirect('cart')   # ✅ Always return something


def remove_cart(request,product_id,cart_item_id):
    cart = Cart.objects.get(cart_id = _cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart,id=cart_item_id)
    if cart_item.quantity>1:
        cart_item.quantity -=1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart')

def remove_total_cart(request,product_id,cart_item_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product,id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart,id=cart_item_id)
    cart_item.delete()
    return redirect('cart')

from django.core.exceptions import ObjectDoesNotExist

def cart(request, total=0, quantity=0, cart_items=None):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))   # cart_id fixed
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax =(2 * total)/100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass   # safe fallback if no cart

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax':tax,
        'grand_total': grand_total,
    }
    return render(request, 'cart.html', context)


def search(request):
    products=[]
    product_count=0
    if 'keyword' in request.GET:
        keyword_value=request.GET['keyword']
        if keyword_value:
            products=Product.objects.order_by('created_date').filter(Q(description__icontains=keyword_value)|Q(product_name__icontains=keyword_value))
            product_count=products.count()
    context={'products':products,
             'product_count':product_count
             }
    return render(request,'store.html',context)