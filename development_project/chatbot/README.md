# UniBot – a multi-agent student-services chatbot

UniBot is a prototype chatbot for a university student-support desk. A signed-in
student can hold a short conversation and ask it to:

1. greet them and sign off politely;
2. show the weekly **timetable** of the modules they are currently taking;
3. create and download a PDF **transcript** of their marks to date;
4. list their **active assignments** (deadline not yet passed) and deliver the PDF brief for any of them.

All data is synthetic. Nothing in this repository connects to a real student record system.

## How it works in one paragraph

Four agents cooperate over an in-process message bus. The **dialogue agent** owns the
conversation: it interprets each message, keeps per-session state (what was last listed,
whether a clarification is pending) and decides which specialist to involve. The
**timetable**, **transcript** and **assignment agents** each own one competence and only
ever answer messages addressed to them. Messages carry a performative (`ask-one`,
`achieve`, `tell`, `sorry`, `error`) borrowed from KQML, so the trace of a conversation
reads as a sequence of speech acts; the web interface can show it live ("show agent
messages"). Interpretation of the student's words is pluggable: a deterministic
rule-based interpreter runs by default, and a language-model interpreter (Anthropic
Claude, tool use) can be switched on. The model can only pick one of ten tools; every
record lookup, deadline check, PDF and download link is produced by ordinary Python
behind an authenticated session, and if the model is unavailable the system falls back
to the rules.

```
browser ──► FastAPI (web.py) ──► DialogueAgent ──┬─► TimetableAgent ──► SQLite
             │  session + ownership checks       ├─► TranscriptAgent ──► ReportLab PDF
             │                                   └─► AssignmentAgent ──► SQLite + brief PDFs
             └──► /documents/{id}, /assignments/{id}/pdf  (re-checked on every request)
```

## Requirements

* Python 3.11 or later (developed on 3.11, macOS; nothing platform-specific is used)
* The packages in `requirements.txt`

```bash
cd chatbot
python3 -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Running the application

1. **Seed the database** (creates `data/unibot.sqlite3`, the assignment-brief PDFs and two demo accounts with random passwords):

   ```bash
   python -m unibot.seed --reset
   ```

   The command prints the usernames (`amina`, `ben`) and their generated passwords and
   writes them to `data/demo_credentials.json`. The `data/` folder is ignored by git.

2. **Start the web interface:**

   ```bash
   python -m unibot.web
   ```

   The server prints the address to open (normally <http://127.0.0.1:8000>; if that port is
   busy it takes the next free one and says so, or set `UNIBOT_PORT`). Starting before seeding
   stops with a message saying to seed first. Sign in as `amina`, and try, for example:
   *"hi"*, *"when are my classes?"*, *"can I have my transcript as a PDF"*,
   *"which assignments are still open?"*, *"download the second one"*, *"bye"*.
   Tick **show agent messages** to see the inter-agent exchange for each turn.

3. **Terminal client** (same agents, text rendering):

   ```bash
   python -m unibot.cli --user amina --trace
   ```

### Enabling the language-model interpreter (optional)

Create a file named `.env` in the `chatbot` folder containing

```
UNIBOT_LLM_ENABLED=true
ANTHROPIC_API_KEY=your-key
```

and restart the server. `UNIBOT_LLM_MODEL` and `UNIBOT_LLM_TIMEOUT` (seconds) can be set
there too. The header pill changes from
`RuleInterpreter` to `LLMInterpreter`, and each reply shows whether the intent was
decided by the model (`llm`) or by the rules after a fallback (`llm-fallback-rules`).
The model defaults to `claude-haiku-5-5`, the cheapest current Claude model, which is sufficient for choosing one of ten tools; set `UNIBOT_LLM_MODEL` to change it.
Without a key, or if the API times out, errors or returns anything other than exactly
one tool call, the rule interpreter answers instead. Only the student's message and a
short window of recent turns are sent to the model; records, marks and PDFs never are.

Note on the two copies of this code: the copy submitted through the portal includes a
`.env` with the language-model interpreter enabled and a working key, so that it can be
tested as demonstrated in the report. The public repository omits `.env` (it is listed in
`.gitignore`) and runs with the rule interpreter unless you supply your own key.

### Freezing the clock for demonstrations

Active assignments depend on the current time. Set `UNIBOT_FAKE_NOW=2026-03-02T12:00:00+00:00`
(for example) before seeding and running to make a demonstration repeatable.

## Testing and quality checks

```bash
python -m pytest -v                       # 54 tests: agents, protocol, interpreters, HTTP access control
python -m flake8 unibot tests scripts     # style
python -m pylint unibot                   # static analysis (config in pyproject.toml)
python -m bandit -r unibot -c pyproject.toml   # security linter
python -m pip_audit -r requirements.txt   # known vulnerabilities in dependencies
python scripts/interpreter_eval.py        # rule interpreter on 24 scenarios; add --live to include the LLM
```

The linters, bandit and pip-audit need the extra tools in `requirements-dev.txt`
(`pip install -r requirements-dev.txt`).

The raw outputs of these tools, before and after remediation, are in `evidence/`.
Tests run entirely offline: the LLM adapter is exercised with a fake client.

## Project layout

```
unibot/
  acl.py            message format and performatives (KQML-inspired)
  bus.py            message bus / facilitator with a per-turn trace
  agents/base.py    Agent contract
  agents/records.py TimetableAgent, TranscriptAgent, AssignmentAgent
  agents/dialogue.py DialogueAgent: deliberative control loop and session state
  interpreters.py   RuleInterpreter, LLMInterpreter, tool schemas, validation
  db.py             schema, parameterised queries, synthetic seed data
  documents.py      ReportLab PDF generation (transcripts, briefs)
  auth.py           PBKDF2 password hashing, server-side sessions
  web.py            FastAPI routes; ownership re-checked on every download
  cli.py            terminal client
  seed.py           python -m unibot.seed
tests/              pytest suite (see above)
scripts/            interpreter evaluation script
evidence/           tool outputs and screenshots used in the report
```

## Security notes

* Passwords are hashed with PBKDF2-HMAC-SHA256; session tokens are random, stored hashed,
  expire, and are carried in an `HttpOnly`, `SameSite=Strict` cookie.
* Every SQL statement is parameterised and every record query is filtered by the
  session's student id. The student id is never taken from the chat text or the URL.
* Download routes look the file up by id in the database and re-check ownership (and,
  for assignments, enrolment and deadline) on each request. A missing and an
  unauthorised document both return 404.
* The chat endpoint rejects unknown fields and messages over 1000 characters, and
  requires a custom header that cross-site forms cannot supply.
* The prototype binds to `127.0.0.1` and does not set the `Secure` cookie flag; both
  would change for any deployment beyond localhost, behind HTTPS and institutional SSO.

## Sources that informed the design

* Bratman, M.E., Israel, D.J. and Pollack, M.E. (1988) Plans and resource-bounded practical reasoning. *Computational Intelligence* 4(3): 349–355.
* Finin, T., Fritzson, R., McKay, D. and McEntire, R. (1994) KQML as an agent communication language. *Proceedings of CIKM '94*: 456–463.
* OWASP (2021) *SQL Injection Prevention Cheat Sheet*. Available from: https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html
* Searle, J.R. (1969) *Speech Acts: An Essay in the Philosophy of Language*. Cambridge: Cambridge University Press.
* Wooldridge, M. (2009) *An Introduction to MultiAgent Systems*. 2nd edn. Chichester: Wiley.
* Anthropic (2026) *Define tools* and *Handle tool calls*, Claude developer documentation. Available from: https://platform.claude.com/docs/
* FastAPI (2026) *Testing*. Available from: https://fastapi.tiangolo.com/tutorial/testing/
