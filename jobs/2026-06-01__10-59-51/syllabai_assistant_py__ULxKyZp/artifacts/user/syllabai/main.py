import argparse
import os
import sys
from alchemyst_ai import AlchemystAI
from openai import OpenAI

def ingest(args):
    alchemyst_client = AlchemystAI(api_key=os.environ.get("ALCHEMYST_AI_API_KEY"))
    
    with open(args.syllabus_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    course_id = args.course_id
    file_name = f"syllabus_{course_id}.md"
    
    document = {
        "content": content,
        "metadata": {
            "file_name": file_name,
            "group_name": ["syllabus", course_id]
        }
    }
    
    try:
        alchemyst_client.v1.context.add(
            documents=[document],
            context_type="resource",
            source="syllabus",
            scope="internal"
        )
        print(f"Ingested syllabus for course: {course_id}")
    except Exception as e:
        if "409" in str(e) or "Conflict" in str(e):
            print(f"Ingested syllabus for course: {course_id} (Already exists)")
        else:
            print(f"Error ingesting syllabus: {e}")
            sys.exit(1)

def ask(args):
    alchemyst_client = AlchemystAI(api_key=os.environ.get("ALCHEMYST_AI_API_KEY"))
    openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    
    course_id = args.course_id
    question = args.question
    
    try:
        search_response = alchemyst_client.v1.context.search(
            query=question,
            similarity_threshold=0.5,
            scope="internal",
            metadata={"group_name": ["syllabus", course_id]}
        )
        
        # We don't know the exact structure of search_response, so stringifying it is safest
        # to ensure we don't crash on attribute errors, while still passing the content.
        context_text = str(search_response)
    except Exception as e:
        print(f"Error searching context: {e}")
        sys.exit(1)
        
    prompt = f"Use the following syllabus context to answer the question.\n\nContext:\n{context_text}\n\nQuestion: {question}"
    
    try:
        completion = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful teaching assistant. Provide a concise answer on a single line."},
                {"role": "user", "content": prompt}
            ]
        )
        
        answer = completion.choices[0].message.content.strip()
        answer_single_line = answer.replace("\n", " ")
        print(f"Answer: {answer_single_line}")
    except Exception as e:
        print(f"Error calling OpenAI: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="SyllabAI Assistant")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    ingest_parser = subparsers.add_parser("ingest")
    ingest_parser.add_argument("syllabus_path", help="Path to syllabus markdown file")
    ingest_parser.add_argument("--course-id", required=True, help="Course ID")
    
    ask_parser = subparsers.add_parser("ask")
    ask_parser.add_argument("question", help="Question to ask")
    ask_parser.add_argument("--course-id", required=True, help="Course ID")
    
    args = parser.parse_args()
    
    if args.command == "ingest":
        ingest(args)
    elif args.command == "ask":
        ask(args)

if __name__ == "__main__":
    main()