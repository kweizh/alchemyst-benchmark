# SyllabAI-Style Syllabus Q&A with Alchemyst AI (Python SDK)

## Background
You are building a script inspired by [SyllabAI](https://getalchemystai.com/docs/example-projects/team/syllabai) that turns a course syllabus into an interactive study assistant. Using the Alchemyst AI Python SDK (`alchemystai`), you will ingest several excerpts from a Math 101 syllabus as separate documents into the Alchemyst context engine, then issue three different questions **in parallel** to retrieve the most relevant snippet for each question. The top retrieved snippet per question must be written to a structured JSON answer file.

## Requirements
- Use the Alchemyst AI Python SDK (`alchemystai`) authenticated via the `ALCHEMYST_AI_API_KEY` environment variable.
- Read the `ZEALT_RUN_ID` environment variable and use it to isolate this trial's documents from concurrent runs. Append `${ZEALT_RUN_ID}` as a third element of the `group_name` array so that ingestion and searches stay scoped to this run.
- Ingest **5 separate syllabus excerpt documents** (one document per `client.v1.context.add` document entry) covering at least: the **midterm exam date**, the **required textbook**, the **grading policy**, the **office hours**, and the **course description**. Each document must include a metadata dict with:
    - A **unique `file_name`** generated with `uuid.uuid4()` (e.g., `syllabus-<uuid4>.md`).
    - `group_name = ["syllabus", "math101", "${ZEALT_RUN_ID}"]` (the literal strings `syllabus` and `math101`, plus the run-id read from the environment).
- Issue the following three questions **in parallel** (e.g., with a thread pool or `asyncio`) against the Alchemyst context engine, filtered to the run-scoped group via `metadata={"group_name": [..., "${ZEALT_RUN_ID}"]}`:
    1. `When is the midterm?`
    2. `What textbook is required?`
    3. `What is the grading policy?`
- For each question, take the **top (highest-ranked) snippet** returned by `client.v1.context.search` and record it.
- Write the structured answers to `/workspace/syllabus_answers.json` using the schema described in Acceptance Criteria.

## Implementation Hints
- Initialize the SDK with `AlchemystAI(api_key=os.environ["ALCHEMYST_AI_API_KEY"])`.
- Use `client.v1.context.add(...)` with `context_type="resource"`, `source="syllabus"`, `scope="internal"` to ingest the excerpts. All 5 documents may be sent in a single `add` call (one entry per document) or one at a time — what matters is that they each carry distinct content and a unique `file_name`.
- After ingestion, allow a short delay (a few seconds) for indexing before searching.
- For the parallel search step, you can use `concurrent.futures.ThreadPoolExecutor` and submit one `client.v1.context.search(...)` call per question, or use `asyncio.to_thread` + `asyncio.gather`.
- Use `similarity_threshold=0.5` (or lower) to ensure each question retrieves at least one snippet. Always pass the run-scoped `group_name` filter.
- The Python SDK returns search results where each context has a `.content` attribute (or `content` key). Pick the first (top) item from `result.contexts`.
- The output JSON file path is `/workspace/syllabus_answers.json`. Make sure `/workspace` exists.

## Acceptance Criteria
- Project path: /workspace
- Output file: /workspace/syllabus_answers.json
- The script must be invoked exactly via: `python3 /workspace/syllabus_qa.py`
- Read `ZEALT_RUN_ID` from the environment and use it inside `group_name` for both ingestion and search.
- 5 documents are added to the Alchemyst context engine within the group `["syllabus", "math101", "${ZEALT_RUN_ID}"]`, each with a unique `file_name` metadata value.
- `/workspace/syllabus_answers.json` exists after the run, is valid JSON, and matches this schema:

    ```json
    {
      "run_id": "<value of ZEALT_RUN_ID>",
      "answers": [
        {"question": "When is the midterm?", "snippet": "<top retrieved snippet text>"},
        {"question": "What textbook is required?", "snippet": "<top retrieved snippet text>"},
        {"question": "What is the grading policy?", "snippet": "<top retrieved snippet text>"}
      ]
    }
    ```

- The `answers` list must contain exactly the three questions above, in any order. Each snippet must be a non-empty string drawn from the documents you ingested.
- The snippet for `When is the midterm?` must contain the substring `October 15` (case-insensitive).
- The snippet for `What textbook is required?` must contain the substring `Stewart` (case-insensitive).
- The snippet for `What is the grading policy?` must contain the substring `Homework 30%` (case-insensitive).

