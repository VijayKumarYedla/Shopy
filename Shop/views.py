from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
import uuid
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import FormView
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import FormView
from django.contrib.auth import login
from django.contrib import messages
from .forms import Signup_Form, SearchForm
from.models import Category, Brand, Products, Cart, CartItem, Order, OrderItem
from django.contrib.auth.models import User
from django.views.generic import TemplateView, ListView, DetailView
from django.contrib.auth.views import LoginView

# Create your views here.

class Landing_page(TemplateView):
    template_name = '00_landing_page.html'
    
class Login_Page(LoginView):
    template_name = '01_login_page.html' # render login page
    redirect_authenticated_user = False # redirect authenticated users to home page
    next_page = reverse_lazy('home_page') # redirect authenticated users to home page

class Signup_View(FormView):
    template_name = '02_signup_page.html' # render signup page
    form_class = Signup_Form # render signup form
    success_url = reverse_lazy('home_page') # redirect to home page after signup

    def form_valid(self, form): # override form_valid method to save user to database
        user = form.save() # save user to database
        login(self.request, user) # login user
        return super().form_valid(form) # redirect to home page
    
class HomePage(TemplateView):
    template_name = '03_home_page.html'

    def get_context_data(self, **kwargs): # override get_context_data method to get user data
        context = super().get_context_data(**kwargs) # get context data from parent class
        context['username'] = self.request.user.username if self.request.user.is_authenticated else 'Guest' # get username from request
        context['categories'] = Category.objects.all()
        return context 

# Views for displaying all the categories in the ahop
class Category_List(View):
    template_name = '04_category_list.html'

    def get(self, request, *args, **kwargs): # override get method to get category data
        categories = Category.objects.all() # get all categories from database
        return render(request, '04_category_list.html', {'categories': categories}) # render category list page

# Views for displying the brands in the category
class Brand_List(View):
    template_name = '05_brand_list.html'

    def get(self, request, category_id, *args, **kwargs):
        category = get_object_or_404(Category, id=category_id)
        brands = Brand.objects.filter(category=category)
        return render(request, self.template_name, {'category': category, 'brands': brands})
    
# Views for displaying products in brands
class Product_List(ListView):
    model = Products
    template_name = '06_product_list.html'  # Ensure this template exists
    context_object_name = 'products'
    paginate_by = 10  # Number of products per page

    def get_queryset(self):
        # Get the brand_id from the URL
        brand_id = self.kwargs.get('brand_id')
        
        if brand_id:
            # Filter products by the given brand_id
            return Products.objects.filter(brand__id=brand_id)
        
        # If no brand_id is provided, return all products or an empty queryset
        return Products.objects.all()  # This will show all products if no filter is applied


class CategoryBrandView(DetailView):
    model = Category
    template_name = '05_brand_list.html'
    context_object_name = 'category'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.get_object()
        brands = Brand.objects.filter(category=category)
        print("Brands:", brands)  # Debugging line
        context['brands'] = brands
        return context

class AddToCart(View):
    def post(self, request, product_id):
        if not request.user.is_authenticated:
            return redirect('login')  # Redirect to the login page if the user is not authenticated

        # Get the product or return a 404 if not found
        product = get_object_or_404(Products, id=product_id)

        # Get or create the cart for the authenticated user
        cart, created = Cart.objects.get_or_create(user=request.user)

        # If the cart was just created, ensure it has a unique cart_id
        if created:
            cart.cart_id = str(uuid.uuid4())  # Generate a unique cart_id
            cart.save()

        # Add the product to the cart
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

        if not created:
            cart_item.quantity += 1  # Increment quantity if the item already exists in the cart
        cart_item.save()
        return redirect('view_cart')

                

class ViewCartView(View):
    def get(self, request):
        try:
            # Get the cart for the current user
            cart = Cart.objects.get(user=request.user)
            cart_items = CartItem.objects.filter(cart=cart)
        except Cart.DoesNotExist:
            cart_items = []  # Return an empty cart if no cart exists for the user
            total_price = 0
        else:
            # Calculate the total price for all items in the cart
            total_price = sum(item.product.price * item.quantity for item in cart_items)

        # Ensure render is called with a proper response object
        return render(request, '08_cart_view.html', {'cart_items': cart_items, 'total_price': total_price})

class RemoveFromCart(View):
    def post(self, request, product_id):
        if not request.user.is_authenticated:
            return redirect('login')  # Redirect to the login page if the user is not authenticated

        # Get the user's cart
        cart = get_object_or_404(Cart, user=request.user)

        # Get the cart item or return a 404 if not found
        cart_item = get_object_or_404(CartItem, cart=cart, product__id=product_id)

        # Remove the item from the cart
        cart_item.delete()

        return redirect('view_cart')  # Redirect to the cart view

class UpdateCartView(View):
    def post(self, request, product_id):
        # Get the cart item or return 404 if not found
        cart_item = get_object_or_404(CartItem, product__id=product_id, user=request.user)
        
        # Get the new quantity from the form data
        new_quantity = int(request.POST.get('quantity', 1))
        
        if new_quantity > 0:
            cart_item.quantity = new_quantity  # Update quantity
            cart_item.save()
        else:
            cart_item.delete()  # Remove item if quantity is set to 0
        
        # Redirect to cart view
        return redirect('view_cart')

class PlaceOrderView(View):
    def post(self, request, product_id=None):
        if not request.user.is_authenticated:
            return redirect('login')  # Redirect to login if not authenticated

        if product_id:
            # Get the product being ordered
            product = get_object_or_404(Products, id=product_id)

            # Get the user's cart, or create one if it doesn't exist
            cart, created = Cart.objects.get_or_create(user=request.user)

            # Add the product to the cart if it's not already in the cart
            cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

            if not created:  # If product is already in the cart, you may want to increase its quantity
                cart_item.quantity += 1
                cart_item.save()

            # Get the cart items again, as a new product may have been added

            cart_items = CartItem.objects.filter(cart=cart)

            if not cart_items.exists():
                return redirect('view_cart')  # Redirect if cart is empty

            # Calculate total price
            total_price = sum(item.product.price * item.quantity for item in cart_items)

            # Create the order
            order = Order.objects.create(user=request.user, total_price=total_price)

            # Create order items
            for item in cart_items:
                if item.product:

                    print(f"Creating OrderItem for product: {item.product.name}")


                    OrderItem.objects.create(
                        order=order, 
                        product=item.product, 
                        quantity=item.quantity, 
                        price=item.product.price
                    )

                else:
                    print(f"Skipping OrderItem creation for item {item.id} due to missing product")



            # Clear the cart after placing the order
            cart_items.delete()

            return redirect('order_success')  # Redirect to a success page
        else:
            # Get the user's cart
            cart = get_object_or_404(Cart, user=request.user)

            # Get the cart items
            cart_items = CartItem.objects.filter(cart=cart)

            if not cart_items.exists():
                return redirect('view_cart')  # Redirect if cart is empty

            # Calculate total price
            total_price = sum(item.product.price * item.quantity for item in cart_items)

            # Create the order
            order = Order.objects.create(user=request.user, total_price=total_price)

            # Create order items
            for item in cart_items:
                if item.product:

                    print(f"Creating OrderItem for product: {item.product.name}")


                    OrderItem.objects.create(
                        order=order, 
                        product=item.product, 
                        quantity=item.quantity, 
                        price=item.product.price
                    )

                else:
                    print(f"Skipping OrderItem creation for item {item.id} due to missing product")



            # Clear the cart after placing the order
            cart_items.delete()

            return redirect('order_success')  # Redirect to a success page


class OrderSuccessView(View):
    def get(self, request):
        return render(request, '09_order_success.html')
    
class SearchResultsView(View):
    template_name = '10_search_results.html'  # Create this template


    def get(self, request):
        form = SearchForm()
        query = request.GET.get('query')  # Get the search query from the URL
        results = Products.objects.none()  # Default to an empty queryset

        if query:
            # Filter products based on the search query
            results = Products.objects.filter(name__icontains=query)


        return render(request, '10_search_results.html', {'form': form, 'results': results, 'query': query})
    
class MyOrdersView(LoginRequiredMixin, ListView):
    model = Order
    template_name = '11_my_orders.html'  # Specify your template name
    context_object_name = 'orders'  # Name of the context variable to be used in the template

    def get_queryset(self):
        # Filter orders for the logged-in user
        return Order.objects.filter(user=self.request.user).order_by('-order_date')

    
@login_required
def change_password(request):
    if request.method == 'POST':
        form = SetPasswordForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your password has been successfully updated.')
            return redirect('home_page')  # Replace 'home_page' with your desired redirect URL
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = SetPasswordForm(user=request.user)  # Pass the logged-in user to the form

    return render(request, '12_change_password.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('landing_page') 

