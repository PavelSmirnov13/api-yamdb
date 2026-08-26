import csv

from django.core.management.base import BaseCommand

from reviews.models import Category, Genre, Title


class Command(BaseCommand):
    """Команда импорта данных из CSV-файлов в базу данных."""

    help = 'Импорт данных из CSV-файлов в базу данных'

    def handle(self, *args, **kwargs):
        """Импортирует категории, жанры и произведения."""
        self.import_categories()
        self.import_genres()
        self.import_titles()
        self.import_genre_title_relations()
        self.stdout.write(self.style.SUCCESS('Импорт завершён!'))

    def import_categories(self):
        """Импортирует категории из CSV."""
        with open('static/data/category.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                Category.objects.get_or_create(
                    id=row['id'],
                    defaults={
                        'name': row['name'],
                        'slug': row['slug'],
                    }
                )
        self.stdout.write(self.style.SUCCESS('Категории импортированы'))

    def import_genres(self):
        """Импортирует жанры из CSV."""
        with open('static/data/genre.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                Genre.objects.get_or_create(
                    id=row['id'],
                    defaults={
                        'name': row['name'],
                        'slug': row['slug'],
                    }
                )
        self.stdout.write(self.style.SUCCESS('Жанры импортированы'))

    def import_titles(self):
        """Импортирует произведения из CSV."""
        with open('static/data/titles.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                category = Category.objects.get(id=row['category'])
                name = row['name']
                Title.objects.get_or_create(
                    id=row['id'],
                    defaults={
                        'name': name,
                        'year': row['year'],
                        'description': row.get('description', ''),
                        'category': category,
                    }
                )
        self.stdout.write(self.style.SUCCESS('Произведения импортированы'))

    def import_genre_title_relations(self):
        """Импортирует связи жанров с произведениями."""
        try:
            file = open(
                'static/data/genre_title.csv',
                'r',
                encoding='utf-8'
            )
        except FileNotFoundError:
            self.stdout.write(
                self.style.WARNING('Файл genre_title.csv не найден')
            )
            return

        with file:
            reader = csv.DictReader(file)
            count = 0
            for row in reader:
                title = Title.objects.get(id=row['title_id'])
                genre = Genre.objects.get(id=row['genre_id'])
                title.genre.add(genre)
                count += 1
            self.stdout.write(
                self.style.SUCCESS(
                    f'Связи жанров с произведениями добавлены: {count}'
                )
            )
