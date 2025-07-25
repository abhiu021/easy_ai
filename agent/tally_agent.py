import os
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv
from tally_agent_prompt import prompt_template

# Load environment variables
load_dotenv()

# Set OpenRouter variables
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["OPENAI_API_BASE"] = os.getenv("OPENAI_API_BASE")  # Needed for OpenRouter

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

# LangChain LLMChain
chain = prompt | llm

# Run loop
def run_agent():
    while True:
        user_input = input("\n💬 Enter a Tally-related query (or type 'exit'):\n> ")
        if user_input.lower() == "exit":
            break
        result = chain.invoke({"user_input": user_input})
        print("\n🧾 Extracted JSON:\n", result)

if __name__ == "__main__":
    run_agent()
