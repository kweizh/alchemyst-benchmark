# Shared Team Session Memory with Alchemyst AI (TypeScript SDK)

## Background
Alchemyst AI's memory API supports team collaboration scenarios where multiple `userId`s share the same `sessionId`, creating a shared memory space. In this task, you will simulate two teammates collaborating in the same session: user A stores a project codename, and user B later searches the shared session memory to recall it.

## Requirements
- Use the `@alchemystai/sdk` TypeScript SDK to interact with the Alchemyst AI Memory API.
- Generate two distinct user IDs (`userA`, `userB`) and one shared session ID using `crypto.randomUUID()`, then append the current `run-id` (from the `ZEALT_RUN_ID` environment variable) to each identifier to keep concurrent runs isolated.
- As user A, add a memory containing the sentence `Project codename is Falcon` under the shared session.
- As user B, search the memory under the **same** `sessionId` (but with userB's `userId`) and persist the recalled content.
- Write a JSON report of the recall to `/workspace/team_recall.json`.
- Write a log of the full run to `/workspace/output.log`.

## Implementation Hints
- Authenticate the SDK with the `ALCHEMYST_AI_API_KEY` environment variable.
- The TypeScript memory client lives at `client.v1.context.memory` and exposes `add` and `search` operations. Both `userId` and `sessionId` are required.
- Generate fresh UUIDs at runtime so that repeated executions do not collide; suffix them with `ZEALT_RUN_ID` for parallel-run safety.
- After user B's search, extract the recalled memory contents (an array of strings/objects from `memories`) and serialize them to the recall report.
- Allow a short propagation delay after adding the memory before searching, so the search call can locate the freshly added entry.

## Acceptance Criteria
- Project path: /home/user/myproject
- Log file: /workspace/output.log
- Recall report: /workspace/team_recall.json
- The script must be executable with: `node --experimental-vm-modules /home/user/myproject/index.mjs` (or via `npm start` from the project directory).
- The script must read `ZEALT_RUN_ID` from the environment and incorporate it into both `userId` values and the `sessionId`.
- `/workspace/team_recall.json` must be a JSON object with the following shape:
  ```json
  {
    "userA": string,
    "userB": string,
    "sessionId": string,
    "recalled": string[]
  }
  ```
  where `recalled` is the list of memory content strings that user B retrieved from the shared session.
- The `recalled` array must include at least one entry that contains the substring `Falcon` (case-sensitive).
- `userA` and `userB` must be different strings, but both must contain the value of `ZEALT_RUN_ID` as a suffix.
- `sessionId` must contain the value of `ZEALT_RUN_ID` as a suffix.
- `/workspace/output.log` must contain a line of the form `Recall complete: <session_id>` where `<session_id>` matches the `sessionId` written to the recall report.

