from google import genai
import os
import json
import re
from dotenv import load_dotenv

# --- Načtení API klíče ---
load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY nebyl nalezen. Zkontrolujte .env soubor!")

# Inicializace klienta
client = genai.Client(api_key=api_key)

# --- Nástroj / funkce ---
def add_numbers(a: int, b: int) -> int:
    """Sečte dvě čísla a vrátí výsledek."""
    return a + b

# --- Prompt pro model ---
prompt = """
Jsi asistent s přístupem k nástroji 'add_numbers(a,b)'.
Úkol: Sečti čísla 42 a 58.

DŮLEŽITÉ:
- Odpověď napiš **pouze** ve formátu JSON:
{
  "tool": "add_numbers",
  "args": {"a": 42, "b": 58}
}
- Nepiš nic jiného, žádný komentář.
"""

# --- Volání LLM ---
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt
)

llm_output = response.text.strip()
print("--- Odpověď LLM ---")
print(llm_output)

# --- Pokus o dekódování JSON ---
tool_data = None
try:
    tool_data = json.loads(llm_output)
except json.JSONDecodeError:
    # Fallback: vyhledání čísla a b pomocí regex
    match = re.search(r'"a":\s*(\d+).*"b":\s*(\d+)', llm_output)
    if match:
        tool_data = {
            "tool": "add_numbers",
            "args": {
                "a": int(match.group(1)),
                "b": int(match.group(2))
            }
        }

if tool_data and tool_data.get("tool") == "add_numbers":
    a = tool_data["args"]["a"]
    b = tool_data["args"]["b"]
    result = add_numbers(a, b)
    print("\n--- Výsledek nástroje ---")
    print(f"{a} + {b} = {result}")

    # --- Poslání výsledku zpět modelu pro finální odpověď ---
    follow_up_prompt = f"Výpočetní funkce 'add_numbers' vrátila hodnotu: {result}. Napiš odpověď uživateli."
    follow_up_response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=follow_up_prompt
    )
    print("\n--- Finální odpověď LLM ---")
    print(follow_up_response.text)
else:
    print("\n--- Model neposlal platnou instrukci pro nástroj ---")

