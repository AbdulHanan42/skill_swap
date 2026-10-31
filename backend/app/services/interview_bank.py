"""Skill-aware question bank and task briefs for the AI interview.

The interview runs on this local content unless an AI provider is configured, so
the flow never depends on a network round trip to be playable.
"""

import random
import re

QUESTION_COUNT = 5

# Each entry is tagged with the skill family it probes. Families are resolved from
# the names on the user's profile, so the quiz always matches what they offer.
QUESTION_BANK: list[dict] = [
    {
        "family": "sql",
        "prompt": "What is the correct SQL statement to retrieve unique values from the 'skills' column in a 'twins' table?",
        "options": [
            "SELECT UNIQUE skills FROM twins",
            "SELECT DISTINCT skills FROM twins",
            "SELECT DIFFERENT skills FROM twins",
            "SELECT skills FROM twins WHERE unique=True",
        ],
        "answer_index": 1,
        "explanation": "DISTINCT removes duplicate rows from the result set; UNIQUE is not a SQLite keyword.",
    },
    {
        "family": "sql",
        "prompt": "Which join returns every row from the left table even when the right table has no match?",
        "options": ["INNER JOIN", "LEFT OUTER JOIN", "CROSS JOIN", "NATURAL JOIN"],
        "answer_index": 1,
        "explanation": "A LEFT OUTER JOIN keeps unmatched left rows and fills the right columns with NULL.",
    },
    {
        "family": "sql",
        "prompt": "You need swap counts per skill, only for skills used more than three times. Which clause filters the groups?",
        "options": ["WHERE after GROUP BY", "HAVING after GROUP BY", "ORDER BY ... FILTER", "LIMIT 3"],
        "answer_index": 1,
        "explanation": "WHERE runs before grouping; HAVING filters the aggregated groups afterwards.",
    },
    {
        "family": "sql",
        "prompt": "Which statement safely updates a user's designation only for one account?",
        "options": [
            "UPDATE users SET designation = 'Backend Dev'",
            "UPDATE users SET designation = 'Backend Dev' WHERE id = 12",
            "ALTER users SET designation = 'Backend Dev' WHERE id = 12",
            "SET users.designation = 'Backend Dev' WHERE id = 12",
        ],
        "answer_index": 1,
        "explanation": "Without the WHERE clause the update rewrites every row in the table.",
    },
    {
        "family": "sql",
        "prompt": "What does an index on a foreign key column mainly improve?",
        "options": [
            "Insert speed into that table",
            "Join and cascade lookups that filter on that column",
            "The size of the stored rows",
            "Uniqueness of the referenced primary key",
        ],
        "answer_index": 1,
        "explanation": "Indexes speed up lookups on the indexed column, at the cost of a little write overhead.",
    },
    {
        "family": "python",
        "prompt": "Which expression reads an environment variable without raising when it is missing?",
        "options": [
            "os.environ.get('API_KEY', '')",
            "os.environ['API_KEY']",
            "os.getenv.required('API_KEY')",
            "environ('API_KEY')",
        ],
        "answer_index": 0,
        "explanation": "os.environ[...] raises KeyError; .get() returns the supplied default instead.",
    },
    {
        "family": "python",
        "prompt": "You have a list of swap dictionaries. Which is the idiomatic way to keep only completed ones?",
        "options": [
            "[s for s in swaps if s['status'] == 'completed']",
            "filter.equals(swaps, 'completed')",
            "swaps.where(status='completed')",
            "for s in swaps: s.status == 'completed'",
        ],
        "answer_index": 0,
        "explanation": "A list comprehension with a condition is the standard pure-Python filter.",
    },
    {
        "family": "python",
        "prompt": "Why is 'with open(path) as handle:' preferred over a bare open() call?",
        "options": [
            "It reads the file faster",
            "It closes the handle even when an exception is raised",
            "It locks the file against other processes",
            "It returns bytes instead of text",
        ],
        "answer_index": 1,
        "explanation": "The context manager guarantees cleanup on every exit path.",
    },
    {
        "family": "python",
        "prompt": "Which pandas call produces one row per skill with the average session length?",
        "options": [
            "df.groupby('skill')['minutes'].mean()",
            "df.pivot('skill', 'minutes')",
            "df['minutes'].rolling('skill')",
            "df.resample('skill').avg()",
        ],
        "answer_index": 0,
        "explanation": "groupby then mean aggregates the column per group.",
    },
    {
        "family": "python",
        "prompt": "A function must accept an optional timeout. Which signature is correct?",
        "options": [
            "def run(timeout=30): ...",
            "def run(timeout: =30): ...",
            "def run(timeout := 30): ...",
            "def run(timeout? = 30): ...",
        ],
        "answer_index": 0,
        "explanation": "Python declares defaults as name=value in the parameter list.",
    },
    {
        "family": "javascript",
        "prompt": "Which Vue 3 API creates a reactive value you can read and write in a <script setup> block?",
        "options": ["ref()", "reactiveValue()", "useState()", "observable()"],
        "answer_index": 0,
        "explanation": "ref() returns an object whose .value is tracked; computed() derives from it.",
    },
    {
        "family": "javascript",
        "prompt": "What does 'const { data } = await response.json()' assume about the response?",
        "options": [
            "It is a JSON object with a data property",
            "It is a plain text string",
            "It is a FormData instance",
            "It is a Blob",
        ],
        "answer_index": 0,
        "explanation": "Destructuring only works once json() has parsed an object.",
    },
    {
        "family": "web",
        "prompt": "Which HTTP status means the request was understood but the server refused to authorise it?",
        "options": ["401", "403", "404", "422"],
        "answer_index": 1,
        "explanation": "401 is missing credentials; 403 is authenticated but not allowed.",
    },
    {
        "family": "web",
        "prompt": "What is the point of adding a database index inside an Alembic migration rather than at runtime?",
        "options": [
            "It keeps schema changes versioned and repeatable per environment",
            "It avoids writing Python code",
            "Indexes are ignored outside migrations",
            "It makes SELECT statements faster without an index",
        ],
        "answer_index": 0,
        "explanation": "Migrations give every environment the same, replayable schema history.",
    },
    {
        "family": "git",
        "prompt": "You committed to the wrong branch. Which command moves the last commit safely while keeping the change staged?",
        "options": [
            "git reset --hard HEAD~1",
            "git reset --soft HEAD~1",
            "git checkout HEAD~1",
            "git rm --cached HEAD",
        ],
        "answer_index": 1,
        "explanation": "--soft undoes the commit but keeps the index and working tree intact.",
    },
    {
        "family": "docker",
        "prompt": "Which image layout keeps a Python container smallest for a FastAPI service?",
        "options": [
            "Full ubuntu image with everything installed",
            "Slim base, install requirements, then copy only the app package",
            "Two images: one to build, one that copies nothing",
            "The largest available base image for safety",
        ],
        "answer_index": 1,
        "explanation": "A slim base plus selective copying avoids shipping build tools and caches.",
    },
]

TASK_TEMPLATES: dict[str, dict] = {
    "python+sql": {
        "title": "Task 1: Python & SQL Script Integration",
        "brief": (
            "Build a Python script that parses SQLite database logs, filters active skill swaps, "
            "and creates a clean pandas DataFrame."
        ),
        "requirements": [
            "Read the SQLite log file with the standard library only for I/O.",
            "Keep swaps whose status is 'active' and whose duration is at least 15 minutes.",
            "Return a pandas DataFrame with the columns: skill, partner, minutes, swapped_on.",
            "Print a one-line summary per skill with the total hours.",
            "Handle a missing table or empty log without raising an unhandled exception.",
        ],
        "deliverables": [
            "python_sql_challenge.py — the script itself",
            "output.csv — the DataFrame you produced",
        ],
    },
    "python": {
        "title": "Task 1: Python Automation Script",
        "brief": (
            "Build a Python script that ingests a CSV of skill swap sessions, validates each row, "
            "and writes a cleaned summary back to disk."
        ),
        "requirements": [
            "Parse the CSV with the csv module or pandas.",
            "Drop rows with missing dates or non-numeric durations, and report how many were dropped.",
            "Aggregate total hours per skill and per partner.",
            "Write the summary to summary.csv and print it to stdout.",
        ],
        "deliverables": ["solution.py — the script", "summary.csv — its output"],
    },
    "sql": {
        "title": "Task 1: SQL Reporting Queries",
        "brief": (
            "Write the SQL that answers the swap-reporting questions below and save it as a single "
            ".sql file you can run against SQLite."
        ),
        "requirements": [
            "Use GROUP BY and HAVING where an aggregate filter is needed.",
            "Prefer explicit JOINs over comma-separated FROM lists.",
            "Name every computed column so the result reads like a report.",
            "Add a comment above each query describing what it answers.",
        ],
        "deliverables": ["report.sql — the queries", "notes.md — anything you assumed about the schema"],
    },
    "javascript": {
        "title": "Task 1: Frontend Data Flow",
        "brief": (
            "Build a small module that fetches a JSON endpoint, keeps the result reactive and exposes "
            "loading and error states to a component."
        ),
        "requirements": [
            "Use native fetch, no HTTP libraries.",
            "Expose loading, error and data state.",
            "Cancel or ignore a response when a newer request has started.",
        ],
        "deliverables": ["useResource.js — the module", "usage.md — how a component consumes it"],
    },
    "general": {
        "title": "Task 1: Practical Engineering Exercise",
        "brief": (
            "Pick one tool you offer and automate a repetitive part of your workflow with it, then "
            "document what you built and why."
        ),
        "requirements": [
            "State the problem the script solves in one paragraph.",
            "Show the input and the expected output.",
            "Include the command you use to run it.",
        ],
        "deliverables": ["the script or notes", "README.md — how to run it"],
    },
}

ACCEPTED_SUFFIXES = (".py", ".sql", ".zip", ".txt", ".md", ".ipynb", ".csv", ".json", ".tar.gz")

FAMILY_KEYWORDS: dict[str, tuple[str, ...]] = {
    "python": ("python", "django", "fastapi", "flask", "pandas", "numpy"),
    "sql": ("sql", "postgres", "mysql", "sqlite", "database", "oracle", "mongodb"),
    "javascript": ("javascript", "typescript", "node", "react", "vue", "angular", "svelte"),
    "web": ("http", "rest", "api", "networking", "backend", "frontend", "web"),
    "git": ("git", "github", "gitlab", "version control"),
    "docker": ("docker", "kubernetes", "devops", "aws", "azure", "cloud"),
}


def _normalise(name: str) -> str:
    return re.sub(r"[^a-z0-9 +]", "", name.lower()).strip()


def skill_families(names: list[str]) -> list[str]:
    """Map profile skill names onto the families the bank can actually test."""
    families: list[str] = []
    for raw in names:
        name = _normalise(raw)
        if not name:
            continue
        for family, keywords in FAMILY_KEYWORDS.items():
            if any(keyword in name for keyword in keywords) and family not in families:
                families.append(family)
    return families


def _ordered_bank(families: list[str], seed: int) -> tuple[list[dict], list[str]]:
    """Questions the user can actually be asked, best-matched first."""
    focus = families or ["general"]
    rng = random.Random(seed)
    matched = [item for item in QUESTION_BANK if item["family"] in focus]
    rest = [item for item in QUESTION_BANK if item["family"] not in focus]
    rng.shuffle(matched)
    rng.shuffle(rest)
    return matched + rest, focus


def build_questions(names: list[str], count: int = QUESTION_COUNT, seed: int = 0) -> list[dict]:
    families = skill_families(names)
    pool, focus = _ordered_bank(families, seed)
    if focus:
        # Guarantee every tested skill appears: take its family first, then fill in.
        picked: list[dict] = []
        for family in focus:
            for item in pool:
                if item["family"] == family and all(pick is not item for pick in picked):
                    picked.append(item)
                    break
        picked += [item for item in pool if item not in picked]
        pool = picked
    chosen = pool[: max(1, min(count, len(pool)))]
    return [
        {
            "id": index,
            "prompt": item["prompt"],
            "options": list(item["options"]),
            "family": item["family"],
            "answer_index": item["answer_index"],
            "explanation": item["explanation"],
        }
        for index, item in enumerate(chosen, 1)
    ]


def task_for(names: list[str], seed: int = 0) -> dict:
    families = set(skill_families(names))
    if "python" in families and "sql" in families:
        key = "python+sql"
    else:
        key = next((family for family in ("python", "sql", "javascript") if family in families), "general")
    template = TASK_TEMPLATES[key]
    brief_name = "SQL_Challenge_Brief.pdf" if "sql" in families else "Task_Brief.pdf"
    return {
        "key": key,
        "title": template["title"],
        "brief": template["brief"],
        "requirements": list(template["requirements"]),
        "deliverables": list(template["deliverables"]),
        "filename": brief_name,
        "accepted": list(ACCEPTED_SUFFIXES),
        "skills": sorted(families) or ["general"],
    }
