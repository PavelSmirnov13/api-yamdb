import csv
from django.core.management.base import BaseCommand
from reviews.models import Category, Genre, Title


class Command(BaseCommand):
    help = 'Импорт данных из CSV-файлов в базу данных'

    def handle(self, *args, **kwargs):
        # Импорт категорий
        with open('static/data/category.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                Category.objects.get_or_create(
                    id=row['id'],
                    name=row['name'],
                    slug=row['slug']
                )
        self.stdout.write(self.style.SUCCESS('✅ Категории импортированы'))

        # Импорт жанров
        with open('static/data/genre.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                Genre.objects.get_or_create(
                    id=row['id'],
                    name=row['name'],
                    slug=row['slug']
                )
        self.stdout.write(self.style.SUCCESS('✅ Жанры импортированы'))

        # Импорт произведений
        with open('static/data/titles.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                category = Category.objects.get(id=row['category'])
                Title.objects.get_or_create(
                    id=row['id'],
                    name=row['name'],
                    year=row['year'],
                    description=row.get('description', ''),
                    category=category
                )
        self.stdout.write(self.style.SUCCESS('✅ Произведения импортированы'))

        try:
            with open(
                'static/data/genre_title.csv',
                'r', encoding='utf-8'
            ) as file:
                reader = csv.DictReader(file)
                count = 0
                for row in reader:
                    title = Title.objects.get(id=row['title_id'])
                    genre = Genre.objects.get(id=row['genre_id'])
                    title.genre.add(genre)
                    count += 1
            self.stdout.write(self.style.SUCCESS(
                f'Связи жанров с произведениями добавлены: {count}'))
        except FileNotFoundError:
            self.stdout.write(
                self.style.WARNING('Файл genre_title.csv не найден'))

        self.stdout.write(self.style.SUCCESS('Импорт завершён!'))
