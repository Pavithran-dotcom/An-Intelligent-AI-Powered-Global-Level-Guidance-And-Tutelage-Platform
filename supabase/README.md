# GlobalGuru: seed with 56 experts + answers

Load order (Supabase SQL Editor): `supabase/schema.sql`, then `supabase/seed.sql` (safe to re-run).

What was added to your original seed (learners, communities and the 100 questions are untouched):
- 56 experts (users + expert_profiles) across the 10 communities (5-6 per domain), with community memberships
- 257 comments: 205 expert answers (`is_answer = true`, 2-3 per question, 100/100 questions covered) + 52 threaded follow-ups (learner asks, expert replies)
- Matching rows the UI reads: votes, answer_ratings, helpful_votes, reputation_events, badges, notifications
- question_relevance rows computed with your backend's own TF-IDF routing
- posts updated: 63 `answered`, 37 `resolved` (with one accepted answer)

Notes: expert accounts use the same non-loginable placeholder password as the seeded learners. `local_sqlite/globalguru_seeded.db` is an optional SQLite copy for local dev (your original backend/globalguru.db is not overwritten). `experts_roster.csv` lists all experts. All people and organisations are fictional.
