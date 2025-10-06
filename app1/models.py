from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager
from django.urls import reverse
from django.utils.text import slugify
# Create your models here.

class MyAccountManager(BaseUserManager):
    def create_user(self,first_name, last_name, username, email, password=None):
        if not email:
            raise ValueError('User must have an email address')
        if not username:
            raise ValueError('User must have an username')
        
        user=self.model(
            email=self.normalize_email(email),
            username=username,
            first_name=first_name,
            last_name=last_name,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self,first_name, last_name, email, username, password):
        user=self.create_user(
            email=self.normalize_email(email),
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        user.is_admin=True
        user.is_active=True
        user.is_staff=True
        user.is_superadmin=True

        user.save(using=self._db)
        return user


class Account(AbstractBaseUser):
    first_name=models.CharField(max_length=50)
    last_name=models.CharField(max_length=50)
    email=models.EmailField(max_length=50,unique=True)
    username=models.CharField(max_length=50,unique=True)
    phone_number=models.CharField(max_length=50)

    # required
    date_joined=models.DateTimeField(auto_now_add=True)
    last_login=models.DateTimeField(auto_now_add=True)
    is_admin=models.BooleanField(default=False)
    is_staff=models.BooleanField(default=False)
    is_active=models.BooleanField(default=False)
    is_superadmin=models.BooleanField(default=False)

    USERNAME_FIELD='email'
    REQUIRED_FIELDS=['username','first_name','last_name']


    objects=MyAccountManager()
    def __str__(self):
        return self.email
    
    def has_perm(self,perm,obj=None):
        return self.is_admin
    
    def has_module_perms(self,add_label):
        return True

class Category(models.Model):
    category_name=models.CharField(max_length=100,unique=True)
    slug=models.SlugField(max_length=255,blank=True,unique=True)
    description=models.TextField(max_length=255,blank=True)
    category_image=models.ImageField(upload_to='photos/categories')


    class Meta:
        verbose_name='category'
        verbose_name_plural='categories'

    def save(self,*args,**kwargs):
        if not self.slug:
            self.slug =slugify(self.category_name)
        super().save(*args,**kwargs)

    def get_url(self):
        return reverse('product_by_category',args=[self.slug])

    def __str__(self):
        return self.category_name
    

class Product(models.Model):
    product_name    =models.CharField(max_length=200,unique=True)
    slug            =models.SlugField(max_length=200,unique=True)
    description     =models.TextField(max_length=200,blank=True)
    price           =models.IntegerField()
    images          =models.ImageField(upload_to='photos/products')
    stock           =models.IntegerField()
    is_available    =models.BooleanField(default=True)
    category        =models.ForeignKey(Category,on_delete=models.CASCADE)
    created_date    =models.DateTimeField(auto_now_add=True)
    modified_date   =models.DateTimeField(auto_now=True)

    

    def get_url(self):
        return reverse('product_detail',args=[self.category.slug,self.slug])

    def __str__(self):
        return self.product_name
    
class VariationManager(models.Manager):
    def colors(self):
        return super(VariationManager,self).filter(variation_category='color',is_active=True)
    def sizes(self):
        return super(VariationManager,self).filter(variation_category='size',is_active=True)

variation_category =(
    ('color','color'),
    ('size','size'),
)


class Variation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation_category = models.CharField(max_length=100, choices=variation_category)
    variation_values = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at =models.DateTimeField(auto_now=True)

    objects = VariationManager()
    def __str__(self):
        return self.variation_values
    
    
    
class Cart(models.Model):
    cart_id=models.CharField(max_length=200,blank=True)
    date_added=models.DateField(auto_now_add=True)

    def __str__(self):
        return self.cart_id
    
class CartItem(models.Model):
    product   = models.ForeignKey(Product,on_delete=models.CASCADE)
    variations = models.ManyToManyField(Variation,blank=True)
    cart      = models.ForeignKey(Cart,on_delete=models.CASCADE)
    quantity  = models.IntegerField()
    is_active = models.BooleanField(default=True)

    def sub_total(self):
        return self.product.price*self.quantity

    def __str__(self):
        return self.product.product_name

