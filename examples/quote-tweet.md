Anthropic's Dario Amodei just mass-published the
internal evals framework they use before every Claude release.

The part nobody's talking about: they now include "character
evaluations" — testing whether the model stays consistent under
adversarial pressure, not just whether it can code or do math.

"We don't want a model that's brilliant but unreliable.
Consistency of character is a safety property." — Amodei

This is where it gets interesting for anyone building on top of
LLMs. If the foundation model provider is testing for
*behavioral stability*, that changes what you can assume about
the API you're calling.

Full breakdown in our analysis →
