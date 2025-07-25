import sys
from agent.tally_agent import process_message, queue


def main() -> None:
    """Read text from stdin and process it with the Tally agent."""
    user_text = sys.stdin.read().strip()
    if not user_text:
        print("No input provided")
        return
    response = process_message(user_text)
    print(response)
    pending = queue.get_pending()
    if pending:
        print(f"Queued XML count: {len(pending)}")


if __name__ == "__main__":
    main()
