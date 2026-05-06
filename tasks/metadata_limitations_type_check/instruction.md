# Metadata Limitations Type Check

## Background
Alchemyst AI allows adding metadata to documents to help with context filtering. However, metadata values must be `string` or `number` only. Nested objects or arrays (other than `group_name`) may cause the API to return an error or be ignored.

## Requirements
- Create a Python script `/home/user/myproject/check_metadata.py`.
- Use the `alchemyst_ai` SDK to interact with the Alchemyst API.
- The script should attempt to add two documents to the context engine (use `context_type="resource"`, `source="docs"`, `scope="internal"`):
  1. A document with valid metadata: `file_name` (string), `version` (number), and `group_name` (array of strings).
  2. A document with invalid metadata: `file_name` (string) and `nested_data` (a dictionary/object).
- The script must handle any exceptions thrown by the API when adding the invalid metadata.
- Finally, the script must write a JSON file to `/home/user/myproject/result.json` with the following format:
  `{"valid_added": true/false, "invalid_added": true/false}` depending on whether each API call succeeded without throwing an exception.

## Constraints
- Project path: `/home/user/myproject`
- Output file: `/home/user/myproject/result.json`
- Use the `alchemystai` Python package.
- Read the `ALCHEMYST_AI_API_KEY` environment variable for authentication.