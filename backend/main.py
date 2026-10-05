import json
import hashlib
import hmac
import secrets
import sqlite3
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from agent import PORTKEY_API_KEY, run_shop_agent
from models import ChatReply, ChatRequest, CustomerContext, PageContext, ShopDeps
from tools import catalogue_context

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data"
DB_PATH = ROOT / "data" / "campus_customs.db"
PRODUCTS_PATH = ROOT / "data" / "products"

app = FastAPI(title="Campus Customs API")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"], allow_methods=["*"], allow_headers=["*"])
app.mount("/media", StaticFiles(directory=DATA_PATH), name="media")
SESSIONS: dict[str, int] = {}

def ensure_chat_history_table() -> None:
    with sqlite3.connect(DB_PATH) as db:
        db.execute("""CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            products_json TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )""")

ensure_chat_history_table()

HASH_ITERATIONS = 120_000

class RegisterRequest(BaseModel):
    first_name: str = Field(min_length=1, max_length=80)
    last_name: str = Field(min_length=1, max_length=80)
    email: str = Field(min_length=3, max_length=200)
    password: str = Field(min_length=8, max_length=200)

class LoginRequest(BaseModel):
    email: str = Field(min_length=3, max_length=200)
    password: str = Field(min_length=1, max_length=200)

def make_password_hash(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), HASH_ITERATIONS).hex()
    return f"pbkdf2_sha256${salt}${digest}"

def check_password(password: str, stored_hash: str) -> bool:
    try:
        algorithm, salt, expected = stored_hash.split("$", 2)
        if algorithm != "pbkdf2_sha256":
            return False
        actual = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), HASH_ITERATIONS).hex()
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False

def public_user(row: sqlite3.Row) -> dict:
    return {"id": row["id"], "first_name": row["first_name"], "last_name": row["last_name"], "name": row["name"], "email": row["email"]}

def issue_session(row: sqlite3.Row) -> str:
    token = secrets.token_urlsafe(32)
    SESSIONS[token] = row["id"]
    return token

def customer_for_session(token: str | None) -> CustomerContext | None:
    user_id = SESSIONS.get(token or "")
    if not user_id:
        return None
    with sqlite3.connect(DB_PATH) as db:
        db.row_factory = sqlite3.Row
        row = db.execute("SELECT id, name, email FROM users WHERE id = ?", (user_id,)).fetchone()
    return CustomerContext(user_id=row["id"], name=row["name"], email=row["email"]) if row else None

def save_chat_message(user_id: int, role: str, content: str, products: list[dict] | None = None) -> None:
    with sqlite3.connect(DB_PATH) as db:
        db.execute("INSERT INTO chat_messages (user_id, role, content, products_json) VALUES (?, ?, ?, ?)", (user_id, role, content, json.dumps(products or [])))

def product_row(row: sqlite3.Row, db: sqlite3.Connection) -> dict:
    product = dict(row)
    for field in ("colors", "search_tags"):
        product[field] = json.loads(product[field])
    stock = db.execute("SELECT size, quantity FROM inventory WHERE product_id = ? ORDER BY id", (product["product_id"],)).fetchall()
    product["inventory"] = [dict(item) for item in stock]
    return product

def read_products(product_id: str | None = None) -> list[dict]:
    if not DB_PATH.exists():
        raise HTTPException(status_code=503, detail="Local database not found. Place it at data/campus_customs.db.")
    with sqlite3.connect(DB_PATH) as db:
        db.row_factory = sqlite3.Row
        query = "SELECT * FROM catalogue"
        args: tuple[str, ...] = ()
        if product_id:
            query += " WHERE product_id = ?"
            args = (product_id,)
        query += " ORDER BY name"
        return [product_row(row, db) for row in db.execute(query, args).fetchall()]

@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

@app.get("/api/products")
def products() -> list[dict]:
    return read_products()

@app.get("/api/products/{product_id}")
def product(product_id: str) -> dict:
    result = read_products(product_id)
    if not result:
        raise HTTPException(status_code=404, detail="Product not found")
    return result[0]

@app.post("/api/auth/register")
def register(request: RegisterRequest) -> dict:
    email = request.email.strip().lower()
    first_name = request.first_name.strip()
    last_name = request.last_name.strip()
    if not first_name or not last_name or "@" not in email:
        raise HTTPException(status_code=400, detail="Please enter a valid name and email address.")
    with sqlite3.connect(DB_PATH) as db:
        db.row_factory = sqlite3.Row
        existing = db.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
        if existing:
            raise HTTPException(status_code=409, detail="An account with that email already exists.")
        db.execute("INSERT INTO users (name, email, password_hash, first_name, last_name) VALUES (?, ?, ?, ?, ?)", (f"{first_name} {last_name}", email, make_password_hash(request.password), first_name, last_name))
        row = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        return {"user": public_user(row), "session_token": issue_session(row)}

@app.post("/api/auth/login")
def login(request: LoginRequest) -> dict:
    email = request.email.strip().lower()
    with sqlite3.connect(DB_PATH) as db:
        db.row_factory = sqlite3.Row
        row = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        if not row or not check_password(request.password, row["password_hash"]):
            raise HTTPException(status_code=401, detail="Email or password is incorrect.")
        return {"user": public_user(row), "session_token": issue_session(row)}

@app.get("/api/chat/history")
def chat_history(session_token: str) -> dict:
    customer = customer_for_session(session_token)
    if not customer:
        raise HTTPException(status_code=401, detail="A valid login is required to load chat history.")
    with sqlite3.connect(DB_PATH) as db:
        db.row_factory = sqlite3.Row
        rows = db.execute("SELECT id, role, content, products_json, created_at FROM chat_messages WHERE user_id = ? ORDER BY id", (customer.user_id,)).fetchall()
    messages = []
    for row in rows:
        try:
            products = json.loads(row["products_json"] or "[]")
        except json.JSONDecodeError:
            products = []
        messages.append({"id": row["id"], "role": row["role"], "content": row["content"], "products": products, "created_at": row["created_at"]})
    return {"messages": messages}

@app.post("/api/chat")
async def chat(request: ChatRequest) -> dict:
    customer = customer_for_session(request.session_token)
    fallback_products = []
    if not PORTKEY_API_KEY:
        try:
            fallback_products = catalogue_context(DB_PATH, request.message)
        except Exception:
            fallback_products = []
    current_product = None
    if request.current_product_id:
        try:
            selected = read_products(request.current_product_id)[0]
            current_product = PageContext(page=request.page, product_id=selected["product_id"], product_name=selected["name"])
        except (HTTPException, IndexError):
            current_product = PageContext(page=request.page)
    page_context = current_product or PageContext(page=request.page)
    try:
        result = await run_shop_agent(request.message, ShopDeps(DB_PATH, customer=customer, page=page_context), fallback_products)
    except Exception:
        result = ChatReply(reply="I’m having trouble reaching the shop assistant right now. Please try again in a moment.", products=fallback_products)
    payload = result.model_dump()
    if customer:
        save_chat_message(customer.user_id, "user", request.message)
        save_chat_message(customer.user_id, "assistant", result.reply, payload["products"])
    return payload
