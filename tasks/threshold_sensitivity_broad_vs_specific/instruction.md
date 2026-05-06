# Threshold Sensitivity Test

## Background
Alchemyst AI allows adjusting the `similarity_threshold` when searching for context. A higher threshold (e.g., 0.9) requires precise matches, while a lower threshold (e.g., 0.5) is more exploratory.

## Requirements
Write a Python script `test_threshold.py` in `/home/user/project` that:
1. Initializes the `AlchemystAI` client using the `ALCHEMYST_AI_API_KEY` environment variable.
2. Adds a document with content: 'Our refund policy: We offer a 30-day money back guarantee.' and metadata `file_name` set to 'refunds_123.md'.
3. Performs a search for the query 'refund policy' with `similarity_threshold=0.9`.
4. Performs a search for the query 'refund policy' with `similarity_threshold=0.5`.
5. Writes the lengths of the contexts returned to a JSON file at `/home/user/project/output.json` with the keys `count_09` and `count_05`.

## Constraints
- Project path: `/home/user/project`
- The script must wait a few seconds after adding the document to ensure it is indexed before searching.
- Output file: `/home/user/project/output.json`