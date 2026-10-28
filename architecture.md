# Architecture Notes

## 1. Boundaries

- `accounts`: identity and user profile.
- `catalog`: product read/write model and inventory quantity.
- `cart`: temporary customer intent; never used as historical order data.
- `orders`: financial/business record. Order items snapshot the name and price at checkout.
- `payments`: payment state and gateway abstraction boundary. The included provider is intentionally fake.

## 2. Checkout invariants

Checkout must satisfy all of these before creating an order:

1. The cart belongs to the authenticated user.
2. The cart is not empty.
3. Every product is still active.
4. Requested quantity does not exceed current stock.
5. Product rows are locked with `SELECT ... FOR UPDATE`.
6. The order, order items, stock decrements, and cart cleanup happen in one transaction.

If any validation fails, the transaction rolls back.

## 3. Why order snapshots exist

A product is mutable. Its name and price can change after purchase. An order is historical. Therefore `OrderItem` stores:

- product FK for reference
- product_name snapshot
- unit_price snapshot
- quantity
- subtotal

The FK is not enough for audit/history.

## 4. Concurrency

Two users can attempt to buy the last unit simultaneously. The checkout service locks the relevant product rows before checking stock and decrementing it. The products are locked in deterministic primary-key order to reduce deadlock risk when carts contain multiple products.

## 5. API authorization

- Catalog GET endpoints are public for active products.
- Catalog mutations are staff-only.
- Cart endpoints require authentication.
- Order endpoints are always filtered by `request.user`.
- Payment endpoints only allow the owner of the target order.

## 6. Caching

Caching is intentionally not enabled in v1. Once the correctness path is understood, Redis caching can be added to product/category read paths with explicit invalidation on catalog writes.

## 7. Payment gateway

The interface already exists in `apps/payments/gateways.py`:

```python
class PaymentGateway(Protocol):
    def create_payment(self, *, order: Order) -> PaymentResult: ...
```

`pay_order` (in `apps/payments/services.py`) locks the order row, calls the gateway selected by `settings.PAYMENT_GATEWAY`, records the `Payment`, updates the order, and queues the confirmation email with `transaction.on_commit(..., robust=True)`. The included `MockGateway` always succeeds. A real provider is a new class implementing `create_payment`; nothing else needs to change.

The HTTP webhook from the provider must be authenticated/verified, idempotent, and transactionally update payment/order state. Card numbers, CVVs, or raw payment credentials must never be stored by this application.

## 8. Order cancellation and stock release

Checkout decrements stock immediately, so an unpaid order *reserves* stock. To keep abandoned orders from holding stock forever:

- `POST /api/orders/{id}/cancel/` lets the owner cancel an order that is `PENDING` and `UNPAID`.
- `python manage.py expire_pending_orders` cancels unpaid orders older than `PENDING_ORDER_TTL_HOURS` (default 24). Run it from cron or Celery beat.
- Both go through `cancel_order`, which locks the order row, then the product rows in primary-key order (same order as checkout), and releases stock with an `F()` update inside one transaction.
- Paying locks the same order row, so a payment and a cancellation of the same order are serialized and can never both succeed.

## 9. Operational notes

- `GET /api/health/` checks database connectivity for load balancers.
- Logout blacklists the refresh token (`rest_framework_simplejwt.token_blacklist`); refresh tokens are rotated and the old one is blacklisted.
- Login/registration/refresh use the stricter `auth` throttle scope. Throttle counters need a shared cache (`CACHE_URL`) once more than one worker runs.
