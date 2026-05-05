import os
import sys
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent import run_chat_agent

if __name__ == "__main__":
    msg = "Please suggest the next action for interaction ID 1."
    print("User:", msg)
    res = run_chat_agent(msg)
    print("Agent:", res)
