You are setting up the initial knowledge base for a customer support agent using the Alchemyst AI TypeScript SDK. 

You need to write a script that ingests a 30-day refund policy document into the context engine and then immediately performs a search to retrieve it based on a user query about refunds. 

**Constraints:**
- You MUST accommodate the SDK parameter inconsistency by using `group_name` when storing the document, but `groupName` when executing the search.
- Metadata values provided during the context addition must strictly be strings or numbers; do not pass nested objects or arrays (except for the group configuration).