import json
import os
import datetime

MEMORY_FILE = "memory.json"

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return {"conversations": [], "errors": [], "profile": {"name": "Partner", "preferences": {}}}

def save_memory(mem):
    with open(MEMORY_FILE, "w") as f:
        json.dump(mem, f, indent=2)

def add_conversation(user, assistant):
    mem = load_memory()
    mem["conversations"].append({
        "timestamp": datetime.datetime.now().isoformat(),
        "user": user,
        "assistant": assistant
    })
    # Keep last 200 entries
    if len(mem["conversations"]) > 200:
        mem["conversations"] = mem["conversations"][-200:]
    save_memory(mem)

def add_error(context, correction):
    mem = load_memory()
    mem["errors"].append({"context": context, "correction": correction})
    save_memory(mem)

def get_relevant_errors(query, n=2):
    # Simple keyword matching (no embeddings, lightweight)
    mem = load_memory()
    keywords = query.lower().split()
    matches = []
    for err in mem["errors"]:
        score = sum(1 for w in keywords if w in err["context"].lower())
        if score > 0:
            matches.append(err)
            if len(matches) >= n:
                break
    return matches

def get_user_profile():
    mem = load_memory()
    return json.dumps(mem["profile"])
