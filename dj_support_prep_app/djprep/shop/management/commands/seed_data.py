import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from faker import Faker
from shop.models import Category, Product, Order, OrderItem


class Command(BaseCommand):
    help = 'Seeds the database with sample data for practice'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=100,
            help='Number of users to create'
        )
        parser.add_argument(
            '--products',
            type=int,
            default=1000,
            help='Number of products to create'
        )
        parser.add_argument(
            '--orders',
            type=int,
            default=500,
            help='Number of orders to create'
        )

    def handle(self, *args, **options):
        fake = Faker()

        self.stdout.write('Creating categories...')
        categories = self._create_categories()

        self.stdout.write(f'Creating {options["users"]} users...')
        users = self._create_users(fake, options['users'])

        self.stdout.write(f'Creating {options["products"]} products...')
        products = self._create_products(fake, categories, users, options['products'])

        self.stdout.write(f'Creating {options["orders"]} orders...')
        self._create_orders(fake, users, products, options['orders'])

        self.stdout.write(self.style.SUCCESS('Done!'))

    def _create_categories(self):
        parent_categories = [
            'Electronics', 'Clothing', 'Home & Garden', 'Sports',
            'Books', 'Toys', 'Food & Beverages', 'Health', 'Automotive', 'Office'
        ]

        categories = []
        for name in parent_categories:
            cat, _ = Category.objects.get_or_create(name=name, parent=None)
            categories.append(cat)

        subcategories = {
            'Electronics': ['Phones', 'Laptops', 'Tablets', 'Cameras', 'Audio'],
            'Clothing': ['Men', 'Women', 'Kids', 'Shoes', 'Accessories'],
            'Home & Garden': ['Furniture', 'Kitchen', 'Decor', 'Garden Tools'],
            'Sports': ['Fitness', 'Outdoor', 'Team Sports', 'Water Sports'],
        }

        for parent_name, subs in subcategories.items():
            parent = Category.objects.get(name=parent_name)
            for sub_name in subs:
                cat, _ = Category.objects.get_or_create(name=sub_name, parent=parent)
                categories.append(cat)

        return categories

    def _create_users(self, fake, count):
        users = list(User.objects.all())

        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin')

        existing = User.objects.count()
        to_create = max(0, count - existing)

        for _ in range(to_create):
            username = fake.user_name() + str(random.randint(1000, 9999))
            user = User.objects.create_user(
                username=username,
                email=fake.email(),
                password='testpass123'
            )
            users.append(user)

        return list(User.objects.all())

    def _create_products(self, fake, categories, users, count):
        existing = Product.objects.count()
        to_create = max(0, count - existing)

        products = []
        for _ in range(to_create):
            product = Product.objects.create(
                name=fake.catch_phrase(),
                description=fake.paragraphs(nb=5, ext_word_list=None),
                price=round(random.uniform(9.99, 999.99), 2),
                category=random.choice(categories),
                created_by=random.choice(users),
            )
            products.append(product)

        return list(Product.objects.all())

    def _create_orders(self, fake, users, products, count):
        statuses = ['pending', 'processing', 'shipped', 'delivered', 'cancelled']

        existing = Order.objects.count()
        to_create = max(0, count - existing)

        for _ in range(to_create):
            order = Order.objects.create(
                user=random.choice(users),
                status=random.choice(statuses),
            )

            num_items = random.randint(1, 8)
            order_products = random.sample(products, min(num_items, len(products)))

            for product in order_products:
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=random.randint(1, 5),
                    price=product.price,
                )
