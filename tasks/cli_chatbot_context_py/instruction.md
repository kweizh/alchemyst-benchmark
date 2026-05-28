# Context-Aware CLI Chatbot with Alchemyst AI Memory (Python)

## Background
Build a non-interactive command-line chatbot in Python that uses Alchemyst AI as its context/memory layer and OpenAI as its language model. The CLI should be safely re-runnable: each time it is invoked it must search the Alchemyst context engine for prior conversation snippets scoped to the current run, feed them as system context to an OpenAI chat completion, print the assistant reply on stdout, and then persist the new user/assistant turn back into the Alchemyst context engine so future invocations can recall it.

This pattern is inspired by the Alchemyst CLI chatbot example but extends it with cross-invocation memory: because each invocation is a fresh process, the only way to remember earlier turns is to store them in Alchemyst keyed by a stable `userId`/`sessionId` and read them back on the next call.

## Requirements
- Implement a Python 3.11+ CLI named `chat.py` that takes the user message as a single positional argument:
  `python chat.py "<question>"`.
- The CLI must read the current `run-id` from the `ZEALT_RUN_ID` environment variable and derive a deterministic `userId` and `sessionId` from it (so concurrent runs do not collide).
- On every invocation the CLI must:
  1. Search the Alchemyst context engine for snippets relevant to the current message, scoped to this run's `userId`/`sessionId`.
  2. Build an OpenAI chat completion request using the retrieved snippets as system context together with the new user message.
  3. Print only the assistant's reply text on stdout (no extra prefixes/banners on the line containing the answer).
  4. Store the new turn (the user message and the assistant reply) back into Alchemyst under the same `userId`/`sessionId` so it can be retrieved on subsequent invocations.
- Two consecutive invocations within the same `ZEALT_RUN_ID` must share state: a fact stated in the first call must be recallable in the second call's answer.
- Read `ALCHEMYST_AI_API_KEY` and `OPENAI_API_KEY` from environment variables. Do not hardcode credentials.

## Implementation Hints
- Use the `alchemystai` Python SDK to talk to the Alchemyst context engine and the `openai` Python SDK for chat completions.
- Memory in Alchemyst is keyed by `userId` and `sessionId`; both are required. Derive stable values from `ZEALT_RUN_ID` such as `cli-user-${ZEALT_RUN_ID}` and `cli-session-${ZEALT_RUN_ID}`.
- After retrieving snippets, format them into a system message so the LLM has the prior facts available before answering the new question.
- Keep stdout clean so a calling shell can capture the reply with `$(python chat.py "...")` or by redirection.
- Choose an OpenAI chat model that is generally available (e.g., `gpt-4o-mini`).

## Acceptance Criteria
- Project path: /home/user/cli-chatbot
- Entry script: /home/user/cli-chatbot/chat.py
- Command: `python chat.py "<question>"` (the question is a single positional argument)
- The script exits with status 0 on success and prints the assistant reply to stdout.
- Memory scoping: the `userId` and `sessionId` used by the script must be derived from the `ZEALT_RUN_ID` environment variable so two invocations in the same run share memory and two invocations in different runs do not.
- Cross-invocation recall: when invoked twice in sequence within the same `ZEALT_RUN_ID`, where the first invocation states a fact and the second asks about that fact, the second invocation's stdout must include the fact previously stated.
- The script must call the real Alchemyst AI API and the real OpenAI API; mocking either provider is not allowed.

