"""Enrich catalog items with local (or OpenAI) AI summary/tags."""

from django.core.management.base import BaseCommand

from main.models import Animation, Movie, Series
from main.services import EnrichmentService


class Command(BaseCommand):
    help = 'Enrich movies/series/animations with ai_summary and ai_tags'

    def add_arguments(self, parser):
        parser.add_argument('--force', action='store_true', help='Re-enrich even if already done')
        parser.add_argument('--limit', type=int, default=50, help='Max items per type')

    def handle(self, *args, **options):
        force = options['force']
        limit = options['limit']
        total = 0
        for model, label in (
            (Movie, 'movie'),
            (Series, 'series'),
            (Animation, 'animation'),
        ):
            qs = model.objects.all().order_by('id')[:limit]
            for item in qs:
                EnrichmentService.enrich_instance(item, force=force)
                total += 1
                self.stdout.write(f'enriched {label} id={item.pk} title={item.title}')
        self.stdout.write(self.style.SUCCESS(f'Done. Enriched {total} items.'))
