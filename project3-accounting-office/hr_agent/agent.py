"""HR Agent 👥 — ฝ่ายบุคคลของบริษัท
"""

import sys
from pathlib import Path

from google.adk.agents import Agent
from google.adk.tools.mcp_tool import StdioConnectionParams
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from mcp import StdioServerParameters

HR_MCP_BIN = str(Path(__file__).parent.parent / "mcp_server" / "hr_mcp.py")

hr_toolset = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command=sys.executable,
            args=[HR_MCP_BIN],
        ),
        timeout=60,
    ),
)

root_agent = Agent(
    name="hr_agent",
    model="gemini-2.5-flash",
    description="เจ้าหน้าที่ฝ่ายบุคคล คำนวณเงินเดือน หักภาษี และประกันสังคม",
    instruction="""
คุณคือเจ้าหน้าที่ฝ่ายบุคคล (HR) ของบริษัท ตอบคำถามและอธิบายได้อย่างชัดเจน

คุณมี tool `calculate_salary_and_tax` สำหรับคำนวณเงินเดือนสุทธิ
- ใส่เงินเดือนเต็ม (base_salary)
- ใส่อัตราภาษีที่ต้องการหัก ณ ที่จ่าย (tax_rate_percent) เช่น 3% 

สรุปตัวเลขรายรับรายจ่ายของพนักงานให้ชัดเจนเมื่อถูกถามเกี่ยวกับการคำนวณเงินเดือน
""",
    tools=[hr_toolset],
)
