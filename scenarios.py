"""
The runs your test needs. ← UNIT 4, MILESTONE 3

Each of your five criteria needs something run against it. A criterion about
the empty-search branch needs an impossible query. One about the fit card needs
the same item run more than once. Working that out is Milestone 3's first step,
and this file is where you write it down.

`run_eval.py` runs everything here five times and writes the run log — five
because your criteria are written out of five.

Three scenarios are filled in to show the shape. Add or change whatever your
own criteria need — these are a starting point, not a fixed set.
"""

SCENARIOS = [
    {
        # A query the data can match. Criterion 1.
        "name": "matching query completes",
        "query": "vintage graphic tee under $30",
        "wardrobe": "example",
        "criterion": 1,
    },
    {
        # A query nothing can match. Criterion 2 — the branch.
        "name": "impossible query stops early",
        "query": "designer ballgown size XXS under $5",
        "wardrobe": "example",
        "criterion": 2,
    },
    {
        # Criterion 3 — state. Same query as criterion 1, because the criterion
        # says "the matching query from criterion 1". What's checked is the
        # session: selected_item id == search_results[0] id, the same title at
        # the suggest_outfit and create_fit_card steps of the trace, and that
        # item's price in the fit card.
        "name": "selected item survives every handoff",
        "query": "vintage graphic tee under $30",
        "wardrobe": "example",
        "criterion": 3,
    },
    {
        # Criterion 4 — the fit card. The SAME item five times with caching
        # off: 2-4 sentences, exact $price and platform in at least 4 of 5,
        # and no two cards opening with the same sentence.
        "name": "fit card states price and platform, varies",
        "query": "vintage graphic tee under $30",
        "wardrobe": "example",
        "criterion": 4,
    },
    {
        # Criterion 5 — price and size filters. Built to catch the substring
        # bug: two XL listings under $25 mention "vintage" (lst_012, lst_027),
        # and "l" in "xl" is True.
        "name": "size L under $25 excludes XL and over-budget",
        "query": "vintage tee size L under $25",
        "wardrobe": "example",
        "criterion": 5,
    },
    {
        # A user with nothing saved. One of unit 4's three failure modes.
        "name": "empty wardrobe",
        "query": "denim jacket under $50",
        "wardrobe": "empty",
        "criterion": None,
    },
]

WARDROBES = ("example", "empty")


def validate() -> list[str]:
    """Complain about anything malformed, before a long run rather than during."""
    problems = []
    for i, scenario in enumerate(SCENARIOS, 1):
        if not scenario.get("query", "").strip():
            problems.append(f"scenario {i} has no query")
        if scenario.get("wardrobe") not in WARDROBES:
            problems.append(
                f"scenario {i} has wardrobe {scenario.get('wardrobe')!r} — "
                f"it should be one of {WARDROBES}"
            )
    return problems
