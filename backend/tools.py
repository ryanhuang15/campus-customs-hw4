import json
import re
import sqlite3
from functools import lru_cache

from pydantic_ai import RunContext

from audit import record_activity
from models import InventoryLookup, ProductCard, ProductLookup, ShopDeps


@lru_cache(maxsize=1)
def _catalogue_rows(db_path: str) -> tuple[dict, ...]:
    with sqlite3.connect(db_path) as db:
        db.row_factory = sqlite3.Row
        return tuple(dict(row) for row in db.execute("SELECT * FROM catalogue ORDER BY name").fetchall())


@lru_cache(maxsize=256)
def _search_rows(db_path: str, query: str, limit: int = 6) -> list[dict]:
    stopwords = {"a", "an", "and", "are", "do", "for", "have", "i", "is", "me", "of", "show", "some", "the", "want", "what", "you"}
    terms = []
    for term in re.findall(r"[a-z0-9]+", query.lower()):
        if term in stopwords:
            continue
        plural_aliases = {"hoodies": "hoodie", "tshirts": "t-shirt", "sweatshirts": "sweatshirt"}
        terms.append(plural_aliases.get(term, term[:-3] + "y" if term.endswith("ies") else term[:-1] if term.endswith("s") and len(term) > 3 else term))
    scored = []
    for row in _catalogue_rows(str(db_path)):
        haystack = " ".join((row["name"], row["garment_type"], row["description"], row["colors"], row["search_tags"])).lower()
        score = sum(term in haystack for term in terms)
        if not terms or score:
            scored.append((score, dict(row)))
    scored.sort(key=lambda item: (-item[0], item[1]["name"]))
    return [row for _, row in scored[:limit]]


def _cards(rows: list[dict]) -> list[ProductCard]:
    return [ProductCard(product_id=row["product_id"], name=row["name"], price=row["price"], image_file_path=row["image_file_path"], description=row["description"]) for row in rows]


def _product_lookup(row: dict) -> ProductLookup:
    return ProductLookup(product_id=row["product_id"], name=row["name"], garment_type=row["garment_type"], description=row["description"], colors=json.loads(row["colors"]), price=row["price"], image_file_path=row["image_file_path"])


def _inventory_lookup(db_path, row: dict, size: str | None = None) -> InventoryLookup:
    with sqlite3.connect(db_path) as db:
        stock_rows = db.execute("SELECT size, quantity FROM inventory WHERE product_id = ? ORDER BY id", (row["product_id"],)).fetchall()
    quantities = {stock_size: quantity for stock_size, quantity in stock_rows}
    requested = size.strip().upper() if size else None
    quantity = quantities.get(requested, 0) if requested else sum(quantities.values())
    return InventoryLookup(product_id=row["product_id"], product_name=row["name"], requested_size=requested, quantity=quantity, total_stock=sum(quantities.values()), size_quantities=quantities)


async def search_products(ctx: RunContext[ShopDeps], query: str) -> list[ProductCard]:
    """Find catalogue products matching a shopper's words."""
    result = _cards(_search_rows(ctx.deps.db_path, query))
    record_activity("search_products", {"query": query}, {"count": len(result), "product_ids": [item.product_id for item in result]}, "tool_completed")
    return result


async def get_product(ctx: RunContext[ShopDeps], product_id: str) -> ProductCard | None:
    """Look up one catalogue product by product_id or recognizable product words."""
    rows = _search_rows(ctx.deps.db_path, product_id, limit=1)
    result = _cards(rows)[0] if rows else None
    record_activity("get_product", {"product_id": product_id}, result.model_dump() if result else None, "tool_completed")
    return result


async def lookup_product_details(ctx: RunContext[ShopDeps], product_query: str) -> ProductLookup | None:
    """Look up factual product description, colors, and price from catalogue."""
    rows = _search_rows(ctx.deps.db_path, product_query, limit=1)
    result = _product_lookup(rows[0]) if rows else None
    record_activity("lookup_product_details", {"product_query": product_query}, result.model_dump() if result else None, "tool_completed")
    return result


async def lookup_inventory(ctx: RunContext[ShopDeps], product_query: str, size: str | None = None) -> InventoryLookup | None:
    """Look up total stock or exact size stock from inventory; zero means out of stock."""
    rows = _search_rows(ctx.deps.db_path, product_query, limit=1)
    result = _inventory_lookup(ctx.deps.db_path, rows[0], size) if rows else None
    record_activity("lookup_inventory", {"product_query": product_query, "size": size}, result.model_dump() if result else None, "tool_completed")
    return result


async def get_current_product(ctx: RunContext[ShopDeps]) -> ProductLookup | None:
    """Return the product currently visible on the shopper's detail page."""
    if not ctx.deps.page or not ctx.deps.page.product_id:
        return None
    rows = _search_rows(ctx.deps.db_path, ctx.deps.page.product_id, limit=1)
    result = _product_lookup(rows[0]) if rows else None
    record_activity("get_current_product", {"product_id": ctx.deps.page.product_id if ctx.deps.page else None}, result.model_dump() if result else None, "tool_completed")
    return result


def catalogue_context(db_path, query: str) -> list[ProductCard]:
    """Small deterministic lookup used when no model key is configured."""
    return _cards(_search_rows(db_path, query))


def candidate_context(db_path, query: str, limit: int = 6) -> list[ProductCard]:
    """Return ranked candidates so the agent can clarify an ambiguous request."""
    return _cards(_search_rows(db_path, query, limit))


def deterministic_lookup(db_path, query: str) -> tuple[ProductLookup | None, InventoryLookup | None]:
    rows = _search_rows(db_path, query, limit=1)
    if not rows:
        return None, None
    row = rows[0]
    return _product_lookup(row), _inventory_lookup(db_path, row)
