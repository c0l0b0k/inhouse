from django.shortcuts import render, get_object_or_404
from .models import Product, Category, Brand
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from .models import Feedback


def index(request):
    categories = Category.objects.all()  # Получаем все категории
    brands = Brand.objects.all()  # Получаем все бренды
    return render(request, 'main/index.html', {'categories': categories, 'brands': brands})


def catalog(request, category_id):
    category_instance = Category.objects.get(id=category_id)
    products = Product.objects.filter(category=category_instance)

    # Поиск
    search_query = request.GET.get('q')
    if search_query:
        products = products.filter(name__icontains=search_query)

    # Фильтрация по бренду
    brand_filter = request.GET.get('brand')
    if brand_filter:
        products = products.filter(brand__name=brand_filter)

    # Фильтрация по наличию
    stock_filter = request.GET.get('in_stock')
    if stock_filter == 'on':
        products = products.filter(in_stock=True)

    # Сортировка
    sort_by = request.GET.get('sort')
    if sort_by == 'price':
        products = products.order_by('price')
    elif sort_by == 'name':
        products = products.order_by('name')

    # Только бренды, у которых есть товары в этой категории
    brands = Brand.objects.filter(product__category=category_instance).distinct()

    return render(request, 'main/catalog.html', {
        'products': products,
        'category': category_instance,
        'brands': brands,
    })


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'main/product_detail.html', {'product': product})


def contact_view(request):
    print("работает")
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        # Сохраняем данные в базе данных
        Feedback.objects.create(name=name, email=email, message=message)

        # Можешь отправить уведомление в Telegram через API, например, используя python-telegram-bot

        return JsonResponse({'status': 'success'})

    return render(request, 'contact.html')

