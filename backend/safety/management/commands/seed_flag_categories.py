from django.core.management.base import BaseCommand

from safety.models import FlagCategory

CATEGORIES = [
    {
        "name": "self_harm",
        "description": "Self-harm or harm-related content",
        "canned_response": (
            "I care about you and want you to be safe. If you're going through a tough time, "
            "please talk to a trusted adult like a parent, teacher, or school counselor. "
            "You can also call Kids Helpline at 1800 55 1800. "
            "I'm here to help you learn — let's focus on something positive together!"
        ),
        "patterns": [
            r"\b(?:(?:want to |wanna |going to |gonna )?(?:kill myself|end (?:my |it all|everything))"
            r"|(?:want to |wanna )?(?:hurt myself|harm myself|cut myself)"
            r"|(?:i (?:don'?t |do not )?want to (?:live|be alive|exist))"
            r"|(?:suicid(?:e|al))"
            r"|(?:self[- ]?harm)"
            r"|(?:better off dead)"
            r"|(?:no reason to live)"
            r"|(?:wish i (?:was|were) dead)"
            r"|(?:i(?:'m| am) (?:going to |gonna )?(?:die|disappear)))\b",
        ],
    },
    {
        "name": "sexual_content",
        "description": "Sexual or inappropriate content for minors",
        "canned_response": (
            "That's not something I'm able to help with. "
            "Let's talk about something fun to learn instead! "
            "Do you have any questions about science, math, history, or another subject?"
        ),
        "patterns": [
            r"\b(?:(?:sex(?:ual)?(?:ly)?)"
            r"|(?:porn(?:ography)?)"
            r"|(?:nude|naked|nudes)"
            r"|(?:genitals?|penis|vagina)"
            r"|(?:intercourse)"
            r"|(?:masturbat(?:e|ion|ing))"
            r"|(?:orgasm)"
            r"|(?:erotic)"
            r"|(?:sexually (?:explicit|arousing))"
            r"|(?:send (?:me )?(?:pics|pictures|photos)))\b",
        ],
    },
    {
        "name": "pii_request",
        "description": "Requests for or sharing of personal contact information",
        "canned_response": (
            "I'm not able to share or receive personal information like phone numbers, "
            "emails, or addresses. This is to keep everyone safe! "
            "Is there a learning topic I can help you with instead?"
        ),
        "patterns": [
            r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
            r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}",
            r"(?:what(?:'s| is) your (?:phone|number|email|address|name))"
            r"|(?:where do you live)"
            r"|(?:give me your (?:number|email|address|phone))"
            r"|(?:my (?:phone|email|address) is)"
            r"|(?:i live at)"
            r"|(?:my (?:snapchat|instagram|tiktok|discord|whatsapp) is)"
            r"|(?:add me on)"
            r"|(?:here(?:'s| is) my (?:number|email|address|phone))",
        ],
    },
    {
        "name": "manipulation",
        "description": "Manipulative or emotionally risky guidance",
        "canned_response": (
            "I want to make sure you stay safe. If anyone ever makes you feel uncomfortable "
            "or asks you to keep secrets from your parents or teachers, please tell a trusted adult. "
            "Now, what would you like to learn about today?"
        ),
        "patterns": [
            r"(?:don'?t tell (?:your |any(?:one|body) |the )(?:parents?|teacher|mom|dad|family|adult))"
            r"|(?:this is (?:our|a) secret)"
            r"|(?:keep (?:this|it) (?:between us|a secret))"
            r"|(?:you can (?:only )?trust (?:only )?me)"
            r"|(?:no one (?:else )?(?:cares|understands|loves you))"
            r"|(?:(?:your |the )?(?:parents?|teacher|adults?) (?:don'?t|do not) (?:care|love|understand))"
            r"|(?:run away (?:from home|with me))"
            r"|(?:i(?:'m| am) the only (?:one|person))",
        ],
    },
    {
        "name": "harm_content",
        "description": "Violence or harmful content",
        "canned_response": (
            "I'm not able to help with that topic. "
            "Let's focus on something positive and educational instead! "
            "What would you like to learn about?"
        ),
        "patterns": [],
    },
    {
        "name": "moderation_unavailable",
        "description": "Moderation checker failed — flagged for manual review",
        "canned_response": (
            "I need a moment — could you try asking your question again? "
            "I'm here to help you learn!"
        ),
        "patterns": [],
    },
]


class Command(BaseCommand):
    help = "Seed the FlagCategory table with the canonical set of categories"

    def handle(self, *args, **options):
        for cat_data in CATEGORIES:
            obj, created = FlagCategory.objects.update_or_create(
                name=cat_data["name"],
                defaults={
                    "description": cat_data["description"],
                    "canned_response": cat_data["canned_response"],
                    "patterns": cat_data["patterns"],
                },
            )
            status = "created" if created else "updated"
            self.stdout.write(f"  {obj.name}: {status}")
        self.stdout.write(self.style.SUCCESS("Flag categories seeded."))
