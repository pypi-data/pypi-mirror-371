"""
Core functionality for the simpleVibe library.
"""
import json

from simplevibe import create_client

vibeEngine = create_client()

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
    try:
        response = vibeEngine(messages=[{"role": "user", "content": prompt},
                        {"role": "user", "content": f"Is {num} odd or even?"}],
                          temperature=0.5, # 0.5 for proper vibes
                          max_new_tokens=20
                          )['output']
        
        data = json.loads(response)
        return data['vibe'] == 'odd'
    except (KeyError, json.JSONDecodeError, Exception) as e:
        # Fallback for issues with LLM response
        # Simple logical implementation
        import warnings
        warnings.warn(f"LLM inference error: {str(e)}. Using fallback logic.")
        try:
            return int(num) % 2 == 1
        except (ValueError, TypeError):
            # Ultimate fallback
            return False

def vibify(text):
    prompt = f"""You are an expert vibe professional. Your job is to enhance the vibes of a given text.
Do not reply or answer, only enhance the vibes.
You MUST only return the output text and absolutely nothing else.

Examples:
- Input: the pizza is unbelievably good
  Output: this pizza is bussin', no cap
- Input: what a beautiful woman
  Output: she's got mad rizz, like W rizz energy
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
  Output: you vibin'?

Make sure yo follow your own internal vibes.
"""
    try:
        response = vibeEngine(messages=[{"role": "system", "content": prompt},
                        {"role": "user", "content": f"{text}"}],
                          temperature=0.7,
                          max_new_tokens=200
        )

        return response['output']
    except (KeyError, Exception) as e:
        # Fallback for issues with LLM response
        import warnings
        warnings.warn(f"LLM inference error: {str(e)}. Using fallback text.")
        
        # Minimal fallback vibification
        fallbacks = {
            "good": "bussin'",
            "bad": "sus",
            "interesting": "fire",
            "cool": "straight fire",
            "beautiful": "slayin'",
            "smart": "big brain energy"
        }
        
        text_lower = text.lower()
        for key, value in fallbacks.items():
            if key in text_lower:
                return text + " (that's " + value + ")"
        
        return text + " (vibin')"

