from django.db import models
from django.contrib.auth.models import AbstractUser
from pytils.translit import slugify

RATING_CHOISES = [
    (1, '1'),
    (2, '2'),
    (3, '3'),
    (4, '4'),
    (5, '5')
]


class User(AbstractUser):
    username = models.CharField(max_length=64, unique=True)
    password = models.CharField(max_length=64)


class Category(models.Model):
    name = models.CharField(max_length=64, verbose_name='Название')
    slug = models.CharField(max_length=64, verbose_name='Ссылка', null=True, blank=True)
    subcategory_number = models.PositiveIntegerField(default=0, verbose_name='Количество подкатегорий')
    parent_category_id = models.PositiveIntegerField(default=0, verbose_name='Родительская категория')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ('parent_category_id',)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        self.subcategory_number = Category.objects.filter(parent_category_id=self.id).count()
        if self.subcategory_number:
            self.parent_category_id = 0
        else:
            parent_cat = Category.objects.filter(id=self.parent_category_id).first() or None
            if not parent_cat:
                self.parent_category_id = 0
            elif parent_cat.parent_category_id:
                self.parent_category_id = parent_cat.parent_category_id
                #parent_cat = Category.objects.filter(id=self.parent_category_id).first() or None
                parent_cat.save()
            else:
                parent_cat.save()
        super().save(*args, **kwargs)


class Product(models.Model):
    name = models.CharField(max_length=150, verbose_name='Наименование товара')
    slug = models.CharField(null=True, max_length=150, verbose_name='Ссылка')
    price = models.PositiveIntegerField(verbose_name='Цена', default=0)
    quantity = models.PositiveIntegerField(verbose_name='Остаток', default=0)
    category = models.ForeignKey(Category, verbose_name='Категория', related_name='products', on_delete=models.CASCADE)
    description = models.TextField(verbose_name='Описание', null=True)
    rating = models.FloatField(verbose_name='Средняя оценка', default=0)
    rat_number = models.PositiveIntegerField(verbose_name='Количество оценок', default=0)
    image = models.ImageField(null=True, blank=True, verbose_name='Изображение')

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ('-id',)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Paper(models.Model):
    title = models.CharField(max_length=150, verbose_name='Заголовок')
    text = models.TextField(verbose_name='Текст')
    products = models.ManyToManyField(Product, related_name='papers', verbose_name='Товары', blank=True)
    categories = models.ManyToManyField(Category, related_name='papers', verbose_name='Категории', blank=True)

    class Meta:
        verbose_name = 'Статья'
        verbose_name_plural = 'Статьи'
        ordering = ('-id',)

    def __str__(self):
        return self.title

    def without_products(self):
        if not self.products.count():
            return True
        return False

    without_products.short_description = 'Нет привязанных продуктов'

    def without_categories(self):
        if not self.categories.count():
            return True
        return False

    without_categories.short_description = 'Нет привязанных статей'


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name='Пользователь')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар', related_name='reviews')
    text = models.TextField(verbose_name='Текст отзыва')
    rating = models.PositiveIntegerField(verbose_name='Оценка', choices=RATING_CHOISES, default=5)

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ('-id',)

    def __str__(self):
        return self.text


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Покупатель')
    products = models.ManyToManyField(Product, verbose_name='Товары', related_name='carts', through='CartFullness')

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'
        ordering = ('-id',)

    @property
    def is_empty(self):
        if not self.products.count():
            return True
        return False


class CartFullness(models.Model):
    cart = models.ForeignKey(Cart, verbose_name='Корзина', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, verbose_name='Товар', related_name='fullness', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(verbose_name='Количество единиц', default=0)

    def save(self, *args, **kwargs):
        if self.quantity > self.product.quantity:
            self.quantity = self.product.quantity
        super().save(*args, **kwargs)

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Покупатель')
    products = models.ManyToManyField(Product, verbose_name='Товары', related_name='orders', through='OrderFullness')
    status = models.BooleanField(default=True, verbose_name='Новый заказ')
    date = models.DateTimeField(verbose_name='Дата заказа')

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ('-date',)


    def count(self):
        count = 0
        for product in self.products.all():
            count += OrderFullness.objects.filter(order=self, product=product).first().quantity
        return count

    count.short_description = 'Количество позиций'


class OrderFullness(models.Model):
    order = models.ForeignKey(Order, verbose_name='Заказ', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, verbose_name='Товар', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(verbose_name='Количество единиц', default=0)
    class Meta:
        verbose_name = 'Подробности заказа'
        verbose_name_plural = 'Подробности заказа'
