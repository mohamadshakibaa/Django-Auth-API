# Junior Backend Review Checklist

Use this checklist when reviewing the project instead of only reading the code.

## Django / ORM

- [ ] Explain every model relationship.
- [ ] Explain `PROTECT` vs `CASCADE` in this project.
- [ ] Explain why `select_related` is used on products.
- [ ] Explain why `prefetch_related` is used for images/cart/order items.
- [ ] Explain every database index and constraint.
- [ ] Explain migrations and why they are committed.

## Business logic

- [ ] Explain why checkout is in a service function.
- [ ] Explain `transaction.atomic`.
- [ ] Explain `select_for_update`.
- [ ] Explain how overselling is prevented.
- [ ] Explain why order items snapshot product data.
- [ ] Explain why the cart is cleared only inside the checkout transaction.

## DRF

- [ ] Explain ViewSet + Router.
- [ ] Explain serializer validation vs model validation.
- [ ] Explain pagination.
- [ ] Explain filtering/search/ordering.
- [ ] Explain object ownership in order endpoints.
- [ ] Explain JWT access vs refresh tokens.

## Security

- [ ] Never trust `order_id` from the client without checking ownership.
- [ ] Never accept price from the client during checkout.
- [ ] Never calculate order totals from client-supplied totals.
- [ ] Never store raw card data.
- [ ] Use environment variables for secrets.
- [ ] Run `python manage.py check --deploy` before deployment.

## Production

- [ ] PostgreSQL
- [ ] Gunicorn
- [ ] Docker
- [ ] Redis
- [ ] Celery
- [ ] Static/media handling
- [ ] HTTPS
- [ ] Logging
- [ ] Monitoring
- [ ] Database backups
