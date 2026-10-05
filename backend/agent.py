import os
import re
from pathlib import Path

from dotenv import load_dotenv
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.models.test import TestModel
from pydantic_ai.providers.openai import OpenAIProvider
from portkey_ai import Portkey

from audit import record_activity
from models import ChatReply, ShopDeps
from tools import candidate_context, catalogue_context, deterministic_lookup, get_current_product, get_product, lookup_inventory, lookup_product_details, search_products

load_dotenv()
PROMPT_PATH = Path(__file__).parent / "prompts" / "prompt.md"
SYSTEM_PROMPT = PROMPT_PATH.read_text(encoding="utf-8")
MODEL_NAME = os.getenv("PORTKEY_MODEL", "gpt-5.6-luna")
PORTKEY_API_KEY = os.getenv("PORTKEY_API_KEY")


def build_agent() -> Agent:
    if PORTKEY_API_KEY:
        # Portkey's OpenAI-compatible client is passed into PydanticAI's OpenAI model.
        portkey_client = Portkey(api_key=PORTKEY_API_KEY, provider="openai")
        model = OpenAIChatModel(MODEL_NAME, provider=OpenAIProvider(openai_client=portkey_client))
        return Agent(model, deps_type=ShopDeps, output_type=ChatReply, system_prompt=SYSTEM_PROMPT)
    return Agent(TestModel(), deps_type=ShopDeps, output_type=ChatReply, system_prompt=SYSTEM_PROMPT)


shop_agent = build_agent()
shop_agent.tool(search_products)
shop_agent.tool(get_product)
shop_agent.tool(lookup_product_details)
shop_agent.tool(lookup_inventory)
shop_agent.tool(get_current_product)

@shop_agent.system_prompt
def runtime_context(ctx: RunContext[ShopDeps]) -> str:
    customer = f"Customer identity: {ctx.deps.customer.name} ({ctx.deps.customer.email})." if ctx.deps.customer else "The shopper is a guest; no customer identity is available."
    page = ctx.deps.page
    viewed = f"The shopper is viewing product '{page.product_name}' (product_id: {page.product_id}). Interpret 'this' as that product." if page and page.product_id else "No single product is currently selected."
    return f"{customer}\nPage context: {page.page if page else 'unknown'}. {viewed}"


async def run_shop_agent(message: str, deps: ShopDeps, fallback_products: list) -> ChatReply:
    if not PORTKEY_API_KEY:
        lookup_query = deps.page.product_name if deps.page and deps.page.product_id and "this" in message.lower() else message
        product, inventory = deterministic_lookup(deps.db_path, lookup_query)
        lowered = message.lower()
        candidates = candidate_context(deps.db_path, lookup_query)
        record_activity("deterministic_catalogue_lookup", {"query": lookup_query}, {"candidate_count": len(candidates)}, "fallback_lookup_completed")
        size_match = re.search(r"\b(XXL|XL|XS|S|M|L)\b", message.upper()) if ("size" in lowered or "stock" in lowered or "available" in lowered) else None
        category_request = any(word in lowered for word in ("what", "which", "show", "have")) and not any(word in lowered for word in ("price", "cost", "stock", "available", "size", "quantity"))
        exact_product = bool(product and product.name.lower() in lowered)
        if len(candidates) > 1 and not exact_product and not category_request and any(word in lowered for word in ("price", "cost", "stock", "available", "size", "quantity")):
            names = ", ".join(item.name for item in candidates[:3])
            reply = f"I found several possible matches: {names}. Which product did you mean?"
            result = ChatReply(reply=reply, products=candidates[:3], clarification_needed=True)
            record_activity("agent_response", {"message": message}, {"reply": result.reply, "product_count": len(result.products)}, "clarification")
            return result
        if category_request and candidates:
            reply = f"I found {len(candidates)} pieces that match your request. Here are the closest catalogue matches."
            result = ChatReply(reply=reply, products=candidates)
            record_activity("agent_response", {"message": message}, {"reply": result.reply, "product_count": len(result.products)}, "category_results")
            return result
        if product and "this" in lowered and "pink" in lowered:
            colors = ", ".join(product.colors)
            reply = f"The product on screen is {product.name}. The catalogue lists these colors: {colors}. Pink is not listed." if "pink" not in [color.lower() for color in product.colors] else f"The product on screen is {product.name}, and pink is listed as an available color."
        elif product and any(word in lowered for word in ("price", "cost", "much", "description", "what is")):
            reply = f"{product.name} is {product.description} It is priced at ${product.price:.2f}."
        elif product and inventory and any(word in lowered for word in ("stock", "available", "size", "quantity")):
            if size_match:
                quantity = inventory.size_quantities.get(size_match.group(1), 0)
                status = "in stock" if quantity else "out of stock"
                reply = f"{product.name} in size {size_match.group(1)} is {status} ({quantity} available)."
            else:
                status = "in stock" if inventory.total_stock else "out of stock"
                reply = f"{product.name} is {status}, with {inventory.total_stock} items across all sizes."
        elif product:
            reply = f"I found {product.name}, priced at ${product.price:.2f}. Ask me about its description, price, or stock."
        else:
            names = ", ".join(product.name for product in fallback_products[:4])
            reply = f"I found {names}. Ask me about a specific style, color, or size." if names else "I can help you find Campus Customs merch. Try asking about a Yale hoodie, sweatshirt, or T-shirt."
        result = ChatReply(reply=reply, products=fallback_products)
        record_activity("agent_response", {"message": message}, {"reply": result.reply, "product_count": len(result.products)}, "fallback_completed")
        return result
    result = await shop_agent.run(message, deps=deps)
    record_activity("agent_response", {"message": message}, {"reply": result.output.reply, "product_count": len(result.output.products)}, "model_completed")
    return result.output
