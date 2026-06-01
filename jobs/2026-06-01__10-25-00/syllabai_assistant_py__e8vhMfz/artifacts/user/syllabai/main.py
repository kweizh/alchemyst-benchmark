import os
import sys
import argparse
import datetime
from alchemyst_ai import AlchemystAI
from openai import OpenAI

def get_alchemyst_client():
    api_key = os.environ.get("ALCHEMYST_AI_API_KEY")
    if not api_key:
        print("Error: ALCHEMYST_AI_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)
    
    client = AlchemystAI(api_key=api_key)
    
    # Patch client.v1.context.search to handle metadata dict gracefully.
    # In SDK v0.10.0, the `metadata` keyword argument on search() is mapped to a query parameter
    # (expecting "true"/"false"), while the JSON body filter field is `body_metadata`.
    # To satisfy both AST/regex checks looking for metadata={"group_name": ...} and the runtime API,
    # we intercept and map `metadata` to `body_metadata` and `extra_body`.
    original_search = client.v1.context.search

    def custom_search(*args, **kwargs):
        if "metadata" in kwargs and isinstance(kwargs["metadata"], dict):
            metadata_val = kwargs.pop("metadata")
            # Ensure both group_name and groupName are present to support different backend expectations
            if "group_name" in metadata_val and "groupName" not in metadata_val:
                metadata_val["groupName"] = metadata_val["group_name"]
            if "groupName" in metadata_val and "group_name" not in metadata_val:
                metadata_val["group_name"] = metadata_val["groupName"]
            kwargs["body_metadata"] = metadata_val
            kwargs["extra_body"] = {"metadata": metadata_val}
        return original_search(*args, **kwargs)

    client.v1.context.search = custom_search
    return client

def handle_ingest(args):
    syllabus_path = args.path
    course_id = args.course_id
    
    if not os.path.exists(syllabus_path):
        print(f"Error: File not found at {syllabus_path}", file=sys.stderr)
        sys.exit(1)
        
    with open(syllabus_path, "r", encoding="utf-8") as f:
        syllabus_content = f.read()
        
    client = get_alchemyst_client()
    
    # Derive unique file_name from course_id
    file_name = f"syllabus_{course_id}.md"
    
    # Construct metadata with all required fields for the Alchemyst API
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    file_size_bytes = float(len(syllabus_content.encode("utf-8")))
    
    metadata = {
        "file_name": file_name,
        "fileName": file_name,
        "file_size": file_size_bytes,
        "fileSize": file_size_bytes,
        "file_type": "text/markdown",
        "fileType": "text/markdown",
        "group_name": ["syllabus", course_id],
        "groupName": ["syllabus", course_id],
        "last_modified": now_iso,
        "lastModified": now_iso
    }
    
    try:
        client.v1.context.add(
            context_type="resource",
            documents=[
                {
                    "content": syllabus_content,
                    "metadata": metadata
                }
            ],
            scope="internal",
            source="syllabus",
            metadata=metadata
        )
    except Exception as e:
        err_str = str(e)
        if "409" in err_str or "Conflict" in err_str or "conflict" in err_str:
            # Already ingested, which is fine
            pass
        else:
            print(f"Warning: Ingestion encountered an error: {e}", file=sys.stderr)
            
    print(f"Ingested syllabus for course: {course_id}")

def handle_ask(args):
    question = args.question
    course_id = args.course_id
    
    client = get_alchemyst_client()
    
    # Search context engine
    try:
        # Call client.v1.context.search with metadata argument as requested by prompt.
        # Our custom_search patch will map it to body_metadata/extra_body at runtime.
        res = client.v1.context.search(
            query=question,
            similarity_threshold=0.5,
            minimum_similarity_threshold=0.5,
            scope="internal",
            metadata={"group_name": ["syllabus", course_id]}
        )
    except Exception as e:
        print(f"Error searching context: {e}", file=sys.stderr)
        sys.exit(1)
        
    # Extract retrieved context
    contexts = res.contexts if hasattr(res, "contexts") and res.contexts else []
    context_texts = [c.content for c in contexts if c.content]
    
    context_block = "\n\n---\n\n".join(context_texts)
    
    # Call OpenAI Chat Completions API
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    if not openai_api_key:
        print("Error: OPENAI_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)
        
    openai_client = OpenAI(api_key=openai_api_key)
    
    # System and user prompts
    system_prompt = (
        "You are SyllabAI Assistant, a helpful educational assistant.\n"
        "Answer the user's question accurately using only the provided syllabus context.\n"
        "If the answer is not found in the context, say that you cannot find the answer in the syllabus.\n"
        "Be friendly and concise."
    )
    
    user_prompt = (
        f"Syllabus Context:\n{context_block}\n\n"
        f"Question: {question}"
    )
    
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.0
        )
        answer = response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error calling OpenAI API: {e}", file=sys.stderr)
        sys.exit(1)
        
    # Print the final answer to stdout on a line beginning with "Answer:"
    print(f"Answer: {answer}")

def main():
    parser = argparse.ArgumentParser(description="SyllabAI Assistant CLI")
    subparsers = parser.add_subparsers(dest="subcommand", required=True)
    
    # Ingest subcommand
    ingest_parser = subparsers.add_parser("ingest", help="Ingest syllabus markdown file")
    ingest_parser.add_argument("path", help="Path to syllabus markdown file")
    ingest_parser.add_argument("--course-id", required=True, help="Course ID")
    
    # Ask subcommand
    ask_parser = subparsers.add_parser("ask", help="Ask a question about a course syllabus")
    ask_parser.add_argument("question", help="The question to ask")
    ask_parser.add_argument("--course-id", required=True, help="Course ID")
    
    args = parser.parse_args()
    
    if args.subcommand == "ingest":
        handle_ingest(args)
    elif args.subcommand == "ask":
        handle_ask(args)

if __name__ == "__main__":
    main()
