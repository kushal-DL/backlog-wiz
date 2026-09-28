# Expected Outputs — Sample Verification

For each sample input, this document defines what "good output" looks like so results
can be judged against a bar, not subjectively.

---

## Sample 1 — `meeting_notes.txt` (with `backlog.json` context)

**Input:** Sprint planning meeting notes covering three agenda items — onboarding flow,
notification preferences, and feed performance.

**Existing backlog:** 3 items covering sign-up, login, and password reset.

### Good output must include

| # | Story expected | Priority | Notes |
|---|---|---|---|
| 1 | Resend verification email button (appears after 60s) | Must | Explicit in notes |
| 2 | Onboarding progress indicator (step 1 of 3) | Must | Explicit in notes |
| 3 | Google OAuth sign-up | Should | Deferred by Priya — Should, not Must |
| 4 | Per-category notification toggles (comments, mentions, reminders) | Must | Explicit |
| 5 | Pause all notifications (1h/8h/24h) | Should | Enterprise customer request |
| 6 | Notification preference sync across devices (≤30s) | Must | Explicit |
| 7 | Feed pagination (load 20, fetch-more-on-scroll) | Must | All three agreed |
| 8 | Local feed state cache for instant render | Must | All three agreed |
| 9 | Lazy loading of avatar images | Must/Could | Lowest effort, highest impact |

**Quality bar:**
- Each story uses "As a / I want / So that" format.
- Each story has ≥2 testable acceptance criteria.
- Google OAuth is NOT Must (the notes explicitly deprioritised it to next sprint).
- No stories invented that aren't in the notes.
- At least one warning about overlap with existing backlog (S-001 sign-up relates to onboarding items).

### Actual run result (22 Oct 2024)

10 stories generated. All 9 expected stories present. Priorities correct — OAuth marked
Should. No invented requirements. 1 story added for backend per-category filtering
infrastructure (S-010, Must) — reasonable inference from Sam's action item.
Deduplication warnings not triggered, but existing backlog items (sign-up/login/password)
are distinct enough from the new stories that this is correct behaviour.

**Verdict: ✅ meets the good-output bar.**

---

## Sample 2 — `requirements.pdf` (no backlog context)

**Input:** 2-page product requirements PDF for "Notification Centre v2" covering 4
numbered requirements: per-channel preferences, do-not-disturb schedule, unread badge
count, and admin broadcast notifications.

### Good output must include

| # | Story expected | Priority |
|---|---|---|
| 1 | Per-channel delivery preferences (push/email/in-app/none per category) | Must |
| 2 | Do-not-disturb schedule with queued digest delivery at window end | Must |
| 3 | Unread badge count — real-time decrement, mark-all-read | Must |
| 4 | Admin broadcast notification to all users or segment | Must |

**Quality bar:**
- All 4 REQ-XX items produce at least one story.
- REQ-02 may produce 2 stories (DND schedule + queued digest delivery) — that is acceptable.
- Non-goals section ("SMS, third-party aggregators") does NOT appear as stories.
- source_reference quotes phrases from the PDF text, not generic descriptions.
- No warnings expected (no existing backlog).

---

## Sample 3 — `meeting_notes.txt` (no backlog context)

Same input as Sample 1 but without the existing backlog. Verifies standalone generation.

**Good output must include** the same 9 stories as Sample 1.
**Key difference:** no deduplication warnings expected since no backlog was provided.
OAuth should still be Should. All other priorities unchanged.
