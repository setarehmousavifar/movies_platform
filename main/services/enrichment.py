"""AI / NLP enrichment for catalog synopsis (local extractive + optional OpenAI)."""

from __future__ import annotations

import json
import logging
import re
from collections import Counter

from decouple import config
from django.db import transaction
from django.utils import timezone as dj_timezone

from main.models import Animation, Movie, Series, Tag

logger = logging.getLogger('main.enrichment')

STOPWORDS = {
    'the', 'a', 'an', 'and', 'or', 'of', 'to', 'in', 'on', 'for', 'with', 'is', 'are',
    'was', 'were', 'be', 'as', 'by', 'at', 'from', 'that', 'this', 'it', 'its', 'into',
    'their', 'his', 'her', 'they', 'them', 'but', 'not', 'have', 'has', 'had', 'will',
}


class EnrichmentService:
    @staticmethod
    def _tokenize(text: str) -> list[str]:
        return re.findall(r"[A-Za-z0-9']+", (text or '').lower())

    @classmethod
    def local_summary(cls, title: str, description: str, max_sentences: int = 2) -> str:
        text = (description or '').strip()
        if not text:
            return f'{title}: no synopsis available.'
        sentences = re.split(r'(?<=[.!?])\s+', text)
        chosen = [s.strip() for s in sentences if s.strip()][:max_sentences]
        summary = ' '.join(chosen) if chosen else text[:240]
        return summary[:500]

    @classmethod
    def local_tags(cls, title: str, description: str, limit: int = 8) -> list[str]:
        tokens = [
            t for t in cls._tokenize(f'{title} {description}')
            if t not in STOPWORDS and len(t) > 2
        ]
        counts = Counter(tokens)
        return [w for w, _ in counts.most_common(limit)]

    @classmethod
    def openai_enrich(cls, title: str, description: str) -> tuple[str, list[str]] | None:
        api_key = config('OPENAI_API_KEY', default='')
        if not api_key:
            return None
        try:
            import urllib.request

            payload = {
                'model': config('OPENAI_MODEL', default='gpt-4o-mini'),
                'messages': [
                    {
                        'role': 'system',
                        'content': (
                            'Return JSON with keys summary (string, max 2 sentences) '
                            'and tags (array of up to 8 short keywords).'
                        ),
                    },
                    {
                        'role': 'user',
                        'content': f'Title: {title}\nSynopsis: {description}',
                    },
                ],
                'temperature': 0.2,
            }
            req = urllib.request.Request(
                'https://api.openai.com/v1/chat/completions',
                data=json.dumps(payload).encode('utf-8'),
                headers={
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json',
                },
                method='POST',
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                body = json.loads(resp.read().decode('utf-8'))
            content = body['choices'][0]['message']['content']
            parsed = json.loads(content)
            summary = str(parsed.get('summary', '')).strip()
            tags = [str(t).strip().lower() for t in parsed.get('tags', []) if str(t).strip()]
            if summary and tags:
                return summary, tags[:8]
        except Exception:  # noqa: BLE001
            logger.exception('OpenAI enrichment failed; falling back to local')
        return None

    @classmethod
    @transaction.atomic
    def enrich_instance(cls, instance, force: bool = False):
        if instance.ai_enriched_at and not force:
            return instance

        openai_result = cls.openai_enrich(instance.title, instance.description)
        if openai_result:
            summary, tags = openai_result
            provider = 'openai'
        else:
            summary = cls.local_summary(instance.title, instance.description)
            tags = cls.local_tags(instance.title, instance.description)
            provider = 'local'

        instance.ai_summary = summary
        instance.ai_tags = tags
        instance.ai_enriched_at = dj_timezone.now()
        instance.save(update_fields=['ai_summary', 'ai_tags', 'ai_enriched_at'])

        if hasattr(instance, 'tags'):
            for name in tags:
                tag, _ = Tag.objects.get_or_create(name=name[:50])
                instance.tags.add(tag)

        logger.info(
            'enriched type=%s id=%s provider=%s tags=%s',
            instance.__class__.__name__,
            instance.pk,
            provider,
            len(tags),
        )
        return instance

    @classmethod
    def enrich_movie(cls, movie_id: int, force: bool = False):
        movie = Movie.objects.get(pk=movie_id)
        return cls.enrich_instance(movie, force=force)

    @classmethod
    def enrich_series(cls, series_id: int, force: bool = False):
        series = Series.objects.get(pk=series_id)
        return cls.enrich_instance(series, force=force)

    @classmethod
    def enrich_animation(cls, animation_id: int, force: bool = False):
        animation = Animation.objects.get(pk=animation_id)
        return cls.enrich_instance(animation, force=force)
