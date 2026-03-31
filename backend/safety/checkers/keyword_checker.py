import re

from .base import CheckResult, SafetyChecker

# --- Pattern definitions ---

# PII: Detect both sharing and requesting personal contact info
_EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
_PHONE_PATTERN = re.compile(
    r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}"
)
_PII_REQUEST_PATTERNS = re.compile(
    r"(?:what(?:'s| is) your (?:phone|number|email|address|name))"
    r"|(?:where do you live)"
    r"|(?:give me your (?:number|email|address|phone))"
    r"|(?:my (?:phone|email|address) is)"
    r"|(?:i live at)"
    r"|(?:my (?:snapchat|instagram|tiktok|discord|whatsapp) is)"
    r"|(?:add me on)"
    r"|(?:here(?:'s| is) my (?:number|email|address|phone))",
    re.IGNORECASE,
)

# Self-harm keywords and phrases
_SELF_HARM_PATTERNS = re.compile(
    r"\b(?:"
    r"(?:want to |wanna |going to |gonna )?(?:kill myself|end (?:my |it all|everything))"
    r"|(?:want to |wanna )?(?:hurt myself|harm myself|cut myself)"
    r"|(?:i (?:don'?t |do not )?want to (?:live|be alive|exist))"
    r"|(?:suicid(?:e|al))"
    r"|(?:self[- ]?harm)"
    r"|(?:better off dead)"
    r"|(?:no reason to live)"
    r"|(?:wish i (?:was|were) dead)"
    r"|(?:i(?:'m| am) (?:going to |gonna )?(?:die|disappear))"
    r")\b",
    re.IGNORECASE,
)

# Sexual / inappropriate content for minors
_SEXUAL_CONTENT_PATTERNS = re.compile(
    r"\b(?:"
    r"(?:sex(?:ual)?(?:ly)?)"
    r"|(?:porn(?:ography)?)"
    r"|(?:nude|naked|nudes)"
    r"|(?:genitals?|penis|vagina)"
    r"|(?:intercourse)"
    r"|(?:masturbat(?:e|ion|ing))"
    r"|(?:orgasm)"
    r"|(?:erotic)"
    r"|(?:sexually (?:explicit|arousing))"
    r"|(?:send (?:me )?(?:pics|pictures|photos))"
    r")\b",
    re.IGNORECASE,
)

# Manipulation / emotionally risky guidance
_MANIPULATION_PATTERNS = re.compile(
    r"(?:don'?t tell (?:your |any(?:one|body) |the )(?:parents?|teacher|mom|dad|family|adult))"
    r"|(?:this is (?:our|a) secret)"
    r"|(?:keep (?:this|it) (?:between us|a secret))"
    r"|(?:you can (?:only )?trust (?:only )?me)"
    r"|(?:no one (?:else )?(?:cares|understands|loves you))"
    r"|(?:(?:your |the )?(?:parents?|teacher|adults?) (?:don'?t|do not) (?:care|love|understand))"
    r"|(?:run away (?:from home|with me))"
    r"|(?:i(?:'m| am) the only (?:one|person))",
    re.IGNORECASE,
)


class KeywordChecker(SafetyChecker):
    """Fast, deterministic keyword/regex-based safety checker.

    Layer 1 in the safety pipeline. Catches obvious patterns
    with zero external dependency and zero cost.
    """

    @property
    def name(self) -> str:
        return "keyword"

    def check(self, content: str) -> CheckResult:
        if not content or not content.strip():
            return CheckResult(is_flagged=False)

        normalized = " ".join(content.lower().split())
        categories = []
        reasons = []
        raw_scores = {}

        # Check PII
        pii_matches = self._check_pii(content, normalized)
        if pii_matches:
            categories.append("pii_request")
            reasons.append(
                f"Personal contact information detected: {', '.join(pii_matches)}"
            )
            raw_scores["pii_matches"] = pii_matches

        # Check self-harm
        self_harm_matches = _SELF_HARM_PATTERNS.findall(normalized)
        if self_harm_matches:
            categories.append("self_harm")
            reasons.append("Self-harm or harm-related content detected")
            raw_scores["self_harm_matches"] = self_harm_matches

        # Check sexual content
        sexual_matches = _SEXUAL_CONTENT_PATTERNS.findall(normalized)
        if sexual_matches:
            categories.append("sexual_content")
            reasons.append("Sexual or inappropriate content for minors detected")
            raw_scores["sexual_matches"] = sexual_matches

        # Check manipulation
        manipulation_matches = _MANIPULATION_PATTERNS.findall(normalized)
        if manipulation_matches:
            categories.append("manipulation")
            reasons.append("Manipulative or emotionally risky content detected")
            raw_scores["manipulation_matches"] = manipulation_matches

        return CheckResult(
            is_flagged=len(categories) > 0,
            categories=categories,
            reasons=reasons,
            raw_scores=raw_scores,
        )

    def _check_pii(self, original: str, normalized: str) -> list[str]:
        """Check for PII patterns in both original and normalized content."""
        matches = []

        if _EMAIL_PATTERN.search(original):
            matches.append("email address")

        if _PHONE_PATTERN.search(original):
            # Avoid false positives on short numbers in math context
            phone_match = _PHONE_PATTERN.search(original)
            if phone_match and len(phone_match.group().replace(" ", "")) >= 7:
                matches.append("phone number")

        if _PII_REQUEST_PATTERNS.search(normalized):
            matches.append("personal info request")

        return matches
