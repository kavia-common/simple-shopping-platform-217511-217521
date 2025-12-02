from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint
from marshmallow import Schema, fields, validate
from ..models import (
    list_products, get_product, signup, login,
    get_cart, add_to_cart, update_cart_item, remove_from_cart,
    create_order_from_cart, get_order, get_user_id_from_token,
    list_categories, get_category_by_id, get_category_by_slug
)

blp_api = Blueprint(
    "Shopping API",
    "shopping",
    url_prefix="/api",
    description="Products, cart, orders and authentication endpoints"
)

# Schemas for request/response validation and docs
class ProductSchema(Schema):
    id = fields.String(required=True, description="Product ID")
    name = fields.String(required=True, description="Product name")
    price = fields.Float(required=True, description="Product price")
    description = fields.String(required=True, description="Product description")
    image = fields.String(required=True, description="Image URL")
    category_id = fields.String(required=False, description="Category ID")

class CategorySchema(Schema):
    id = fields.String(required=True, description="Category ID")
    name = fields.String(required=True, description="Category name")
    slug = fields.String(required=True, description="URL slug for the category")

class SignupSchema(Schema):
    email = fields.Email(required=True, description="User email")
    password = fields.String(required=True, load_only=True, description="Password (min 6)", validate=validate.Length(min=6))

class LoginSchema(Schema):
    email = fields.Email(required=True, description="User email")
    password = fields.String(required=True, load_only=True, description="Password")

class AuthResponseSchema(Schema):
    token = fields.String(required=True, description="Bearer token")
    user = fields.Dict(required=True, description="User object")

class AddCartItemSchema(Schema):
    product_id = fields.String(required=True, description="Product ID")
    quantity = fields.Integer(required=True, description="Quantity", validate=validate.Range(min=1))

class UpdateCartItemSchema(Schema):
    product_id = fields.String(required=True, description="Product ID")
    quantity = fields.Integer(required=True, description="Quantity (<=0 to remove)")

class CartItemSchema(Schema):
    product = fields.Nested(ProductSchema, required=True)
    quantity = fields.Integer(required=True)
    line_total = fields.Float(required=True)

class CartSchema(Schema):
    items = fields.List(fields.Nested(CartItemSchema), required=True)
    subtotal = fields.Float(required=True)

class OrderSchema(Schema):
    id = fields.String(required=True)
    user_id = fields.String(required=True)
    items = fields.List(fields.Nested(CartItemSchema), required=True)
    subtotal = fields.Float(required=True)
    status = fields.String(required=True)
    created_at = fields.Integer(required=True)

def _auth_user_id():
    """Extract user_id from Bearer token; return None if invalid/missing."""
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        token = auth.split(" ", 1)[1].strip()
    else:
        token = None
    return get_user_id_from_token(token)

@blp_api.route("/products")
class ProductsList(MethodView):
    """List all products or filter by category."""
    @blp_api.response(200, ProductSchema(many=True))
    def get(self):
        """List products
        ---
        summary: List products
        description: Returns products, optionally filtered by category id (?category_id=ID) or slug (?category=slug).
        tags:
          - Products
        """
        category_id = request.args.get("category_id")
        category_slug = request.args.get("category")
        return list_products(category_id=category_id, category_slug=category_slug)

@blp_api.route("/products/<string:product_id>")
class ProductDetail(MethodView):
    """Get a single product by id."""
    @blp_api.response(200, ProductSchema)
    def get(self, product_id):
        """Get product details
        ---
        summary: Get product details
        description: Returns details for a product by id.
        tags:
          - Products
        responses:
          404:
            description: Product not found
        """
        prod = get_product(product_id)
        if not prod:
            return {"message": "Product not found"}, 404
        return prod

@blp_api.route("/categories")
class CategoriesList(MethodView):
    """List categories."""
    @blp_api.response(200, CategorySchema(many=True))
    def get(self):
        """List categories
        ---
        summary: List categories
        description: Returns all available categories.
        tags:
          - Categories
        """
        return list_categories()

@blp_api.route("/categories/<string:category_id>")
class CategoryDetail(MethodView):
    """Get category by id."""
    @blp_api.response(200, CategorySchema)
    def get(self, category_id):
        """Get category
        ---
        summary: Get category
        description: Returns category details by ID.
        tags:
          - Categories
        responses:
          404:
            description: Not found
        """
        cat = get_category_by_id(category_id)
        if not cat:
            return {"message": "Not found"}, 404
        return cat

@blp_api.route("/categories/slug/<string:slug>")
class CategoryDetailBySlug(MethodView):
    """Get category by slug."""
    @blp_api.response(200, CategorySchema)
    def get(self, slug):
        """Get category by slug
        ---
        summary: Get category by slug
        description: Returns category details by slug.
        tags:
          - Categories
        responses:
          404:
            description: Not found
        """
        cat = get_category_by_slug(slug)
        if not cat:
            return {"message": "Not found"}, 404
        return cat

@blp_api.route("/auth/signup")
class Signup(MethodView):
    """Signup new user."""
    @blp_api.arguments(SignupSchema)
    @blp_api.response(201, AuthResponseSchema)
    def post(self, payload):
        """Signup
        ---
        summary: Signup
        description: Create a new user account and return token.
        tags:
          - Auth
        responses:
          400:
            description: Email already registered
        """
        try:
            return signup(payload["email"], payload["password"]), 201
        except ValueError as e:
            return {"message": str(e)}, 400

@blp_api.route("/auth/login")
class Login(MethodView):
    """Login existing user."""
    @blp_api.arguments(LoginSchema)
    @blp_api.response(200, AuthResponseSchema)
    def post(self, payload):
        """Login
        ---
        summary: Login
        description: Authenticate and return token.
        tags:
          - Auth
        responses:
          400:
            description: Invalid credentials
        """
        try:
            return login(payload["email"], payload["password"])
        except ValueError as e:
            return {"message": str(e)}, 400

@blp_api.route("/cart")
class Cart(MethodView):
    """Get current user's cart."""
    @blp_api.response(200, CartSchema)
    def get(self):
        """Get cart
        ---
        summary: Get cart
        description: Returns the authenticated user's cart.
        tags:
          - Cart
        responses:
          401:
            description: Unauthorized
        """
        user_id = _auth_user_id()
        if not user_id:
            return {"message": "Unauthorized"}, 401
        return get_cart(user_id)

@blp_api.route("/cart/items")
class CartItems(MethodView):
    """Add or update cart items."""

    @blp_api.arguments(AddCartItemSchema)
    @blp_api.response(200, CartSchema)
    def post(self, payload):
        """Add item to cart
        ---
        summary: Add item to cart
        description: Adds a product to the cart or increments its quantity.
        tags:
          - Cart
        responses:
          401:
            description: Unauthorized
          400:
            description: Invalid input or product not found
        """
        user_id = _auth_user_id()
        if not user_id:
            return {"message": "Unauthorized"}, 401
        try:
            return add_to_cart(user_id, payload["product_id"], payload["quantity"])
        except ValueError as e:
            return {"message": str(e)}, 400

    @blp_api.arguments(UpdateCartItemSchema)
    @blp_api.response(200, CartSchema)
    def put(self, payload):
        """Update cart item
        ---
        summary: Update cart item
        description: Updates quantity for a product in the cart; removes if quantity <= 0.
        tags:
          - Cart
        responses:
          401:
            description: Unauthorized
          400:
            description: Invalid input
        """
        user_id = _auth_user_id()
        if not user_id:
            return {"message": "Unauthorized"}, 401
        try:
            return update_cart_item(user_id, payload["product_id"], payload["quantity"])
        except ValueError as e:
            return {"message": str(e)}, 400

@blp_api.route("/cart/items/<string:product_id>")
class CartItemDelete(MethodView):
    """Remove a specific product from cart."""
    @blp_api.response(200, CartSchema)
    def delete(self, product_id):
        """Remove from cart
        ---
        summary: Remove from cart
        description: Removes a product from the cart.
        tags:
          - Cart
        responses:
          401:
            description: Unauthorized
        """
        user_id = _auth_user_id()
        if not user_id:
            return {"message": "Unauthorized"}, 401
        return remove_from_cart(user_id, product_id)

@blp_api.route("/orders")
class Orders(MethodView):
    """Create order from cart."""
    @blp_api.response(201, OrderSchema)
    def post(self):
        """Create order
        ---
        summary: Create order
        description: Creates an order from the current cart and clears the cart.
        tags:
          - Orders
        responses:
          401:
            description: Unauthorized
          400:
            description: Cart empty
        """
        user_id = _auth_user_id()
        if not user_id:
            return {"message": "Unauthorized"}, 401
        try:
            order = create_order_from_cart(user_id)
            return order, 201
        except ValueError as e:
            return {"message": str(e)}, 400

@blp_api.route("/orders/<string:order_id>")
class OrderDetail(MethodView):
    """Get order details."""
    @blp_api.response(200, OrderSchema)
    def get(self, order_id):
        """Get order
        ---
        summary: Get order
        description: Returns order details for the authenticated user.
        tags:
          - Orders
        responses:
          401:
            description: Unauthorized
          404:
            description: Not found
        """
        user_id = _auth_user_id()
        if not user_id:
            return {"message": "Unauthorized"}, 401
        order = get_order(order_id, user_id)
        if not order:
            return {"message": "Not found"}, 404
        return order
