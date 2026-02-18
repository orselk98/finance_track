import csv
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from expenses.models import Transaction


class Command(BaseCommand):
    help = 'Export transactions to a CSV file with optional filters'

    def add_arguments(self, parser):
        parser.add_argument(
            '-o', '--output',
            type=str,
            default='transactions.csv',
            help='Output file path (default: transactions.csv)',
        )
        parser.add_argument(
            '--category',
            type=str,
            help='Filter by category name',
        )
        parser.add_argument(
            '--start-date',
            type=str,
            help='Filter transactions on or after this date (YYYY-MM-DD)',
        )
        parser.add_argument(
            '--end-date',
            type=str,
            help='Filter transactions on or before this date (YYYY-MM-DD)',
        )

    def handle(self, *args, **options):
        qs = Transaction.objects.select_related('category').all()

        if options['category']:
            qs = qs.filter(category__name=options['category'])

        if options['start_date']:
            try:
                start = datetime.strptime(options['start_date'], '%Y-%m-%d').date()
                qs = qs.filter(date__gte=start)
            except ValueError:
                raise CommandError('Invalid start-date format. Use YYYY-MM-DD.')

        if options['end_date']:
            try:
                end = datetime.strptime(options['end_date'], '%Y-%m-%d').date()
                qs = qs.filter(date__lte=end)
            except ValueError:
                raise CommandError('Invalid end-date format. Use YYYY-MM-DD.')

        qs = qs.order_by('-date')

        if not qs.exists():
            self.stderr.write(self.style.WARNING('No transactions found matching the given filters.'))
            return

        output_path = options['output']
        with open(output_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'description', 'amount', 'date', 'category'])
            for t in qs:
                writer.writerow([t.id, t.description, t.amount, t.date, t.category.name])

        count = qs.count()
        self.stdout.write(self.style.SUCCESS(f'Exported {count} transactions to {output_path}'))
