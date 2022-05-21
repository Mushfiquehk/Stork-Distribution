from store.models import Product
from decimal import Decimal 

class Cart():
    """
    Cart to store ids of items added to cart during a session
    """
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('cart-key')
        if 'cart-key' not in request.session:
            cart = self.session['cart-key'] = {}
        self.cart = cart
    
    def update(self, product, amount):
        """ 
        Adding and updating the users cart session data
        """
        product_id = str(product.id)

        self.cart[product_id] = {'price': str(product.price),
                                 'amount': amount,}

        self.session.modified = True

    def delete(self, product_id):
        """ 
        Delete item from session data
        """
        product_id = str(product_id)

        if product_id in self.cart:
            del self.cart[product_id]

        self.session.modified = True

    def empty(self):
        self.session['cart-key'] = {}
        self.session.modified = True
    
    def __iter__(self):
        """ Collect the product_id in the session data to query 
        the database and return products which is added to the 
        session data """
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        cart = self.cart.copy()

        for product in products:
            cart[str(product.id)]['product'] = product

        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['amount']
            yield item


    def __len__(self):
        """ Number of items in cart """
        cart_items = 0
        for _ in self.cart.values():
            cart_items += 1

        return cart_items

    def get_total_price(self):
        return sum(Decimal(item['price']) * item['amount'] for item in self.cart.values())