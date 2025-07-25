import os
import time
import threading
import requests
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
from tally_agent_prompt import prompt_template
from tally_tool.client import TallyClient
from agent.utils.queue import WriteQueue

# Load environment variables
load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
CLIENT_ID = os.getenv("CLIENT_ID", "demo")
CLIENT_TOKEN = os.getenv("CLIENT_TOKEN")

# Set OpenRouter variables
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["OPENAI_API_BASE"] = os.getenv("OPENAI_API_BASE")  # Needed for OpenRouter

# Tally client and persistent queue
tally_client = TallyClient()
queue = WriteQueue(os.path.join(os.path.dirname(__file__), "voucher_queue.db"))

# Initialize LLM using environment model
llm = ChatOpenAI(
    base_url=os.getenv("OPENAI_API_BASE"),
    api_key=os.getenv("OPENAI_API_KEY"),
    model="gpt-3.5-turbo"
)

# Build prompt
prompt = PromptTemplate(
    input_variables=["user_input"],
    template=prompt_template
)

# LangChain chain
chain = prompt | llm


def process_message(user_text: str) -> str:
    """Run the LLM chain on the provided text and upload the result."""
    result = chain.invoke({"user_input": user_text})
    try:
        backend_post(
            "/upload_voucher",
            {
                "client_id": CLIENT_ID,
                "data_type": "json",
                "payload": result,
            },
        )
    except requests.HTTPError:
        pass
    return result


def backend_post(route: str, data: dict) -> requests.Response:
    """Helper to POST to the backend with the auth token."""
    headers = {}
    if CLIENT_TOKEN:
        headers["Authorization"] = f"Bearer {CLIENT_TOKEN}"
    url = f"{BACKEND_URL}{route}"
    resp = requests.post(url, data=data, headers=headers)
    resp.raise_for_status()
    return resp


def is_tally_reachable() -> bool:
    """Check if the Tally HTTP endpoint is reachable."""
    try:
        requests.get(tally_client.url, timeout=3)
        return True
    except requests.RequestException:
        return False


def post_xml_with_queue(xml_str: str) -> str | None:
    """Post XML to Tally or queue it if Tally is unreachable."""
    if is_tally_reachable():
        try:
            return tally_client.post_xml(xml_str)
        except requests.RequestException:
            pass
    queue.enqueue(xml_str, "xml")
    return None


def queue_worker() -> None:
    """Background worker to resend queued XML to Tally."""
    while True:
        tasks = queue.get_pending()
        if tasks and is_tally_reachable():
            for task_id, payload, _ in tasks:
                try:
                    tally_client.post_xml(payload)
                    queue.mark_complete(task_id)
                except requests.RequestException:
                    pass
        time.sleep(900)  # 15 minutes


worker_thread = threading.Thread(target=queue_worker, daemon=True)
worker_thread.start()

# Run loop
def run_agent():
    while True:
        user_input = input("\n💬 Enter a Tally-related query (or type 'exit'):\n> ")
        if user_input.lower() == "exit":
            break
        if user_input.lower().startswith("xml "):
            xml_payload = user_input[4:]
            response = post_xml_with_queue(xml_payload)
            if response:
                print("\n🧾 Tally Response:\n", response)
            else:
                print("\n🧾 XML queued for later sending.")
            continue

        result = process_message(user_input)
        print("\n🧾 Extracted JSON:\n", result)

if __name__ == "__main__":
    run_agent()
