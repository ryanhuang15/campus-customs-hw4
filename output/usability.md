# Usability Improvements

## 1. Product search and filtering

The Products page now supports text search across product names and descriptions, plus garment-type and color filters. This helps shoppers browse the catalogue directly and gives the business a clearer, lower-friction path to merchandise discovery.

## 2. Loading, empty, and error feedback

The frontend now shows a loading indicator while products load, a retry message when the catalogue request fails, a clear empty state when filters find no pieces, and visible chatbot loading/error messages. Shoppers can tell what the site is doing and what to try next.

## 3. Clarification for ambiguous product questions

When a factual price or stock question matches multiple catalogue products, the agent names several likely matches and asks which one the shopper means instead of guessing. This protects answer accuracy while keeping the conversation useful.

## 4. Efficient and reliable product searches

Catalogue rows and ranked search results are cached in the backend to reduce repeated SQLite reads. Chat failures are caught and returned as a helpful structured response, with safe catalogue matches preserved when available, so a temporary model/tool problem does not break the chat experience.
