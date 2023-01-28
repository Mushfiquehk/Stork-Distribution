from decimal import Decimal
from re import search

from django.urls import reverse
from django.http import HttpResponseRedirect
from django.http.response import JsonResponse
from django.template.loader import render_to_string

from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.postgres.search import SearchVector

from django.shortcuts import get_object_or_404, render

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.mail import send_mail

from store.models import Product, Category, Order, OrderItem
from store.forms import OrderForm, SearchForm, UserForm, UserProfileForm
from store.cart import Cart


def index(request):

    new_arrivals = Product.objects.filter(is_active=True).exclude(
        amount__lte=0).order_by('id').reverse()[:8]
    featured = Product.objects.filter(is_active=True).exclude(
        amount__lte=0).order_by('id')[:8]
    categories = Category.objects.all().order_by('id')

    if request.method == 'POST':
        form = SearchForm(request.POST)
        text = form['search_text'].data
        searched = Product.objects.annotate(
            search=SearchVector('name',
                                'category__name'),
        ).filter(search=text).exclude(amount__lte=0).order_by('id')
        print(text)
        categories = Category.objects.all().order_by('id')

        paginator = Paginator(searched, 28)
        page_number = request.GET.get('page', 1)

        try:
            products = paginator.page(page_number)
        except PageNotAnInteger:
            products = paginator.page(1)
        except EmptyPage:
            products = paginator.page(paginator.num_pages)

        page_obj = paginator.get_page(page_number)
        objects = len(page_obj.object_list)

        return render(request, 'store/category_list.html', context={"products": products,
                                                                    "categories": categories,
                                                                    "objects": objects,
                                                                    "page_obj": page_obj, })
    else:
        search_form = SearchForm()

    return render(request=request, template_name="index.html", context={'new_arrivals': new_arrivals,
                                                                        'featured': featured,
                                                                        'categories': categories,
                                                                        'search_form': search_form})


def category_list(request, slug):
    category = get_object_or_404(Category, slug=slug)
    filtered = Product.objects.filter(
        category=category, is_active=True).exclude(amount__lte=0).order_by('id')
    categories = Category.objects.all().order_by('id')

    paginator = Paginator(filtered, 28)
    page_number = request.GET.get('page', 1)

    try:
        products = paginator.page(page_number)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    page_obj = paginator.get_page(page_number)
    objects = len(page_obj.object_list)

    return render(request=request, template_name="store/category_list.html", context={'products': products,
                                                                                      'categories': categories,
                                                                                      'objects': objects,
                                                                                      'page_obj': page_obj})


def product_detail(request, pk):
    product = get_object_or_404(Product, id=pk)
    options = product.options.all()
    return render(request=request, template_name='store/product_detail.html', context={'product': product,
                                                                                       'options': options})


def order_summary(request, pk):
    order = get_object_or_404(Order, id=pk)
    name = order.name.username
    address = order.address
    item_list = list(OrderItem.objects.filter(order__pk=pk))
    total = sum(Decimal(item.price) * item.amount for item in item_list)
    if total < 250:
        total += 10

    confirmed = False
    if order.is_active == False:
        confirmed = True

    return render(request, 'store/order_summary.html', context={'name': name,
                                                                'address': address,
                                                                'item_list': item_list,
                                                                'confirmed': confirmed,
                                                                'total': total})


@login_required
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
            address_line_1 = form.cleaned_data['address_line_1']
            address_line_2 = form.cleaned_data['address_line_2']
            address = str(str(address_line_1) + " " + str(address_line_2))

            order = Order(email=email_address, phone_number=phone_number,
                          name=user, address=address)
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

            # email notification of order to admin
            subject = 'Order Placed! Reference # ' + str(order_id)
            message = 'A new order has been placed by ' + str(first_name) + " " + str(
                last_name) + ". Phone number: " + str(phone_number) + " Email: " + str(email_address) + "."
            html_email = render_to_string(
                'store/order_summary_admin.html',
                {
                    'name': name,
                    'item_list': item_list
                }
            )
            send_mail(
                subject,
                message,
                'mushfiquehasankhan@gmail.com',
                ['storkdistro@gmail.com',
                 'storksalesteam@gmail.com',
                'mushfiquehasankhan@gmail.com'],
                fail_silently=True,
                html_message=html_email
            )

            return HttpResponseRedirect(reverse('store:order_summary', args=[order_id]))

    else:
        form = OrderForm()

    cart_total = cart.get_total_price()
    if cart_total < 250.0:
        free_delivery = 250 - cart_total
    else:
        free_delivery = 0

    return render(request, 'store/cart.html', {'order_form': form,
                                               'total': cart_total,
                                               'left': free_delivery, })


@login_required
def update_cart(request):
    cart = Cart(request)
    cart_total = cart.get_total_price()
    free_delivery = 250 - cart_total

    if request.POST.get('action') == 'update':
        product_id = int(request.POST.get('product_id'))
        amount = int(request.POST.get('amount'))
        product = get_object_or_404(Product, id=product_id)
        cart.update(product=product, amount=amount)

    if request.POST.get('action') == 'delete':
        product_id = int(request.POST.get('product_id'))
        cart.delete(product_id=product_id)

    response = JsonResponse({'items': len(cart),
                             'total': cart_total,
                             'left': free_delivery})
    return response


def register(request):
    if request.method == "POST":
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(request.POST, request.FILES)

        if user_form.is_valid() and profile_form.is_valid():
            
            customer_name = user_form.cleaned_data['username']

            subject = 'Request: Customer Verification'
            message = 'A new customer has created and account.\n\n\t Username: {} \n\nVerification and subsequent authorization from an admin is request.\nPlease follow the link below to sign in and verify.\n\n https://storkdistro.com/admin/auth/user/ '.format(customer_name)
            send_mail(
                subject,
                message,
                'mushfiquehasankhan@gmail.com',
                ['storkdistro@gmail.com', 'storksalesteam@gmail.com', 'mushfiquehasankhan@gmail.com',],
                # ['mushfiquehasankhan@gmail.com'],
                fail_silently=False,
            )
            user = user_form.save()
            user.set_password(user.password)
            user.is_active = False

            profile = profile_form.save(commit=False)
            profile.user = user

            profile.save()
            user.save()
            profile.certificates = request.FILES['certificates']

            # login(request, user)

            return HttpResponseRedirect(reverse("store:category_list", args=["accessories"]))

    else:
        # GET forms
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render(request, 'store/registration.html', {'user_form': user_form,
                                                       'profile_form': profile_form, })


def user_login(request):
    error_message = ""

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("store:category_list", args=["accessories"]))

        else:
            # TODO: clear form for user to try again and send alert that account not found
            error_message = "Invalid credentials. Please try again, or sign up for a new account"
            return render(request=request, template_name="store/login.html", context={"error_message": error_message})

    else:
        return render(request=request, template_name="store/login.html", context={"error_message": error_message})


def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('store:home'))
