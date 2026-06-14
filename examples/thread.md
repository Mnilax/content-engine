🧵 Anthropic just open-sourced their model eval framework.

Here's what matters for builders — a thread.

1/ They evaluate on 4 axes: capability, safety, character, and
alignment. Most labs only publish capability benchmarks.

2/ "Character evaluations" test whether Claude maintains
consistent behavior under adversarial prompts. Think: jailbreak
resistance as a measurable metric.

3/ The safety evals include real-world deployment scenarios —
not just toy examples. Medical advice, legal questions,
financial guidance.

4/ Key insight: they found that capability and safety aren't
always in tension. Some safety improvements *also* improved
task performance.

5/ What this means for developers: you can now run the same
evals on your fine-tuned models. The framework is Apache 2.0.

Full analysis in our latest piece →
