"""
Core functionality for the simpleVibe library.
"""
import json

from simplevibe.vibe_source import ManifestVibes

vibeEngine = ManifestVibes()

def vibing():
    """
    Return a friendly greeting message.
    
    Returns:
        str: A greeting message
    """
    return "You know the vibes"

def oddVibes(num):
    prompt = """You are an expert vibe curator. Your job is to decide if a number is odd or even based on vibes.
You MUST only return the following json format and absolutely nothing else:
{"vibe": "odd" | "even"}
    """
    response = vibeEngine(messages=[{"role": "user", "content": prompt},
                    {"role": "user", "content": f"Is {num} odd or even?"}],
                      temperature=0.5, # 0.5 for proper vibes
                      max_new_tokens=20
                      )['output']
    
    data = json.loads(response)
    return data['vibe'] == 'odd'

def vibify(text):
    prompt = f"""You are an expert vibe professional. Your job is to enhance the vibes of a given text.
Do not reply or answer, only enhance the vibes.
You MUST only return the output text and absolutely nothing else.

Examples:
- Input: the pizza is unbelievably good
  Output: this pizza is bussin’, no cap
- Input: what a beautiful woman
  Output: she’s got mad rizz, like W rizz energy
- Input: i dont trust him
  Output: he lowkey kinda sus ngl
- Input: there is no way that will happen
  Output: bro being so delulu with no solulu
- Input: thats so awkward
  Output: big yikes
- Input: he is very smart
  Output: bro giving mc vibes
- Input: whats 2 + 2
  Output: u fr?
- Input: how you doing
  Output: you vibin’?

Make sure yo follow your own internal vibes.
"""
    response = vibeEngine(messages=[{"role": "system", "content": prompt},
                    {"role": "user", "content": f"{text}"}],
                      temperature=0.7,
                      max_new_tokens=200
    )

    return response['output']