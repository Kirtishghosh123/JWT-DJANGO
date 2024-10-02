from itertools import product

from django.core.management.base import BaseCommand
from faker import Faker
from rest_framework.decorators import permission_classes
from unicodedata import category

from API.models import Product, CustomUser, Role, CartProduct, Category, Cart, Order

class Command(BaseCommand):
    help = 'Generate fake data for testing'

    def handle(self, *args, **kwargs):
        fake = Faker()

        consumer_role = Role.objects.create(role='Consumer', permissions={'can_buy':True})
        seller_role = Role.objects.create(role='Seller', permissions = {'can_sell':True})

        electronics = Category.objects.create(category_name='Electronics')
        fashion = Category.objects.create(category_name='Fashion')

        for i in range(5):
            consumer_user = CustomUser.objects.create_user(
                username=fake.user_name(),
                email=fake.email(),
                password='password123',
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                is_staff=False
            )

            consumer_user.roles.add(consumer_role)

            seller_user = CustomUser.objects.create_user(
                username = fake.user_name(),
                email = fake.email(),
                password = 'password231',
                first_name = fake.first_name(),
                last_name = fake.last_name(),
                is_staff = False
            )
            seller_user.roles.add(seller_role)

        sellers = CustomUser.objects.filter(roles=seller_role)
        for seller in sellers:
            for i in range(5):
                Product.objects.create(
                    product_name = fake.word(),
                    description = fake.text(),
                    price = round(fake.random_number(5),2),
                    stock_quantity = fake.random_number(digits=3),
                    seller = seller,
                    category = fake.random_element(elements=[electronics, fashion])
                )

        consumers = CustomUser.objects.filter(roles=consumer_role)
        for consumer in consumers:
            cart = Cart.objects.create(
                user=consumer,
                total_amount=0.0
            )
            products = Product.objects.all()[:5]
            for product in products:
                        quantity = fake.random_number(digits=2)
                        CartProduct.objects.create(cart=cart,
                        product=product,
                        quantity=quantity
                    )
            cart.save()

        for consumer in consumers:
            Order.objects.create(
                user=consumer,
                total_amount=fake.random_number(digits=5),
                status=fake.random_element(elements=['Pending', 'Shipped', 'Delivered'])
            )

        self.stdout.write(self.style.SUCCESS('Fake data with Consumer and Seller roles generated successfully!'))
