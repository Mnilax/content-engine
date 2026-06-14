"""Content format generators."""

from .quote_tweet import SYSTEM_PROMPT as QUOTE_TWEET_PROMPT, build_user_prompt as quote_tweet_prompt
from .thread import SYSTEM_PROMPT as THREAD_PROMPT, build_user_prompt as thread_prompt
from .qrt import SYSTEM_PROMPT as QRT_PROMPT, build_user_prompt as qrt_prompt
from .summary_card import SYSTEM_PROMPT as SUMMARY_CARD_PROMPT, build_user_prompt as summary_card_prompt

FORMAT_REGISTRY = {
    "quote": {
        "name": "Quote Tweet",
        "system_prompt": QUOTE_TWEET_PROMPT,
        "build_prompt": quote_tweet_prompt,
    },
    "thread": {
        "name": "Thread",
        "system_prompt": THREAD_PROMPT,
        "build_prompt": thread_prompt,
    },
    "qrt": {
        "name": "QRT (Quote Retweet)",
        "system_prompt": QRT_PROMPT,
        "build_prompt": qrt_prompt,
    },
    "card": {
        "name": "Summary Card",
        "system_prompt": SUMMARY_CARD_PROMPT,
        "build_prompt": summary_card_prompt,
    },
}
