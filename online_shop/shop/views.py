import datetime
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from .forms import SignUpForm, ReviewForm, NumberForm
from django.contrib.auth import get_user_model
from django.contrib.auth import login
from .models import Category, Product, Paper, Review, Cart, CartFullness, Order, OrderFullness
import urllib.parse


def product_view(request, name):
    template = 'shop/product_detail.html'
    product = get_object_or_404(Product, slug=name)
    is_review_exist = False
    if request.user.is_authenticated:
        user = request.user
        review = Review.objects.filter(user=user, product=product).first()
        if review:
            is_review_exist = True

    context = {
        'product': product,
        'is_review_exist': is_review_exist,
        'reviews': product.reviews.all(),
        'ordered': False,
        'maincategories': Category.objects.filter(subcategory_number__gt=0),
        'subcategories': Category.objects.filter(parent_category_id__gt=0),
        'categories': Category.objects.filter(subcategory_number=0, parent_category_id=0)
    }
    if request.method == 'POST':
        if 'Cart' in request.POST:
            # put products to cart
            context['review_form'] = ReviewForm()
            form = NumberForm(request.POST)
            if form.is_valid():
                cart = Cart.objects.filter(user=user).first()
                if not cart:
                    cart = Cart.objects.create(user=user)
                cart.products.add(product)
                cart_fullness = CartFullness.objects.filter(cart=cart, product=product).first()
                cart_fullness.quantity += form.cleaned_data.get('quantity')
                cart_fullness.save()
                context['ordered'] = True
                context['count_form'] = NumberForm
            else:
                context['count_form'] = form
        else:
            # publish review
            form = ReviewForm(request.POST)
            context['count_form'] = NumberForm()
            if form.is_valid():
                frm = form.save(commit=False)
                frm.product = product
                frm.user = user
                frm.save()
                assesment = form.cleaned_data.get('rating')
                rating = product.rating
                rat_num = product.rat_number + 1
                product.rat_number += rat_num
                product.rating = (rating * (rat_num - 1) + assesment) / rat_num
                product.save()
                context['is_review_exist'] = True
            else:
                context['review_form'] = form
    else:
        context['review_form'] = ReviewForm()
        context['count_form'] = NumberForm()

    return render(request, template, context)


def category_view(request, name):
    template = 'shop/category.html'
    category = get_object_or_404(Category, slug=name)
    current_page_num = int(request.GET.get('page', 1))
    products = Product.objects.filter(category=category)
    paginator = Paginator(products, 6, 2)
    current_page = paginator.page(current_page_num)
    if current_page.has_next():
        params = urllib.parse.urlencode({'page': current_page_num + 1})
        next_page_url = "?%s" % params
    else:
        next_page_url = None
    if current_page.has_previous():
        params = urllib.parse.urlencode({'page': current_page_num - 1})
        prev_page_url = "?%s" % params
    else:
        prev_page_url = None
    context = {
        'maincategories': Category.objects.filter(subcategory_number__gt=0),
        'subcategories': Category.objects.filter(parent_category_id__gt=0),
        'categories': Category.objects.filter(subcategory_number=0, parent_category_id=0),
        'category_item': category,
        'subcategories_for_item': Category.objects.filter(parent_category_id=category.id),
        'products': current_page.object_list,
        'current_page': current_page_num,
        'prev_page_url': prev_page_url,
        'next_page_url': next_page_url,
    }
    return render(request, template, context)


def cart_view(request):
    template = 'shop/cart.html'
    user = request.user
    context = {
        'maincategories': Category.objects.filter(subcategory_number__gt=0),
        'subcategories': Category.objects.filter(parent_category_id__gt=0),
        'categories': Category.objects.filter(subcategory_number=0, parent_category_id=0),
        'ordered': False
    }
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=user).first() or None
        cart_sum = 0
        if cart:
            if request.method == 'POST':
                if 'Order' in request.POST:
                    context['ordered'] = True
                    order = Order.objects.create(
                        user=user,
                        date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    )
                    for product in cart.products.all():
                        order.products.add(product)
                        orderfull = OrderFullness.objects.filter(order=order, product=product).first()
                        cartfull = CartFullness.objects.filter(cart=cart, product=product).first()
                        orderfull.quantity = cartfull.quantity
                        orderfull.save()
                    cart.products.clear()
                    cart.save()
                else:
                    for product in cart.products.all():
                        cartfull = CartFullness.objects.filter(cart=cart, product=product).first()
                        if f'minus{product.slug}' in request.POST:
                            cartfull.quantity -= 1
                            cartfull.save()
                            if cartfull.quantity == 0:
                                cart.products.remove(product)
                                cart.save()
                        elif f'plus{product.slug}' in request.POST:
                            cartfull.quantity += 1
                            cartfull.save()
                        cart_sum += cartfull.quantity * product.price
            else:
                if cart.is_empty:
                    pass
                else:
                    products = cart.products.all()
                    for product in products:
                        cartfull = CartFullness.objects.filter(cart=cart, product=product).first()
                        cart_sum += cartfull.quantity * product.price
        else:
            cart = Cart.objects.create(user=user)
        context['cart'] = cart
        context['sum'] = cart_sum

    return render(request, template, context)


def home(request):
    template_name = 'shop/index.html'
    maincategories = Category.objects.filter(subcategory_number__gt=0)
    subcategories = Category.objects.filter(parent_category_id__gt=0)
    categories = Category.objects.filter(subcategory_number=0, parent_category_id=0)
    papers = Paper.objects.prefetch_related('products', 'categories')
    context = {
        'papers': papers,
        'maincategories': maincategories,
        'subcategories': subcategories,
        'categories': categories
    }
    return render(
        request,
        template_name,
        context
    )


def signup(request):
    context = {}
    if request.method == 'POST':

        form = SignUpForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password1')
            user = get_user_model().objects.create_user(
                username=email, password=password
            )
            login(request, user)
            return redirect("/")
        else:
            context['form'] = form
    else:
        context['form'] = SignUpForm()

    return render(
        request,
        'registration/signup.html',
        context
    )
