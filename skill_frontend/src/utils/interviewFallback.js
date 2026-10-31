/**
 * Offline paper for the AI interview.
 *
 * The live questions come from the backend; this copy exists only so the page
 * still renders something readable when the service cannot be reached at all.
 */

const QUESTIONS = [
  {
    id: 1,
    prompt: "What is the correct SQL statement to retrieve unique values from the 'skills' column in a 'twins' table?",
    options: [
      'SELECT UNIQUE skills FROM twins',
      'SELECT DISTINCT skills FROM twins',
      'SELECT DIFFERENT skills FROM twins',
      'SELECT skills FROM twins WHERE unique=True',
    ],
    answerIndex: 1,
  },
  {
    id: 2,
    prompt: 'Which join keeps every left row even when the right table has no match?',
    options: ['INNER JOIN', 'LEFT OUTER JOIN', 'CROSS JOIN', 'NATURAL JOIN'],
    answerIndex: 1,
  },
  {
    id: 3,
    prompt: "Which expression reads an environment variable without raising when it is missing?",
    options: ["os.environ.get('API_KEY', '')", "os.environ['API_KEY']", "os.getenv.required('API_KEY')", "environ('API_KEY')"],
    answerIndex: 0,
  },
  {
    id: 4,
    prompt: "Why is 'with open(path) as handle:' preferred over a bare open() call?",
    options: [
      'It reads the file faster',
      'It closes the handle even when an exception is raised',
      'It locks the file against other processes',
      'It returns bytes instead of text',
    ],
    answerIndex: 1,
  },
  {
    id: 5,
    prompt: 'Which pandas call produces one row per skill with the average session length?',
    options: ["df.groupby('skill')['minutes'].mean()", "df.pivot('skill', 'minutes')", "df['minutes'].rolling('skill')", "df.resample('skill').avg()"],
    answerIndex: 0,
  },
]

export const DEMO_TASK = {
  title: 'Task 1: Python & SQL Script Integration',
  brief: 'Build a Python script that parses SQLite database logs, filters active skill swaps, and creates a clean pandas DataFrame.',
  requirements: [
    'Read the SQLite log file with the standard library only for I/O.',
    "Keep swaps whose status is 'active' and whose duration is at least 15 minutes.",
    'Return a pandas DataFrame with the columns: skill, partner, minutes, swapped_on.',
    'Print a one-line summary per skill with the total hours.',
  ],
  deliverables: ['python_sql_challenge.py — the script itself', 'output.csv — the DataFrame you produced'],
  brief_filename: 'SQL_Challenge_Brief.pdf',
  accepted: ['.py', '.sql', '.zip', '.txt', '.md', '.ipynb', '.csv', '.json', '.tar.gz'],
  max_upload_mb: 10,
  submission: null,
}

export function demoStatus() {
  const [first, ...rest] = QUESTIONS.map((item, index) => ({
    id: item.id,
    index: index + 1,
    total: QUESTIONS.length,
    prompt: item.prompt,
    options: item.options,
    answerIndex: item.answerIndex,
  }))
  return {
    state: 'mcq',
    step: 0,
    skills: ['Python', 'SQL'],
    total_questions: QUESTIONS.length,
    answered: 0,
    answers: {},
    question: { ...first, answered: 0 },
    questions: [first, ...rest],
    task: null,
    result: null,
    source: 'offline demo paper',
  }
}
