from typing import Dict, List, Optional
import uuid
import hashlib
import time

# Simple in-memory stores for demo
DB = {
    "products": {},
    "users": {},
    "sessions": {},  # token -> user_id
    "carts": {},     # user_id -> {product_id: quantity}
    "orders": {},    # order_id -> order data
}

# Seed products at import time for demo
def _seed_products():
    if DB["products"]:
        return
    demo = [
        {"name": "Ocean Tee", "price": 19.99, "description": "Soft cotton tee with ocean blue accent.", "image": "https://picsum.photos/seed/ocean-tee/400/300"},
        {"name": "Amber Mug", "price": 9.49, "description": "Ceramic mug with amber glaze.", "image": "https://picsum.photos/seed/amber-mug/400/300"},
        {"name": "Wave Hoodie", "price": 39.0, "description": "Cozy hoodie with wave pattern.", "image": "https://picsum.photos/seed/wave-hoodie/400/300"},
        {"name": "Sea Cap", "price": 14.5, "description": "Adjustable cap with sea emblem.", "image": "https://picsum.photos/seed/sea-cap/400/300"},
    ]
    for p in demo:
        pid = str(uuid.uuid4())
        DB["products"][pid] = {
            "id": pid,
            "name": p["name"],
            "price": p["price"],
            "description": p["description"],
            "image": p["image"],
        }

_seed_products()


def _hash_password(password: str) -> str:
    # Very basic hash for demo purposes only
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def _generate_token(user_id: str) -> str:
    token = hashlib.sha256(f"{user_id}:{time.time()}:{uuid.uuid4()}".encode("utf-8")).hexdigest()
    DB["sessions"][token] = user_id
    return token


def get_user_id_from_token(token: Optional[str]) -> Optional[str]:
    if not token:
        return None
    return DB["sessions"].get(token)


# PUBLIC_INTERFACE
def list_products() -> List[Dict]:
    """Return list of all products for the catalog."""
    return list(DB["products"].values())


# PUBLIC_INTERFACE
def get_product(product_id: str) -> Optional[Dict]:
    """Return a single product by id or None."""
    return DB["products"].get(product_id)


# PUBLIC_INTERFACE
def signup(email: str, password: str) -> Dict:
    """Create a user account with email/password and return auth token."""
    for u in DB["users"].values():
        if u["email"].lower() == email.lower():
            raise ValueError("Email already registered")
    uid = str(uuid.uuid4())
    DB["users"][uid] = {"id": uid, "email": email, "password_hash": _hash_password(password)}
    token = _generate_token(uid)
    # Initialize empty cart
    DB["carts"][uid] = {}
    return {"user": {"id": uid, "email": email}, "token": token}


# PUBLIC_INTERFACE
def login(email: str, password: str) -> Dict:
    """Authenticate user and return auth token."""
    hashed = _hash_password(password)
    for uid, u in DB["users"].items():
        if u["email"].lower() == email.lower() and u["password_hash"] == hashed:
            token = _generate_token(uid)
            return {"user": {"id": uid, "email": u["email"]}, "token": token}
    raise ValueError("Invalid credentials")


# PUBLIC_INTERFACE
def get_cart(user_id: str) -> Dict:
    """Return current cart with product details and totals."""
    cart_items = DB["carts"].setdefault(user_id, {})
    items = []
    subtotal = 0.0
    for pid, qty in cart_items.items():
        prod = DB["products"].get(pid)
        if not prod:
            continue
        line_total = prod["price"] * qty
        subtotal += line_total
        items.append({"product": prod, "quantity": qty, "line_total": round(line_total, 2)})
    return {"items": items, "subtotal": round(subtotal, 2)}


# PUBLIC_INTERFACE
def add_to_cart(user_id: str, product_id: str, quantity: int) -> Dict:
    """Add or increment a product in the user's cart."""
    if product_id not in DB["products"]:
        raise ValueError("Product not found")
    if quantity <= 0:
        raise ValueError("Quantity must be positive")
    cart = DB["carts"].setdefault(user_id, {})
    cart[product_id] = cart.get(product_id, 0) + quantity
    return get_cart(user_id)


# PUBLIC_INTERFACE
def update_cart_item(user_id: str, product_id: str, quantity: int) -> Dict:
    """Update the quantity of a product in the cart; remove if quantity <= 0."""
    cart = DB["carts"].setdefault(user_id, {})
    if product_id not in DB["products"]:
        raise ValueError("Product not found")
    if quantity <= 0:
        cart.pop(product_id, None)
    else:
        cart[product_id] = quantity
    return get_cart(user_id)


# PUBLIC_INTERFACE
def remove_from_cart(user_id: str, product_id: str) -> Dict:
    """Remove a product from cart."""
    cart = DB["carts"].setdefault(user_id, {})
    cart.pop(product_id, None)
    return get_cart(user_id)


# PUBLIC_INTERFACE
def create_order_from_cart(user_id: str) -> Dict:
    """Create an order from the user's current cart and clear the cart."""
    cart_summary = get_cart(user_id)
    if not cart_summary["items"]:
        raise ValueError("Cart is empty")
    order_id = str(uuid.uuid4())
    order = {
        "id": order_id,
        "user_id": user_id,
        "items": cart_summary["items"],
        "subtotal": cart_summary["subtotal"],
        "status": "PLACED",
        "created_at": int(time.time()),
    }
    DB["orders"][order_id] = order
    DB["carts"][user_id] = {}  # clear cart after placing order
    return order


# PUBLIC_INTERFACE
def get_order(order_id: str, user_id: str) -> Optional[Dict]:
    """Return order details if owned by user."""
    order = DB["orders"].get(order_id)
    if not order or order["user_id"] != user_id:
        return None
    return order
