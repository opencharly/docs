---
title: Risk Driven Development & Agent Driven Evaluation
description: Prove the riskiest assumption first; write down what "good" means and have an agent taste it.
sidebar:
  order: 4
---

Two co-equal disciplines. One decides *what to prove first*; the other decides *what correct
means*.

## Risk Driven Development

> **Taste every candy before making the recipe.** The riskiest question — *do these candies
> actually melt together the way I think they do* — gets proven on a real, disposable candybox
> first. Reality is the only ground truth.
>
> — [tenet 5](/vision/)

Documentation and code are hypotheses. When being wrong would invalidate the plan, the assumption
gets proven on a live disposable bed **before** the work is designed around it. The archetypal
unknown is composition at latest versions: does this actually build, together, today?

The instrument is a **spike** — small, time-boxed, thrown away once it has answered the question.
Only the knowledge is kept, never the batch. A spike finds out *how*; it never decides *whether*,
and it never shrinks the work.

When a bed contradicts a document, the document is wrong and gets fixed the same day. That rule
is why this site is generated: a page projected from the source cannot disagree with it.

## Agent Driven Evaluation

> **Write down what "good" means, and have an agent taste it.** The plan's deterministic `check:`
> steps verify the measurable; for the subtle "is it actually right?" an `agent-check:` step has
> an agent taste the live batch and judge.
>
> — [tenet 6](/vision/)

Every candy ships a `plan:` — a runnable acceptance spec, baked into the image and executable
against a live deployment. You can read it on every candy's page in the
[candy reference](/reference/candy/ripgrep/).

Steps carry an explicit intent:

| Intent | Meaning |
|---|---|
| `run:` | changes state |
| `check:` | an idempotent probe — deterministic, and the mandatory minimum |
| `agent-run:` | an agent-performed action |
| `agent-check:` | an agent grades the live deployment; an unparseable or timed-out grader **fails** the step |
| `include:` | compose another entity's plan |

The important property is that the spec is not a document *about* the candy — it is the test, and
it runs.

## Together

RDD proves the risky assumptions a behavior rests on. ADE pins down what correct behavior *is*
and grades the running system against it. The first keeps you from building on a guess; the
second keeps "it works" from being an opinion.

## See also

- **[The check verb reference](/recipes/check/check/)** — every probe verb and the bed model.
- **[Candyboxing](/concepts/candyboxing/)** — why running these beds is cheap enough to do constantly.
