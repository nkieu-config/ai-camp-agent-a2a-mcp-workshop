"""เปิด HR Agent เป็น A2A server (port 8005)
"""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

from google.adk.a2a.utils.agent_to_a2a import to_a2a

from hr_agent.agent import root_agent

A2A_HOST = os.environ.get("A2A_HOST", "localhost")

app = to_a2a(root_agent, host=A2A_HOST, port=8005)
