from typing import Dict, List, Optional
import uuid
import hashlib
import time
import re

# Simple in-memory stores for demo
DB = {
    "products": {},
    "users": {},
    "sessions": {},  # token -> user_id
    "carts": {},     # user_id -> {product_id: quantity}
    "orders": {},    # order_id -> order data
    "categories": {},  # category_id -> category
    "category_slugs": {},  # slug -> category_id (for quick lookup)
}


def _slugify(name: str) -> str:
    """
    Create a simple URL-friendly slug from a category name.
    This is sufficient for demo purposes.
    """
    slug = name.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug).strip("-")
    return slug or "category"


def _ensure_category(name: str) -> Dict:
    """
    Get or create a category by name. Returns the category dict {id, name, slug}.
    """
    slug = _slugify(name)
    existing_id = DB["category_slugs"].get(slug)
    if existing_id:
        return DB["categories"][existing_id]
    cid = str(uuid.uuid4())
    category = {"id": cid, "name": name, "slug": slug}
    DB["categories"][cid] = category
    DB["category_slugs"][slug] = cid
    return category


# Seed products and categories at import time for demo
def _seed_data():
    if DB["products"]:
        return

    # Seed categories
    clothing = _ensure_category("Clothing")
    electronics = _ensure_category("Electronics")
    groceries = _ensure_category("Groceries")

    # Seed products (assign to categories)
    demo = [
        {
            "name": "Ocean Tee",
            "price": 19.99,
            "description": "Soft cotton tee with ocean blue accent.",
            "image": "https://picsum.photos/seed/ocean-tee/400/300",
            "category_id": clothing["id"],
        },
        {
            "name": "Amber Mug",
            "price": 9.49,
            "description": "Ceramic mug with amber glaze.",
            "image": "https://picsum.photos/seed/amber-mug/400/300",
            "category_id": groceries["id"],
        },
        {
            "name": "Wave Hoodie",
            "price": 39.0,
            "description": "Cozy hoodie with wave pattern.",
            "image": "https://picsum.photos/seed/wave-hoodie/400/300",
            "category_id": clothing["id"],
        },
        {
            "name": "Sea Cap",
            "price": 14.5,
            "description": "Adjustable cap with sea emblem.",
            "image": "https://picsum.photos/seed/sea-cap/400/300",
            "category_id": clothing["id"],
        },
        {
            "name": "Coral Earbuds",
            "price": 24.99,
            "description": "Wireless earbuds with clear sound.",
            "image": "https://picsum.photos/seed/coral-earbuds/400/300",
            "category_id": electronics["id"],
        },
        {
            "name": "Tide Power Bank",
            "price": 29.99,
            "description": "Portable charger with fast charging.",
            "image": "https://picsum.photos/seed/tide-powerbank/400/300",
            "category_id": electronics["id"],
        },
        {
            "name": "Citrus Granola",
            "price": 5.99,
            "description": "Crunchy granola with citrus zest.",
            "image": "https://picsum.photos/seed/citrus-granola/400/300",
            "category_id": groceries["id"],
        },
    ]
    for p in demo:
        pid = str(uuid.uuid4())
        DB["products"][pid] = {
            "id": pid,
            "name": p["name"],
            "price": p["price"],
            "description": p["description"],
            "image": p["image"],
            "category_id": p["category_id"],
        }


_seed_data()


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
def list_products(category_id: Optional[str] = None, category_slug: Optional[str] = None) -> List[Dict]:
    """Return list of products; optionally filter by category via id or slug."""
    products = list(DB["products"].values())
    if category_slug:
        cid = DB["category_slugs"].get(category_slug)
        if not cid:
            return []  # unknown slug => no products
        category_id = cid
    if category_id:
        products = [p for p in products if p.get("category_id") == category_id]
    return products


# PUBLIC_INTERFACE
def get_product(product_id: str) -> Optional[Dict]:
    """Return a single product by id or None."""
    return DB["products"].get(product_id)


# PUBLIC_INTERFACE
def list_categories() -> List[Dict]:
    """List all available product categories."""
    # Return consistent ordering (by name)
    return sorted(DB["categories"].values(), key=lambda c: c["name"].lower())


# PUBLIC_INTERFACE
def get_category_by_id(category_id: str) -> Optional[Dict]:
    """Return category by id or None."""
    return DB["categories"].get(category_id)


# PUBLIC_INTERFACE
def get_category_by_slug(slug: str) -> Optional[Dict]:
    """Return category by slug or None."""
    cid = DB["category_slugs"].get(slug)
    if not cid:
        return None
    return DB["categories"].get(cid)


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
