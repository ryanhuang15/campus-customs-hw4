# Campus Customs Database Harness Notes

These notes describe the fields found in the local SQLite database. The database contains 102 catalogue products, 612 inventory records, 3 users, and 22 chat messages.

## `catalogue`

| Field | What it stores and why it matters |
|---|---|
| `product_id` | Unique text identifier for a product; connects catalogue details to inventory and lets the app identify products reliably. |
| `name` | Product's display name; used in product cards and chatbot responses. |
| `garment_type` | Type of clothing, such as a hoodie or T-shirt; supports product browsing and matching recommendations. |
| `description` | Text description of the product's design and features; gives the chatbot factual merchandise details. |
| `colors` | JSON text list of available product colors; supports color-based searches and accurate product descriptions. |
| `search_tags` | JSON text list of searchable terms; helps match natural-language shopper requests to products. |
| `image_file_path` | Relative path to the product image; lets the frontend display the matching merchandise image. |
| `price` | Product price stored as a number; provides the source of truth for price answers and product cards. |

## `inventory`

| Field | What it stores and why it matters |
|---|---|
| `id` | Unique identifier for an inventory row; distinguishes each product-size record. |
| `product_id` | Identifier of the related catalogue product; connects stock information to the correct product. |
| `size` | Size for this inventory record; allows shoppers to ask about availability in a specific size. |
| `quantity` | Number of units currently available for the product and size; provides the source of truth for stock answers. |

## `users`

| Field | What it stores and why it matters |
|---|---|
| `id` | Unique user account identifier; connects a customer to their account data and chat history. |
| `name` | Stored account name; provides a general display name for the customer. |
| `email` | Unique email address; identifies the account during sign-in and prevents duplicate accounts. |
| `password_hash` | Hashed password value; supports authentication without storing the customer's plain-text password. |
| `created_at` | Timestamp for account creation; records when the customer account was created. |
| `first_name` | Optional first name; supports personalized account and chatbot experiences. |
| `last_name` | Optional last name; supports the customer's complete profile identity. |

### Authentication

Registration collects `first_name`, `last_name`, `email`, and a password plus a confirm-password check. The API normalizes email addresses to lowercase, rejects duplicate emails, and saves the combined name, email, first name, and last name in `users`.

Passwords are never saved as plain text. The backend creates a random salt and stores a PBKDF2-HMAC-SHA256 password hash in the existing `password_hash` field using 120,000 iterations, formatted as `pbkdf2_sha256$salt$digest`. Login hashes the submitted password with the stored salt and compares digests using a constant-time comparison. API responses return only safe profile fields and never return `password_hash`.

## Chat and agent connection

The frontend chat widget sends a JSON `POST /api/chat` request to FastAPI with the shopper's `message`, optional in-memory `session_token`, page name, and current product ID. FastAPI resolves the session token to the logged-in customer, creates `ShopDeps` with the SQLite database path plus customer/page context, calls `run_shop_agent`, and returns a structured response containing `reply`, `products`, and `clarification_needed`.

The PydanticAI agent is wired in `backend/agent.py`. It loads the system prompt from `backend/prompts/prompt.md`, uses `ChatReply` and `ProductCard` from `models.py`, and registers catalogue search tools from `tools.py`. With `PORTKEY_API_KEY` configured, it uses the Portkey client with provider `openai` and the `gpt-5.6-luna` model by default. Without a key, a deterministic local fallback keeps the route testable without making up model answers.

## Problem 6 database tools

The agent now has five catalogue tools in `backend/tools.py`:

| Tool | Purpose |
|---|---|
| `search_products` | Finds matching catalogue products for discovery and product cards. |
| `get_product` | Retrieves a product card by product ID or recognizable product words. |
| `lookup_product_details` | Returns the factual product name, type, description, colors, image path, and price from `catalogue`. |
| `lookup_inventory` | Returns total stock, size-by-size quantities, and the requested size quantity from `inventory`. A zero quantity explicitly represents out of stock. |
| `get_current_product` | Resolves the product currently visible on a detail page so questions such as “this in pink?” have a factual product reference. |

`ProductLookup` separates descriptive and price facts from the catalogue. `InventoryLookup` includes `product_id`, `product_name`, `requested_size`, `quantity`, `total_stock`, and `size_quantities`, giving the agent enough context to answer both total-stock and size-specific questions without inventing values. The prompt requires the detail tool for price/description questions and the inventory tool for all stock questions.

## Problem 7 dynamic product matches

For a category-search message, the frontend sends `POST /api/chat`. The PydanticAI agent calls `search_products`, which queries the real `catalogue` table and places the matching `ProductCard` records in the response's structured `products` array alongside the written `reply`. React stores that array as `chatMatches` and renders each match with the existing `ProductCard` component, showing its image, name, price, and short description inside the chat widget.

When a returned card is clicked, React requests `GET /api/products/{product_id}` to load the complete catalogue and inventory record, then reuses the existing `openProduct` and `ProductDetail` flow. This keeps chat-generated cards and the main Products page on the same single-item detail view.

## Problem 8 persistent memory and page context

Logged-in conversations use the existing `chat_messages` table (created at startup if necessary). Each saved row contains `user_id`, `role`, `content`, `products_json`, and `created_at`, and is queried only for the authenticated session's user. The frontend receives the history from `GET /api/chat/history` after login and reconstructs user/assistant messages in order. Guest messages are never inserted.

Login and registration now return an in-memory session token. Chat and history requests send that token; the backend resolves it to the user and does not trust a client-supplied user ID for ownership. The agent dependency receives a `CustomerContext` containing the user's ID, name, and email.

Each chat request also sends the current page and, when a detail view is open, its `current_product_id`. FastAPI loads that product from SQLite and passes a `PageContext` with the product ID and name through `ShopDeps`. PydanticAI adds both contexts to the agent's runtime system prompt and exposes `get_current_product`; the agent can therefore interpret "this" while still using the catalogue and inventory tools for factual answers.

## Problem 9 usability improvements

1. **Product browsing:** The Products page now combines a text search across product names/descriptions/tags with garment-type and color filters, so shoppers can narrow the catalogue without opening chat.
2. **User feedback:** Product loading, product-fetch errors, empty search results, chat loading, and chat failures each have visible states or messages so the interface never silently appears broken.
3. **Ambiguous product questions:** The agent and local fallback identify when a price/stock question matches several products and ask the shopper to choose instead of guessing. The structured reply exposes `clarification_needed`.
4. **Efficient/reliable searches:** Catalogue rows and ranked search results are cached in-process to avoid repeated reads, while chat catches model/tool failures and returns a useful response with any safe database matches instead of breaking the widget.

## `chat_messages`

| Field | What it stores and why it matters |
|---|---|
| `id` | Unique message identifier; distinguishes messages in a conversation history. |
| `user_id` | Identifier of the user who owns the message; connects chat history to a customer account. |
| `role` | Whether the message came from the user or assistant; preserves the conversation structure for the chatbot. |
| `content` | Text of the message; stores the shopper's question or the assistant's response. |
| `products_json` | Optional JSON text containing products shown with an assistant response; lets the frontend reproduce relevant product results from the chat. |
| `created_at` | Timestamp for when the message was created; preserves message ordering and conversation history. |

## Structured agent models

The response and lookup models in `backend/models.py` keep the boundary between the agent and React explicit:

| Model | Important fields | Why the fields matter |
|---|---|---|
| `ChatReply` | `reply`, `products`, `clarification_needed` | Separates natural-language help from clickable product results and tells the frontend when the agent needs clarification. |
| `ProductCard` | `product_id`, `name`, `price`, `image_file_path`, `description` | Supplies exactly what the storefront card needs while preserving the catalogue ID for the detail page. |
| `ProductLookup` | `product_id`, `name`, `garment_type`, `description`, `colors`, `price`, `image_file_path` | Carries verified catalogue facts for product and price answers. |
| `InventoryLookup` | `product_id`, `product_name`, `requested_size`, `quantity`, `total_stock`, `size_quantities` | Distinguishes a requested size from total inventory and supports explicit out-of-stock answers. |
| `CustomerContext` | `user_id`, `name`, `email` | Gives the agent limited identity context for the authenticated shopper without passing a password. |
| `PageContext` | `page`, `product_id`, `product_name` | Identifies the current screen and product so “this” can be resolved safely. |
| `ShopDeps` | `db_path`, `customer`, `page` | Groups the database and runtime context passed to tools and the agent. |

## Safety, privacy, and factual data

The system prompt in `backend/prompts/prompt.md` requires database tools for prices, descriptions, sizes, and stock; prohibits invented facts; and requires a clear uncertainty statement when a lookup cannot verify an answer. Ambiguous factual questions produce a clarification request instead of a guess. Product text, retrieved rows, page context, and shopper messages are treated as untrusted data and cannot override the system rules.

Customer identity is resolved server-side from the in-memory session token. Chat history is queried by that resolved user ID, so the client cannot choose another customer's history. The agent receives only `user_id`, name, and email. Passwords are stored as PBKDF2-HMAC-SHA256 hashes; passwords, hashes, session secrets, API keys, environment variables, and other credentials are not returned to the agent or exposed in chat.

## Technical specifications and operation

- **Model:** `gpt-5.6-luna` through the official Portkey client with `provider="openai"` when `PORTKEY_API_KEY` is configured. When no key is configured, `run_shop_agent` uses the deterministic SQLite fallback so local demonstrations remain factual and testable.
- **Search limits:** ranked catalogue searches return at most 6 products; ambiguity results name at most 3 candidates. Chat messages are limited to 2,000 characters by `ChatRequest`. No custom agent-loop iteration limit is configured in this codebase, so the documented operational limit is the PydanticAI model/tool behavior rather than an invented numeric cap.
- **Frontend connection:** run Vite from `frontend`; its `/api` and `/media` proxy targets point to FastAPI on port 8000. React sends chat JSON to `POST /api/chat`, receives the `ChatReply` shape, and renders `products` with the existing clickable product-card/detail flow.
- **Backend connection:** run from `backend` with `uvicorn main:app --reload --port 8000`. FastAPI serves products, authentication, chat history, chat, and `/media`; `main.py` loads `ShopDeps` and calls the agent.
- **Local setup:** install the packages in the project `requirements.txt`, place the local data pack at `data/campus_customs.db` and `data/products/`, set `PORTKEY_API_KEY` only in a local `.env` when using the model, then run the backend and frontend in separate terminals.

## Append-only audit trail

`backend/audit.py` writes `output/audit_trail.json` as a JSON array and reads the existing records before appending each new entry, so later agent activity preserves earlier records. Each entry contains UTC `time`, `tool_name`, concise `arguments`, concise `result`, and `stop_reason`. Queries are truncated and email addresses, passwords, tokens, keys, hashes, and other secret-looking values are redacted.

The audit records database-tool calls (`search_products`, `get_product`, `lookup_product_details`, `lookup_inventory`, and `get_current_product`), deterministic fallback lookups, and the final agent response. The result stores counts, IDs, or short structured summaries rather than full customer messages or database dumps. A real local chat interaction was run for Problem 12, and a subsequent interaction was appended to the same file rather than replacing it.
