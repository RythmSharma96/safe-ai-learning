from django.core.management.base import BaseCommand

from safety.models import FlagCategory

CATEGORIES = [
    ("self_harm", "Self-harm or harm-related content"),
    ("sexual_content", "Sexual or inappropriate content for minors"),
    ("pii_request", "Requests for or sharing of personal contact information"),
    ("manipulation", "Manipulative or emotionally risky guidance"),
    ("harm_content", "Violence or harmful content"),
    ("moderation_unavailable", "Moderation checker failed — flagged for manual review"),
]


class Command(BaseCommand):
    help = "Seed the FlagCategory table with the canonical set of categories"

    def handle(self, *args, **options):
        for name, description in CATEGORIES:
            _, created = FlagCategory.objects.get_or_create(
                name=name, defaults={"description": description}
            )
            status = "created" if created else "exists"
            self.stdout.write(f"  {name}: {status}")
        self.stdout.write(self.style.SUCCESS("Flag categories seeded."))
