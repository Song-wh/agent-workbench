"""Run: python test_hookscore.py  - checks that spelled-out numbers score like digits."""
import hookscore as h

PAIRS = [
    ("Your MCP server can be eighty-six lines, and Claude Code can write them before you finish your coffee.",
     "Your MCP server can be 86 lines, and Claude Code can write them before you finish your coffee."),
    ("In twenty twelve, CNN wrote that the deaths started ten years earlier.",
     "In 2012, CNN wrote that the deaths started 10 years earlier."),
    ("It took one hundred and three seconds and fifty-two cents.", "It took 103 seconds and 52 cents."),
]
SPELLING = {"eighty-six lines": "86 lines", "nineteen ninety-six": "1996", "two thousand two": "2002",
            "five thousand eight hundred and eighteen people": "5818 people", "the one line": "the one line",
            "forty-two patients in nineteen seventy-two": "42 patients in 1972"}

for spoken, digits in PAIRS:
    assert h.score(spoken)[1] == h.score(digits)[1], (spoken, h.score(spoken)[1], h.score(digits)[1])
for spoken, digits in SPELLING.items():
    assert h.spoken_to_digits(spoken) == digits, (spoken, h.spoken_to_digits(spoken))
print("ok")
