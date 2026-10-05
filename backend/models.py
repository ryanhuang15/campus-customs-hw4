from pydantic import BaseModel, Field


class ProductCard(BaseModel):
    product_id: str
    name: str
    price: float
    image_file_path: str
    description: str = ""


class ProductLookup(BaseModel):
    product_id: str
    name: str
    garment_type: str
    description: str
    colors: list[str]
    price: float
    image_file_path: str


class InventoryLookup(BaseModel):
    product_id: str
    product_name: str
    requested_size: str | None = None
    quantity: int
    total_stock: int
    size_quantities: dict[str, int] = Field(default_factory=dict)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    user_id: int | None = None
    session_token: str | None = None
    page: str = ""
    current_product_id: str | None = None


class CustomerContext(BaseModel):
    user_id: int
    name: str
    email: str


class PageContext(BaseModel):
    page: str = ""
    product_id: str | None = None
    product_name: str | None = None


class ChatReply(BaseModel):
    reply: str
    products: list[ProductCard] = Field(default_factory=list)
    clarification_needed: bool = False


class ShopDeps:
    def __init__(self, db_path, customer: CustomerContext | None = None, page: PageContext | None = None):
        self.db_path = db_path
        self.customer = customer
        self.page = page
