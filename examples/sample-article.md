# How We Cut Template Sprawl from 30 to 9

Last month our team shipped a framework for structuring AI-agent workflows.
The result: 30 templates collapsed to 9, and error rates dropped from 41% to 11%.

## The Core Insight

Most template bloat comes from encoding context that belongs in the prompt, not the template.
We moved context-dependent logic into system prompts and kept templates purely structural.

## Key Rules

1. One template per *outcome*, not per *variation*
2. Never hardcode names, dates, or project-specific data in templates
3. Every template must have a test (input → expected structure)
4. If two templates share >60% of content, merge them

## Results

- 30 → 9 templates (70% reduction)
- Error rate: 41% → 11%
- Saved ~1h 53m per week in template maintenance
- Zero missed edge cases after migration

## Conclusion

Template sprawl isn't a content problem — it's an architecture problem.
Fix the structure and the content takes care of itself.
