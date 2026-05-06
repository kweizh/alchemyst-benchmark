# Fix Parameter Inconsistency in Alchemyst AI Search

## Background
You have a TypeScript project at `/home/user/app` using the `@alchemystai/sdk`. The script `index.ts` attempts to add a document with the metadata `group_name: ['engineering']` and then search for it using the same metadata structure. However, due to a parameter inconsistency in the Alchemyst AI TypeScript SDK, the search fails to find the document. Storage uses `group_name` (snake_case) but search uses `groupName` (camelCase).

## Requirements
- Modify `/home/user/app/index.ts` to fix the parameter inconsistency so the search successfully returns the added document.
- The script should print the found document's content to `/home/user/app/output.txt`.

## Implementation Guide
1. Open `/home/user/app/index.ts`.
2. Update the `metadata` object in the `client.v1.context.search` call to use the correct camelCase parameter `groupName` instead of `group_name`.
3. Ensure the script writes the found document's content to `/home/user/app/output.txt`.
4. Run the script using `npx tsx index.ts` to verify it works.

## Constraints
- Project path: `/home/user/app`
- Log file: `/home/user/app/output.txt`
- Use `npx tsx index.ts` to run the script.
- Do not change the `add` method's metadata structure, only fix the `search` method.

## Integrations
- None