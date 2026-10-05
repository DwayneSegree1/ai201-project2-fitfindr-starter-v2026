# FitFindr

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, every
> command, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> python app.py listings --full -n 6      # read the data (Milestone 1)
> python app.py fields                    # what you can filter on
> python app.py ask 'vintage graphic tee under $30'
> ```
>
> All three tools are stubs, so that last command will do nothing useful yet.
> That's the starting position.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     This is your submission. Fill each section in as you finish the milestone
     it belongs to — don't leave it all to the end.

     Unit 3 asks for the first five sections. Unit 4 adds the five below them.
     Leave the unit 4 sections alone until then; they're here so you know
     what's coming.

     Everything is pasted as TEXT. No screenshots, no images, no video links.
     A typed block of output gets full credit; a picture of the same output
     gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 3 — THE BUILD ═══════════════════════ -->

## What This Does

<!-- Three or four sentences: what a user asks for, and what they get back. -->



---

## Tool Inventory

<!-- Four lines per tool. This is worth 2 points and it's the single most
     common place students lose them.

     "Returns a list" earns NOTHING. The description has to say what is IN
     the list.

     The empty case isn't optional either — it's the thing your loop branches
     on, and if you don't decide it here you'll discover it as a crash in
     Milestone 5. -->

### `search_listings`

- **What it does:** Filters the 40 listings in `data/` by price and size, then ranks what's left by how many of the description's keywords appear in each listing, without calling the model.
- **Inputs:** <!-- name and type each: `max_price` (float), not "a price" -->
  - `description` (str): keywords such as `"vintage graphic tee"`. It is lowercased and split on spaces. A listing scores 1 point for each keyword that appears as a whole word in its `title`, `description`, `category`, `style_tags`, `colors`, or `brand`.
  - `size` (str or None): `None` skips the size filter. Otherwise it is a match when the requested size equals the listing's whole size, or one part of it, ignoring case. Parts are split on `/` and spaces, and anything in parentheses is dropped. So `"M"` matches `"S/M"` and `"M/L"`, `"XL"` matches `"XL (oversized)"`, `"L"` does **not** match `"XL"`, and `"S"` does **not** match `"US 9"`. Listings whose size starts with `"One Size"` match any requested size.
  - `max_price` (float or None): `None` skips the price filter. Otherwise it keeps listings with `price <= max_price`.
- **Returns:** A `list[dict]` of at most `config.SEARCH_RESULT_LIMIT` (10) listing dicts, highest keyword score first. Ties keep the order they have in the data. Listings that score 0 are dropped. Each dict has `id` (str), `title` (str), `description` (str), `category` (str), `style_tags` (list[str]), `size` (str), `condition` (str), `price` (float), `colors` (list[str]), `brand` (str or **None**: most listings have no brand), and `platform` (str).
- **When it has nothing:** It returns an empty list `[]`, never `None` and never an exception. The loop branches on this.

### `suggest_outfit`

- **What it does:** Asks the model, through `generate()`, for one or two outfits built around the thrifted item. When the wardrobe has pieces, the outfits use pieces the user already owns.
- **Inputs:**
  - `new_item` (dict): one listing dict from `search_listings`, with the fields listed above.
  - `wardrobe` (dict): has an `"items"` key holding a `list[dict]`. Each item has `id`, `name`, `category`, `colors` (list[str]), `style_tags` (list[str]), and `notes` (str or None). The list may be empty.
- **Returns:** A non-empty `str` of plain text describing one or two outfits. When the wardrobe has items, each outfit names specific wardrobe pieces by their `name`, e.g. "Baggy straight-leg jeans, dark wash".
- **When it has nothing:** If `wardrobe["items"]` is empty, it still returns a non-empty `str`: general styling advice for the item (what kinds of pieces, colors, and shoes go with it) without naming owned pieces. It never returns `""` and never raises for an empty wardrobe.

### `create_fit_card`

- **What it does:** Asks the model, through `generate()`, for a short social-media caption about the find that reads like a real post, not a product description.
- **Inputs:**
  - `outfit` (str): the string returned by `suggest_outfit`.
  - `new_item` (dict): the same listing dict that was passed to `suggest_outfit`.
- **Returns:** A `str` caption of 2 to 4 sentences. It names the item, its `price` (as `$NN`), and its `platform` once each, and is specific about the outfit's vibe. Because `TEMPERATURE` is 0.9, different runs on the same item give different wording.
- **When it has nothing:** If `outfit` is empty or only whitespace, it skips the model call and returns the string `"Can't write a fit card without an outfit suggestion."` It never raises.

---

## Planning Loop

<!-- Your branch rule, stated as a rule — the condition AND both paths — plus
     the file and function that holds it.

     Like this:
       "If search_listings returns an empty list, put a message in the session
        and stop. Otherwise take the first result and go to suggest_outfit."
        — agent.py::run_agent

     The grader checks your code against what you claim here, so the file and
     function have to be real. -->

**Branch rule:** If `search_listings` returns an empty list, put a message in `session["error"]` that says what the user could change (raise the budget, drop the size, or use broader keywords) and stop, so `suggest_outfit` and `create_fit_card` never run. Otherwise, take the first result as `session["selected_item"]` and go to `suggest_outfit`.

**Where it lives:** `agent.py::run_agent`

**How the query is parsed:** <!-- regex, string splitting, or asking the model — say which --> **Regex**, in `agent.py::parse_query`, with no model call. One pattern finds the price (`under $30`, `below 60`, a bare `$25`) and turns it into `max_price` (float). A second finds the size after the word "size" (`size M`, `size M/L`, `size US 9`, `size W30 L30`) and turns it into `size` (str, uppercased). Both matches are cut out of the text, filler words like "looking for a" are dropped, and what's left becomes `description`. Anything not found is `None`. For example, `designer ballgown size XXS under $5` becomes `{description: "designer ballgown", size: "XXS", max_price: 5.0}`.

**What moves through the session:** <!-- which fields, in what order --> Each step writes its result into the session, and the next step reads it back out:
1. `query` and `wardrobe` are set by `new_session()`.
2. `parsed` is written by `parse_query(query)`.
3. `search_results` is written by `search_listings`, which reads `parsed`. **The branch:** if it is `[]`, `error` is set and the run returns here, so the next three fields stay `None`.
4. `selected_item` is `search_results[0]`.
5. `outfit_suggestion` is written by `suggest_outfit`, which reads `selected_item` and `wardrobe`.
6. `fit_card` is written by `create_fit_card`, which reads `outfit_suggestion` and `selected_item`.

I checked the handoff by wrapping the two model tools to record what they received. For `vintage graphic tee under $30`, `session["selected_item"]` was the same object (`lst_002`, Y2K Baby Tee, $18) that reached both `suggest_outfit` and `create_fit_card`. For `designer ballgown size XXS under $5`, `suggest_outfit` was never called and `fit_card` stayed `None`.

---

## Sample Run

<!-- Two things go here.

     1. One FULL query and its output, pasted as text.
     2. Your three per-tool terminal tests — the command and what it printed. -->

**One full query**

```
$ python app.py ask '...'

```

**The three tools, tested one at a time**

```
$ python -c "from tools import search_listings; print([(r['title'], r['price'], r['size']) for r in search_listings('graphic tee', max_price=30)])"
[('Y2K Baby Tee — Butterfly Print', 18.0, 'S/M'), ('Graphic Tee — 2003 Tour Bootleg Style', 24.0, 'L'), ('Mesh Long-Sleeve Top — Black', 15.0, 'S/M'), ('Vintage Band Tee — Faded Grey', 19.0, 'L'), ('Low-Rise Cargo Pants — Khaki', 27.0, 'W29'), ('Vintage Graphic Hoodie — Faded Black', 26.0, 'L')]
```

```
$ python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"
Outfit 1: Pair the Vintage Levi's 501 Jeans with the white ribbed tank top tucked in, layered under the vintage black denim jacket. Finish with the brown leather belt, black crossbody bag, and chunky white sneakers.

Outfit 2: Style the Vintage Levi's 501 Jeans with the oversized grey crewneck sweatshirt worn loose over the top. Add the black combat boots and the black crossbody bag for an easy, street-ready look.
```

```
$ python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"
Nothing beats a classic pair of vintage Levi's 501s, especially when they fit just right in that perfect medium wash. I love keeping things simple with crisp white sneakers for that effortless, everyday streetwear look. Snagged these on depop for $38 and I honestly don't think I'll be taking them off.
```

---

## How I Used AI

<!-- Two specific moments. What you asked, what came back, what you changed.

     "I used Claude to help me code" is not enough.

     "I gave Claude my search_listings spec. It returned None on no match
     instead of an empty list, so I changed it" is the level we want. -->

**Moment 1**

- *What I asked for:*
- *What came back:*
- *What I changed:*

**Moment 2**

- *What I asked for:*
- *What came back:*
- *What I changed:*

<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════

     Don't fill these in during unit 3.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Run Log — Before

<!-- Five criteria, five tries each, in this exact format.

     Five, because your criteria are written out of five. Mark each try PASS
     or FAIL, count the passes, and read that count against your target — a
     row targeting 4 of 5 with three PASS cells is MISSED (3/5).

     `python run_eval.py --label before` runs everything and writes the table
     into results/. Paste it here and fill in the verdicts. -->

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Real output from one try**, pasted as text, naming the file and function
that produced it:

```

```

---

## Verdicts and Diagnoses

<!-- MET or MISSED per criterion against LAST UNIT's target, plus a sentence on
     how you decided.

     Then, for every miss: which of the four places it happened — a tool, the
     loop's branch, the session, or the model's output — AND the mechanism.

     Not a diagnosis:  "The fit card was bad."
     A diagnosis:      "The fit card criterion missed on 2 of 5 items. Both had
                        an empty brand field. My prompt puts the brand in the
                        first sentence, so the card opened with a blank and read
                        like a fragment. The tool worked; the prompt assumed a
                        field that isn't always there."

     Look for a pattern. Three misses on the same tool is one problem, not
     three. -->

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 |  |  |  |  |
| 2 |  |  |  |  |
| 3 |  |  |  |  |
| 4 |  |  |  |  |
| 5 |  |  |  |  |

**Diagnoses**



---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

**Happy path**

```

```

**Empty search**

```

```

**On the MCP move:** <!-- what changed in your code, and whether anything
behaved differently afterwards. If the rewire didn't work, say exactly where it
broke — the error text and the last thing that worked. That earns the point in
full. -->



---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:**

**Which failure it was meant to fix:**

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Did it help, and how do I know:**

<!-- If it made things worse, say that. Honestly reported, that earns full
     credit and is more interesting than one that worked. -->



---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped where
     you did. "I ran out of time" is fine if it's true. Pretending nothing is
     left is not. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 3

       [ ] criteria.md has five numbered criteria, each with a target
       [ ] Each criterion has a reason underneath it
       [ ] All five unit 3 sections above have real content
       [ ] Tool Inventory: all three tools, inputs WITH TYPES, a specific
           return value, and the empty case
       [ ] Planning Loop names the branch rule and agent.py::run_agent
       [ ] Sample Run: one full query plus the three per-tool tests, as text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN, you submit the same one
           next unit

     SUBMISSION CHECKLIST — unit 4

       [ ] mcp_server.py exists with one tool registered
           (or a written record of exactly where the rewire broke)
       [ ] Run Log — Before, five criteria, five tries each
       [ ] Real output pasted underneath, naming file and function
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, naming a place AND a mechanism
       [ ] Loop Trace, with the MCP call visible in it
       [ ] All three failure modes triggered and handled
       [ ] One improvement, with Run Log — After in the same format
       [ ] What's Still Broken
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository. Your commit history is what
     shows your criteria existed before your results did.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
