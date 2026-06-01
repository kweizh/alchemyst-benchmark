import argparse
import os
import sys
from alchemyst_ai import AlchemystAI, ConflictError
from openai import OpenAI

def ingest(file_path: str):
    alchemyst_api_key = os.environ.get("ALCHEMYST_AI_API_KEY")
    if not alchemyst_api_key:
        print("Error: ALCHEMYST_AI_API_KEY environment variable is missing.", file=sys.stderr)
        sys.exit(1)
        
    run_id = os.environ.get("ZEALT_RUN_ID", "default_run_id")
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}", file=sys.stderr)
        sys.exit(1)
        
    client = AlchemystAI(api_key=alchemyst_api_key)
    
    # basename
    file_name = f"{file_path}-{run_id}"
    
    try:
        client.v1.context.add(
            context_type="resource",
            documents=[{"content": content}],
            scope="internal",
            source="cli-notes",
            metadata={
                "file_name": file_name,
                "file_size": len(content),
                "file_type": "text/plain",
                "last_modified": "2026-06-01T00:00:00Z"
            }
        )
        print(f"Successfully ingested {file_path}")
    except ConflictError:
        print(f"Document {file_path} already ingested (ConflictError).")
    except Exception as e:
        print(f"Error during ingestion: {e}", file=sys.stderr)
        sys.exit(1)

def ask(question: str):
    alchemyst_api_key = os.environ.get("ALCHEMYST_AI_API_KEY")
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    
    if not alchemyst_api_key:
        print("Error: ALCHEMYST_AI_API_KEY environment variable is missing.", file=sys.stderr)
        sys.exit(1)
    if not openai_api_key:
        print("Error: OPENAI_API_KEY environment variable is missing.", file=sys.stderr)
        sys.exit(1)
        
    alchemyst_client = AlchemystAI(api_key=alchemyst_api_key)
    openai_client = OpenAI(api_key=openai_api_key)
    
    try:
        search_res = alchemyst_client.v1.context.search(
            query=question,
            scope="internal",
            minimum_similarity_threshold=0.0,
            similarity_threshold=1.0
        )
    except Exception as e:
        print(f"Error during search: {e}", file=sys.stderr)
        sys.exit(1)
        
    contexts = search_res.contexts or []
    context_texts = [ctx.content for ctx in contexts if ctx.content]
    
    if context_texts:
        grounding_context = "\n\n".join(context_texts)
        system_prompt = f"You are a helpful assistant. Use the following context to answer the question:\n\n{grounding_context}"
    else:
        system_prompt = "You are a helpful assistant. Note: No specific context was found for this question."
        
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ]
        )
        answer = response.choices[0].message.content
        print(answer)
    except Exception as e:
        print(f"Error calling OpenAI: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 main.py <ingest|ask> [args]")
        sys.exit(1)
        
    command = sys.argv[1]
    
    if command == "ingest":
        if len(sys.argv) != 3:
            print("Usage: python3 main.py ingest <file>")
            sys.exit(1)
        ingest(sys.argv[2])
    elif command == "ask":
        if len(sys.argv) < 3:
            print("Usage: python3 main.py ask <question>")
            sys.exit(1)
        question = " ".join(sys.argv[2:])
        ask(question)
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
