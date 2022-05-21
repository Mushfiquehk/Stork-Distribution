from email.policy import default
from django.db import models
from django.urls import reverse
from django.core.validators import RegexValidator

from django.contrib.auth.models import User 

# Create your models here.
class Category(models.Model):
    """ Table for all category Name, Code and ID 
        of a category of products """
    name = models.CharField(max_length=100, db_index=True)
    category_code = models.CharField(max_length=3, unique=True)
    category_id = models.CharField(max_length=2, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    image = models.ImageField(upload_to="category_images/", default="vendor_images/default.png")

    class Meta:
        verbose_name_plural = 'categories'

    def get_absolute_url(self):
        return reverse("store:category_list", kwargs={"slug": self.slug})    

    def __str__(self):
        return str(self.name)

class Vendor(models.Model):
    """ Table contains Name, Code of vendors """
    name = models.CharField(max_length=100, db_index=True)
    vendor_id = models.CharField(max_length=2, unique=True)
    image = models.ImageField(upload_to='vendor_images/', default='vendor_images/default.png')
    
    def __str__(self):
        return str(self.name)

class Product(models.Model):
    added_by = models.ForeignKey(User, related_name="added_by", on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    vendor = models.ForeignKey(Vendor, related_name="vendor", on_delete=models.CASCADE)
    category = models.ForeignKey(Category, related_name="category", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='product_images/', default='product_images/default.png')
    product_code = models.CharField(max_length=4)
    
    price = models.DecimalField(max_digits=4, decimal_places=2)
    description = models.TextField(blank=True)
    is_featured = models.BooleanField(default=True)
    deal_price = models.DecimalField(max_digits=4, decimal_places=2, blank=True, default=99.99)

    class Meta:
        ordering = ('-created',)

    def get_absolute_url(self):
        return reverse("store:product_detail", kwargs={"pk": self.pk})
    
    def __str__(self):
        return str(self.name)

class Order(models.Model):
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    last_name = models.CharField(max_length=255)
    first_name = models.CharField(max_length=255)
    # change below to DateTimeField and then change in OrderForm in forms.py
    pickup_time = models.CharField(max_length=255)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{10,11}$', message="Phone number must be entered in the format: '1234567890'")
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True, default="9999999999")
    email = models.EmailField(max_length=254, blank=True)
    products = models.ManyToManyField(
                        Product,
                        through='OrderItem',
                        through_fields=('order', 'product'),
                        )

    class Meta:
        ordering = ('-created',)

    def get_absolute_url(self):
        return reverse("store:order_summary", kwargs={'pk': self.pk})
    
    def __str__(self):
        return str(str(self.first_name) + str(' ') + str(self.last_name))

class OrderItem(models.Model):
    product = models.ForeignKey(Product, 
                                on_delete=models.CASCADE,
                                related_name="product")
    order = models.ForeignKey(Order, 
                              on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=4, decimal_places=2)
    amount = models.DecimalField(max_digits=6, decimal_places=2)

    #class Meta:
     #   ordering = ('-order.id')
    def __str__(self):
        return str(self.pk)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    company_website = models.URLField(blank=True)
    business_proof = models.ImageField(upload_to='proofs/', blank=True)

    def __str__(self):
        return self.user.username

class Announcement(models.Model):
    description = models.CharField(max_length=255)
    image = models.ImageField(upload_to="announcements/", default="vendor_images/default.png")