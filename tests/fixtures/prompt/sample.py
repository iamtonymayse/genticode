SYSTEM_PROMPT = """
You are a helpful assistant.
Follow the user's instructions carefully.
"""

def use():
    return SYSTEM_PROMPT

# f-string with embedded constant pieces
name = "dev"
F_STR = f"""
system: behave as a bot for {name}
### rules
"""

# Short but keyword-triggering literal
NOTE = "LLM prompt"
