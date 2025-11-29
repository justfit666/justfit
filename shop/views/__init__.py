# shop/views/__init__.py
# Re-export everything so old imports like `from shop import views` or `from shop.views import product_table`
# continue to work if you import from shop.views.*
from .auth_views import *
from .product_views import *
from .variant_views import *
from .favorite_cart_views import *
from .expense_views import *
from .credit_views import *
from .order_views import *
