from agent.tally_agent import process_message


async def process_text(text: str) -> str:
    """Process text using the Tally agent's LLM."""
    return process_message(text)
