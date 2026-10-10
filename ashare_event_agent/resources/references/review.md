# Post-close review

Review exists to improve future premarket recall and selection, not to make the finished market look inevitable.

Start from the immutable frozen cassette. Reconcile all outcome pools and counts. Attribute every in-scope limit-up, plus broken boards, limit-downs and key non-winners.

Post-close attribution may not self-report premarket membership. `in_u0` and `in_u1` must reconcile against the frozen RecallPool; a ticker cannot be placed into mutually exclusive limit-up / broken-board / limit-down attribution sets at the same time, and those sets must reconcile to the corresponding MarketOutcome result classes.

Recall grading is derived from attribution, not typed independently: the in-scope actual-limit-up denominator, knowable count, U0 hits and U1 hits must mechanically reconcile to the attributed frozen records before a grade can pass.

Classify misses by the earliest failed layer: source, event, industry, mapping, role/ranking, timing, or unknowable. `G_UNKNOWABLE` is only legal when the fact was genuinely not knowable before freeze; a HIT must have been knowable and present in frozen U0.

Keep premarket evidence and post-close facts in separate fields. Never use a post-close fact to prove a premarket thesis.
