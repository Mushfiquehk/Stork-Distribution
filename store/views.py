from django.urls import reverse
from django.http import HttpResponseRedirect
from django.http.response import JsonResponse
from django.template.loader import render_to_string

from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail

from django.shortcuts import get_object_or_404, render

from django.core.paginator import Paginator

from store.models import Product, Category, Order, OrderItem, Announcement
from store.forms import OrderForm, UserForm, UserProfileForm
from store.cart import Cart

def index(request):

    new_arrivals = Product.objects.all()[:8]
    featured = Product.objects.all()[:8]
    categories = Category.objects.all()

    
    return render(request=request, template_name="index.html", context={'new_arrivals': new_arrivals,
                                                                        'featured': featured,
                                                                        'categories': categories})

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            print("User logged in.")
            return HttpResponseRedirect(reverse('store:all_products'))

        else:
            # also change to 
            print("Could not login")
            return HttpResponseRedirect(reverse('store:register'))

    else:
        return render(request=request, template_name="store/login.html", context={})

@login_required
def shop(request):
    categories = Category.objects.all()
    products = Product.objects.get_queryset().order_by('id')

    paginator = Paginator(products, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)


    return render(request=request, template_name="store/product_list.html", context={'categories': categories, 
                                                                                     'products': products,
                                                                                     'page_obj': page_obj})

""" Invoked by get_absolute_url method for Category """
@login_required
def category_list(request, slug):
    category = get_object_or_404(Category, slug=slug)
    filtered = Product.objects.filter(category=category)
    categories = Category.objects.all()

    paginator = Paginator(filtered, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request=request, template_name="store/category_list.html", context={'products': filtered,
                                                                                      'categories': categories,
                                                                                      'page_obj': page_obj})
@login_required
def product_detail(request, pk):
    product = get_object_or_404(Product, id=pk)
    options = product.options.all()
    return render(request=request, template_name='store/product_detail.html', context={'product': product, 
                                                                                        'options': options})


@login_required
def order_summary(request, pk):
    order = get_object_or_404(Order, id=pk)
    name = order.name.username
    item_list = list(OrderItem.objects.filter(order__pk=pk))

    confirmed = False
    if order.is_active == False:
        confirmed = True

    return render(request, 'store/order_summary.html', context={'name': name,
                                                                'item_list': item_list,
                                                                'confirmed': confirmed})   


def cart_summary(request): 
    cart = Cart(request)    
    user = request.user

    if request.method == 'POST' and user.is_authenticated:
        form = OrderForm(request.POST)
        if form.is_valid() and bool(cart):
            last_name = form.cleaned_data['last_name']
            first_name = form.cleaned_data['first_name']
            email_address = form.cleaned_data['email_address']
            phone_number = form.cleaned_data['phone_number']

            order = Order(email=email_address, phone_number=phone_number,
                          name=user,)
            order.save()
            order_id = order.id
            name = order.name.username

            for item in cart:
                product = item['product']
                price = item['price']
                amount = item['amount']
                order_item = OrderItem(product=product, amount=amount, 
                                       order=order, price=price)
                order_item.save()

            cart.empty()

            item_list = list(OrderItem.objects.filter(order__pk=order_id))

            # notify admin of order
            subject = 'NEW ORDER# ' + str(order_id)
            message = 'A new order has been placed by ' + str(first_name) + " " + str(last_name) + ". Phone number: " + str(phone_number) + " Email: " + str(email_address) + "."
            html_email = render_to_string(
                        'store\order_summary_admin.html',
                        {
                        'name': name,
                        'item_list': item_list
                        }
                    )
                    
            send_mail(
                subject, 
                message, 
                'orders@storkdistro', 
                # change to storkdistro@gmail.com
                ['mushfiquehasankhan@gmail.com'], 
                fail_silently=True,
                html_message= html_email
            )

            return HttpResponseRedirect(reverse('store:order_summary', args=[order_id]))

    else:
        form = OrderForm()

    return render(request, 'store/cart.html', {'order_form': form})


@login_required
def update_cart(request):
    cart = Cart(request)
    if request.POST.get('action') == 'update':
        product_id = int(request.POST.get('product_id'))
        amount = int(request.POST.get('amount'))
        product = get_object_or_404(Product, id=product_id)
        cart.update(product=product, amount=amount)

    if request.POST.get('action') == 'delete':
        product_id = int(request.POST.get('product_id'))
        cart.delete(product_id=product_id)

    cart_total = cart.get_total_price()
    response = JsonResponse({'items': len(cart), 'cart_total':  cart_total})
    return response


def register(request):

    registered = False

    if request.method == "POST":
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)  

        if user_form.is_valid() and profile_form.is_valid():

            user = user_form.save()
            user.set_password(user.password)
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user

            # remove this, or use to store something useful
            if 'certificates' in request.FILES:
                profile.certificates = request.FILES['certificates']

            profile.save()

            registered = True

        else:

            print(user_form.errors, profile_form.errors)

    else:
        # GET request
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render(request, 'store/registration.html', {'user_form': user_form,
                                                        'profile_form': profile_form,
                                                        'registered': registered})

@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('store:home'))

def contact(request):
    return render(request, template_name="contact.html")