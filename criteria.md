# Acceptance criteria — FitFindr

Five criteria that say what "working" means for this agent, written in unit 3
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"The agent handles errors"* is an opinion.
*"When search returns nothing, the agent stops before calling the second tool,
in 5 of 5 tries"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter one. A reason that says something about your tools, your loop, or the
data earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

**Two are written for you. You write three.**

---

## 1. A matching query completes all three tools

Given a query that matches at least one listing, the agent completes all three
tool calls and returns a fit card — in at least 4 of 5 tries.

**Why this target:**
<!-- Why 4 of 5 and not 5 of 5? Something about your search, probably —
     "my search is a plain keyword match and some phrasings will miss" is a
     real answer. -->
Two of the three tools call the model on the free tier. One run makes two requests against a 15-per-minute limit, so a rate-limit retry that runs out, or a timeout, can end a try even when the loop logic is correct. The search side is a plain keyword match that needs a scoring word to appear in the listing, so a phrasing the data doesn't use can also miss. 5 of 5 would be asking the network and the free tier for something I don't control.

---

## 2. An impossible query stops before the second tool

Given a query that matches no listings, the agent stops before calling
`suggest_outfit` and returns a message naming what to change — 5 of 5 tries.

**Why this target:**
<!-- Why is 5 of 5 reasonable here when criterion 1 isn't? What's different
     about this path? -->
This path never touches the model. Parsing is regex, `search_listings` is a deterministic filter over local data, and the stop is one `if not session["search_results"]` check in `run_agent`. The same input gives the same output every time, so anything less than 5 of 5 means the branch is broken, not unlucky. The error message is also built from `session["parsed"]` rather than generated, so it always names the budget, the size, or the keywords.

---

## 3. Something about state

<!-- YOU WRITE THIS ONE.

     How would you know that the item your search found is the same item the
     next tool received? Name something countable or observable.

     This is the criterion people find hardest, because state failure doesn't
     look like state failure — it looks like a tool problem. Something that
     compares session["selected_item"] against what actually reached
     suggest_outfit is the shape you're after. -->

Given the matching query from criterion 1, every try that reaches the fit card shows the same item at all three handoffs: `session["selected_item"]["id"]` equals `session["search_results"][0]["id"]`; the title in the trace's `suggest_outfit` input and the title in its `create_fit_card` input are both that item's title; and the fit card states that item's price (e.g. `$24`) and not another listing's — in 5 of 5 tries that complete.


**Why this target:**

Every handoff is plain Python reading and writing the same session dict, with no model in between, so if the wrong item ever reaches a tool, that's a bug in my loop rather than variation. The price check on the fit card is the end-to-end proof: the model can only write the right price if the right dict reached it. I only count tries that complete, because a try that dies on a rate limit says nothing about state; that one is criterion 1's problem.

---

## 4. Something about the fit card

<!-- YOU WRITE THIS ONE.

     The fit card calls a model, so the same input can produce different words
     each time. That's not a bug — it's the nature of the tool. So what would
     make it acceptable?

     Think about what you'd actually be unhappy to see. A caption that never
     mentions the price? Two different items producing the same opening
     sentence? A card longer than a caption anyone would post? Any of those can
     be turned into a number. -->

Running the matching query from criterion 1 five times with caching off, at least 4 of the 5 fit cards are 2 to 4 sentences long and contain both the item's exact price (as `$NN`) and its platform name — and no two of the 5 cards have the same first sentence.


**Why this target:**

The words are supposed to change (TEMPERATURE is 0.9), so I'm scoring the parts that shouldn't change: the facts and the length. I allow 1 miss in 5 because the model sometimes drops a detail or adds a fifth sentence even when the prompt asks, and that would be a prompt-tuning problem rather than a broken tool. The "no repeated first sentence" part is strict on purpose: if two of five cards open the same way at 0.9, then caching is still on or the prompt is forcing a template, and that's exactly the failure `config.py` warns about.

---

## 5. Your choice

<!-- YOU WRITE THIS ONE TOO.

     Pick something you actually care about getting right. Speed, the empty
     wardrobe path, what happens when the model can't be reached, whether the
     search respects a price ceiling — anything, as long as it names a number
     or an observable outcome. -->

**The search respects price and size.** For the query `vintage tee size L under $25`, every listing in `session["search_results"]` has `price <= 25` and a size that matches `L` under the rule in my Tool Inventory (`L`, `L/XL`, or a One Size listing). None of them has size `XL`, `XL (oversized)`, or `XL (fits oversized)` — 5 of 5 tries.


**Why this target:**

The filter is deterministic code over local data, so 5 of 5 is the only honest number. I chose this query because it is built to catch the bug the starter code warns about: `"l" in "xl"` is True, and the data has two XL listings under $25 that mention "vintage" (lst_012 and lst_027). A substring filter would pass the price check and still show them. If either one shows up, my size matching is wrong, and a user who asked for a large gets an extra large.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 4 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 4. Something about the fit card

         The fit card is different every time.

         **Why this target:** ...

         > **Revised in unit 4:** For 5 different items, the 5 fit cards share
         > no opening sentence.
         >
         > **Why revised:** "different" wasn't checkable — two cards that
         > differed by one word still counted. The new version is something I
         > can actually score.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said the empty search stops it 5 of 5 times, but I got 3 of 5,
            so 3 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->
