# AI Prompt Log

This file is a running log of the prompts used while completing Homework 4 for the Campus Customs customer website project.

## Problem 1: Vibe coder prompts

### Prompt

> We are starting Homework 4. My existing VS Code folder is named "HW 4", so use that as the project root and don't create another `hw4` folder inside it.
>
> For context, the overall project is going to be a customer website for Campus Customs. Eventually it will have a React + Vite TypeScript frontend and a Python FastAPI backend with a PydanticAI agent. Customers should eventually be able to browse products, make an account, chat about merch, see matching products on the page, and get accurate price and stock information from the local SQLite database. We will build all of that one problem at a time, so don't try to implement the whole project yet.
>
> For Problem 1, create `AI_prompts.md` in the HW 4 project root. This is going to be a running log of the prompts I give you while we work through each problem. Set it up so there can be one section for each problem with the problem number and title, the prompt I gave you, and if needed a follow-up prompt plus a short explanation of what was missing from the first attempt.
>
> For now just create and set up `AI_prompts.md` for Problem 1: Vibe coder prompts. We will keep adding to this same file as we work through the homework.

### Follow-up prompt

_None yet._

### What was missing from the first attempt

_Not applicable yet._

## Problem 2: Database analysis and harness notes

### Prompt

> For problem 2, I need you to analyze the database in `data/campus_customs.db` and understand what information is actually stored there. Please inspect the database itself rather than assuming what the fields are.
>
> At a minimum, look at the catalogue, inventory, and users tables. For each table, identify all of its fields and understand what each one stores.
>
> Then start `output/harness.md`. Write down each table and its fields, with one short line explaining why each field matters for the shop or chatbot. Keep this pretty straightforward since we will keep adding to `harness.md` in later problems for models, tools, safety, specs, etc.
>
> Also add this prompt to `AI_prompts.md` under Problem 2. Don't work ahead on later problems yet.

### Follow-up prompt

_None yet._

### What was missing from the first attempt

_Not applicable yet._

## Problem 3: Campus Customs website scaffold

### Prompt

> For problem 3, I need to build the actual Campus Customs website. Please scaffold a React + Vite + TypeScript frontend and make it look like a real customer-facing store, not just a basic demo.
>
> The site needs a nav bar with Home, Products, About Us, Log in, and Create account. Research yalebulldogblue.com to get a sense of the Campus Customs style and wording for the Home and About Us pages, but don't directly copy their text. Write our own versions that feel similar to the actual store.
>
> For the Products page, use the products from our catalogue database and show the product image, name, price, and a short description. Use the image paths that are already stored in the database. Each product card should be clickable and open its own product page. On that page, show a larger product image on one side and the full product information on the other, including description, price, and sizes/stock when that information is available.
>
> Also add a chat interface that stays in the bottom right of the website. It doesn't need to actually communicate with the AI agent yet, so for now just make it a working frontend stub that we can connect to the backend later.
>
> We will need to read products and images from the database, so you can start a simple FastAPI app in `backend/main.py` to serve what the frontend needs. Keep this setup simple because we are going to expand the backend into the agent in problem 5.
>
> Please run/check the frontend and backend after building them and fix any obvious errors. Add this prompt to `AI_prompts.md` under Problem 3. Don't work ahead on the later problems yet.

### Follow-up prompt

_None yet._

### What was missing from the first attempt

_Not applicable yet._

## Problem 4: Account registration and login

### Prompt

> For problem 4, I need to add a normal create account and login flow to the Campus Customs website. For creating an account, have the user enter their first name, last name, email, and password. Also add a confirm password field. New accounts should be saved in the existing users table in campus_customs.db. Make sure passwords are stored securely and never save the actual plain text password. For login, users should enter their email and password and have those checked against the users table. Give a clear message if the login information is wrong and make a successful login work like a normal website. Please connect both of these to the existing Create account and Log in pages from problem 3 and keep the styling consistent with the rest of the website. Test the login using the existing test user: email: test@campuscustoms.yale.edu; password: [test credential omitted from public log]. Also create a brand new account and confirm that the new account can log in correctly too. Update output/harness.md with how the authentication works, including what information we store for each user and how the passwords are protected. Run/check everything after implementing it and fix any obvious errors. Also add this prompt to AI_prompts.md under Problem 4. Don't work ahead on problem 5 yet.

### Follow-up prompt

_None yet._

### What was missing from the first attempt

_Not applicable yet._

## Problem 5: PydanticAI shop chatbot

### Prompt

> For problem 5, I need to turn the shop chatbot into a PydanticAI agent behind our existing FastAPI backend and connect it to the chat widget we made earlier. Keep the agent organized into these four files under backend: prompts/prompt.md for the system prompt, agent.py for the agent setup/wiring, tools.py for tools the agent can call, and models.py for the Pydantic/PydanticAI structured types. Use backend/main.py as the FastAPI app that we run with Uvicorn. Add a chat route so when a shopper sends a message through the website chat widget, it goes through FastAPI to the PydanticAI agent and returns the agent's reply back to the frontend. Keep the existing product and auth functionality working too. In prompts/prompt.md, give the chatbot a Campus Customs voice and some basic safety rules. It should act like a helpful store assistant and not make up information it doesn't actually know. We will expand the tools and safety rules in later problems, so keep this part fairly simple for now. Add or update the structured types in models.py for chat replies and product cards if they are needed. Update output/harness.md with how the frontend communicates with FastAPI and how the PydanticAI agent gets loaded, including the prompt file and model. Make sure the backend can actually be run from inside the backend folder with: uvicorn main:app --reload --port 8000. Please test the backend and chat connection and fix any obvious errors. Add this prompt to AI_prompts.md under Problem 5. Don't work ahead on problem 6 yet.

### Follow-up prompt

_None yet._

### What was missing from the first attempt

_Not applicable yet._

## Problem 6: Database-backed product and inventory tools

### Prompt

> For problem 6, I need to give the chatbot tools that look up real product information from campus_customs.db instead of having the agent guess. Add the tools to backend/tools.py. The agent should be able to look up product descriptions, prices, how many items are in stock, and stock by size when the customer asks about a specific size. Use the actual catalogue and inventory data we analyzed earlier. The agent should always use these database tools when answering price or stock questions and should never invent a price or quantity. If a product or size is out of stock, it should clearly tell the customer that. Expand backend/prompts/prompt.md so the agent knows when it needs to call these tools, especially for price and inventory questions. Also add or update the structured return types in backend/models.py for the lookup results. Choose fields that give the agent enough information to answer the customer without making anything up. Update output/harness.md with each tool the agent now has and explain the model fields used for the lookup results and why they were chosen. Please test the tools against the actual database and make sure the chatbot can use them correctly. Fix any obvious issues you find. Add this prompt to AI_prompts.md under Problem 6. Don't work ahead on problem 7 yet.

### Follow-up prompt

_None yet._

### What was missing from the first attempt

_Not applicable yet._

## Problem 7: Dynamic chatbot product search

### Prompt

> For Problem 7, I want the chatbot's product search to dynamically update the website. When a customer asks the chatbot about a type of product, such as "what hoodies do you have?", have the agent search the real catalogue database and return structured matching product data to the frontend. The frontend should then display those matches as product cards on the website, including the product image, name, price, and short description. Please implement the full connection between the agent, FastAPI, and React rather than having the chatbot only describe the products in text. Use a clear structured API response so the frontend can distinguish the chatbot's written reply from the matching products it should render. The dynamically generated product cards should work the same way as the product cards we built earlier. When a customer clicks one of the cards returned from chat search, it should open that product's existing single-item detail view with the large image and full product information. Reuse the existing product-card/detail-page behavior instead of creating a separate incompatible version. Update backend/prompts/prompt.md so the agent understands that product-category or product-search requests should use the catalogue search capability and return product matches for the page to display. Update output/harness.md to explain how a customer's chat request flows from the frontend to FastAPI, through the agent/database search, and back to the frontend as structured product matches that become clickable product cards. Test this with at least a query like "what hoodies do you have?" and verify that: 1. the results come from the actual database, 2. matching cards appear dynamically on the page, 3. the cards show image, name, price, and short information, 4. clicking a dynamically generated card opens the correct single-item detail page, 5. existing website and chatbot functionality still works. Add this prompt to AI_prompts.md under Problem 7. Do not work ahead on Problem 8 yet.

### Follow-up prompt

_None yet._

### What was missing from the first attempt

_Not applicable yet._

## Problem 8: Persistent customer memory and page context

### Prompt

> For Problem 8, I want to add persistent customer memory and page context to the chatbot. For logged-in users, save their chat history in the SQLite database and reload that history when they return. Create an appropriate chat-history table if one does not already exist. Associate the stored messages with the correct user so different customers never share chat histories. Store enough information to reconstruct the conversation, such as the user, role, message content, and ordering/timestamp. Guests should still be able to use the chatbot normally, but their chat history does not need to persist after they leave. When a logged-in customer chats, make sure the agent knows who it is talking to, including at least the customer's name and email. Pass this information through the agent dependencies/context or another clear PydanticAI pattern rather than relying on the model to infer the user's identity from conversation text. Also pass relevant page context from the React frontend to the backend/agent. In particular, when the shopper is viewing a single-product page, the agent should know which product is currently being viewed. This should allow contextual questions such as "do you have this in pink?" or "what sizes do you have this in?" to refer to the product currently on screen. The agent should still use the database tools for factual information such as stock rather than inventing an answer. Please connect this to the existing authentication, FastAPI chat route, PydanticAI agent, and React chat interface without breaking the functionality from Problems 3-7. Test that a guest can still chat. Test that a logged-in user's messages are written to the database. Test that the same logged-in user's previous conversation reloads when they return. Test that different users cannot receive each other's histories. Confirm that the agent receives the logged-in customer's name and email. From a product detail page, test that a question using "this" can be interpreted using the current product and page context. Confirm that product, price, and inventory answers still come from the database rather than being invented. Update output/harness.md to explain how chat history is stored, which customer fields the agent receives, and how page/product context travels from the frontend to the agent. Add this prompt to AI_prompts.md under Problem 8. Do not work ahead on Problem 9 yet.

### Follow-up prompt

_None yet._

### What was missing from the first attempt

_Not applicable yet._

## Problem 9: Usability improvements

### Prompt

> For Problem 9, I want to make four meaningful usability improvements to the Campus Customs site: two frontend improvements and two agent/backend improvements. Please implement them in the existing application rather than rebuilding functionality that already works. For the first frontend improvement, improve product browsing by adding a search and filtering experience on the Products page. A shopper should be able to search products by name or description and narrow what is displayed without needing to use the chatbot. Keep this visually consistent with the Campus Customs design we already built. For the second frontend improvement, improve user feedback throughout the site. Add clear loading states while products or chatbot responses are being retrieved, useful empty states when searches have no matches, and understandable error messages when a request fails. The goal is to prevent the shopper from being left with a blank page or wondering whether the site is still working. For the first agent/backend improvement, make the chatbot handle ambiguous product questions more intelligently. If a shopper asks something that is not specific enough to identify the intended product, the agent should ask a useful clarification question instead of guessing. It should continue using the real database for factual product, price, and inventory information. For the second agent/backend improvement, improve the efficiency and reliability of database-backed product searches. Use the existing database tools and structured responses efficiently, avoid unnecessary model calls or repeated database work where possible, and make sure failures produce a useful response rather than breaking the chat experience. Before or while implementing these changes, create output/usability.md. For each of the four improvements, explain what was added and why it helps a Campus Customs shopper or the business. Keep the explanations concise and specific to what was actually implemented. Make sure all four improvements are visible or testable in the running application. Test the new functionality and confirm that the existing product pages, authentication, chatbot, dynamic product results, customer memory, and page context from the earlier problems still work. Add this prompt to AI_prompts.md under Problem 9. Do not work ahead on Problem 10 yet.

### Follow-up prompt

_None yet._

### What was missing from the first attempt

_Not applicable yet._

## Problem 10: Visual design refinement

### Prompt

> For Problem 10, I want to substantially improve the visual design of the Campus Customs website so it feels like a polished, real ecommerce storefront rather than a basic class project. Keep all of the functionality we have already built, but be creative with the presentation and overall shopping experience. Use Campus Customs and Yale-inspired visual identity as the foundation. Create a cohesive color palette, typography system, spacing system, and clear visual hierarchy across the entire site. The pages should feel consistent with each other rather than like separate components that were added over time. Make the home page feel like an actual storefront landing page. Improve the hero area, navigation, calls to action, featured merchandise presentation, and overall composition so a shopper immediately understands the brand and has obvious paths into the catalogue. Give the Products page a more polished ecommerce feel. Improve the product grid, cards, image presentation, search and filter controls, pricing hierarchy, hover states, and spacing. Product cards should feel interactive and make shoppers want to explore individual items. Improve the single-product pages with stronger image presentation and a clear hierarchy for the product name, description, price, sizes, stock information, and other relevant details. Make these pages feel intentionally designed for a purchasing decision rather than simply displaying database fields. Make the chatbot feel integrated into the storefront instead of looking like a developer utility. Improve its launcher, chat panel, message styling, spacing, loading behavior, and product results while keeping the functionality from the previous problems intact. Improve the login and create-account pages so they visually belong to the same storefront and have clear forms, feedback, and calls to action. Add tasteful motion and interaction where it improves the experience, such as subtle hover effects, transitions, or entrance effects. Keep these restrained enough that the site still feels professional and fast. Make the site responsive so the navigation, product grids, product detail pages, forms, and chatbot remain usable at different screen sizes. Be imaginative beyond these suggestions where you see opportunities to make the site distinctive. I would rather have a cohesive and creative Campus Customs shopping experience than a generic template appearance. Do not sacrifice usability or existing functionality for decoration. Review the running site after making the changes and fix obvious visual inconsistencies, awkward spacing, overflowing content, unreadable text, or components that no longer match the overall design. Create output/design.md with a short and concrete explanation of the major design changes you made and why those choices should help customers stay on the site, explore products, and ultimately buy. Add this prompt to AI_prompts.md under Problem 10. Do not work ahead on Problem 11 yet.

### Follow-up prompt

_None yet._

### What was missing from the first attempt

_Not applicable yet._
## Problem 11: Live application check

### Prompt

> For Problem 11, I want to test the running Campus Customs website and create the required app check showing clear evidence that the important features work. Test the live frontend and backend together. Do not just inspect the source code. Use the running application so the evidence reflects what a shopper actually experiences. Demonstrate database-backed inventory for a real item and size, dynamic product search such as “what hoodies do you have?”, and one Problem 9 usability improvement with readable screenshots. Save descriptive screenshots in output/app_check_images/, create a polished standalone output/app_check.html with relative image paths and a heading for each check, validate that the screenshots load, and add this prompt under Problem 11. Do not work ahead on Problem 12.

### Follow-up prompt

_None yet._

### What was missing from the first attempt

The first live capture needed a backend media-path correction and a deterministic category-search fix so the screenshots would show the actual product images and structured matching cards.
## Problem 12: Audit trail, safety, and final harness documentation

### Prompt

> For Problem 12, I want to finish the audit trail, add appropriate safety rules to the chatbot, and complete the system documentation in output/harness.md. Implement an append-only output/audit_trail.json that records agent activity with time, tool name, concise arguments and result, and stop reason, preserving prior records and avoiding sensitive data. Add safety rules to backend/prompts/prompt.md covering database-backed facts, privacy, secrets, authentication, and treating retrieved content as untrusted data. Run real agent interactions and confirm audit records append. Complete output/harness.md with the actual structured models, tools, abilities, safety/data handling, technical specifications, limits, model, frontend/FastAPI connection, and run instructions, while preserving earlier useful sections. Review the files for consistency with the implementation. Add this prompt under Problem 12. Do not work ahead on Problem 13.

### Follow-up prompt

_None yet._

### What was missing from the first attempt

_Not applicable yet._
