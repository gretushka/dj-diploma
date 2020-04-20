from django.contrib import admin
from .models import Category, Product, Paper, Review, Cart, CartFullness, Order, OrderFullness, User
from .forms import PaperAdminForm, ProductAdminForm
from django.forms import BaseInlineFormSet


class OrderFullnessInlineFormset(BaseInlineFormSet):
    pass


#class CartFullnessInlineFormset(BaseInlineFormSet):
#    pass


class OrderFullnessInline(admin.TabularInline):
    model = OrderFullness
    formset = OrderFullnessInlineFormset


#class CartFullnessInline(admin.TabularInline):
#    model = CartFullness
#    formset = CartFullnessInlineFormset


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'subcategory_number', 'parent_category_id')
    list_filter = ['name', 'parent_category_id']
    search_fields = ('name',)


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'price', 'quantity', 'category', 'description', 'image')
    list_filter = ['name', 'category', 'price', 'quantity']
    search_fields = ('name', 'category')
    form = ProductAdminForm


class PaperAdmin(admin.ModelAdmin):
    list_display = ('title', 'text', 'get_products', 'without_products', 'get_categories', 'without_categories')
    search_fields = ('title',)
    form = PaperAdminForm

    def get_products(self, obj):
        return "\n".join([str(p) for p in obj.products.all()])

    def get_categories(self, obj):
        return "\n".join([str(p) for p in obj.categories.all()])


class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'date', 'count')
    list_filter = ['status', 'date']
    search_fields = ('user', 'status',)
    inlines = [OrderFullnessInline]


#class CartAdmin(admin.ModelAdmin):
#    list_display = ('id', 'user',)
#    inlines = [CartFullnessInline]


class ReviewAdmin(admin.ModelAdmin):
    list_display = ('text', 'rating')


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'password')


admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Paper, PaperAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Review, ReviewAdmin)
#admin.site.register(Cart, CartAdmin)
admin.site.register(User, UserAdmin)
