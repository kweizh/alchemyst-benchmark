import os
import json
import argparse
from alchemyst_ai import AlchemystAI
from openai import OpenAI

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--turns", required=True)
    parser.add_argument("--user-id", required=True)
    parser.add_argument("--session-id", required=True)
    args = parser.parse_args()

    zealt_run_id = os.environ.get("ZEALT_RUN_ID", "")
    if zealt_run_id:
        user_id = f"{args.user_id}-{zealt_run_id}"
        session_id = f"{args.session_id}-{zealt_run_id}"
    else:
        user_id = args.user_id
        session_id = args.session_id

    with open(args.turns, "r") as f:
        turns = json.load(f)

    alchemyst_client = AlchemystAI()
    openai_client = OpenAI()

    transcript = []

    for i, turn in enumerate(turns):
        # 1. Retrieve memories
        search_res = alchemyst_client.v1.context.search(
            query=turn,
            scope="internal",
            user_id=user_id,
            minimum_similarity_threshold=0.0,
            similarity_threshold=1.0
        )
        
        # Extract memories
        memories = []
        if hasattr(search_res, "contexts") and search_res.contexts:
            for ctx in search_res.contexts:
                if hasattr(ctx, "content") and ctx.content:
                    memories.append(ctx.content)
                    
        memory_text = "\n\n".join(memories)
        
        print(f"DEBUG: Retrieved memories for turn {i}: {memory_text}")
        
        # 2. Build prompt
        system_msg = "You are a helpful assistant. Use the retrieved memories to personalize answers."
        if memory_text:
            system_msg += f"\n\nRetrieved Memories:\n{memory_text}"
            
        messages = [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": turn}
        ]
        
        # 3. Call OpenAI
        completion = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )
        reply = completion.choices[0].message.content
        
        # 4. Save memory
        alchemyst_client.v1.context.memory.add(
            session_id=session_id,
            contents=[{"content": f"User said: {turn}\nAssistant said: {reply}"}],
            extra_body={"user_id": user_id}
        )
        
        print(f"ASSISTANT[{i}]: {reply}")
        
        transcript.append({
            "turn": i,
            "user": turn,
            "assistant": reply
        })
        
    with open("/home/user/myproject/transcript.json", "w") as f:
        json.dump(transcript, f, indent=2)

if __name__ == "__main__":
    main()
