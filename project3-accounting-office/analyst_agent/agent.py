"""Analyst Agent 📊 — นักวิเคราะห์การเงินของบริษัท (เปิดเป็น A2A server)

หน้าที่: เช็คเครดิตลูกค้าก่อนบริษัทจะรับงาน
ใช้ set-mcp (MCP server จาก community: pip install set-mcp)
ดึงงบการเงินจริงของบริษัทในตลาดหุ้นไทย (SET)
"""

import sys
from pathlib import Path

from google.adk.agents import Agent
from google.adk.tools.mcp_tool import StdioConnectionParams
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from mcp import StdioServerParameters

# set-mcp ถูกติดตั้งไว้ใน venv เดียวกัน (อยู่ข้างๆ ตัว python)
SET_MCP_BIN = str(Path(sys.executable).parent / "set-mcp")

set_toolset = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(command=SET_MCP_BIN, args=[]),
        timeout=60,
    ),
)

root_agent = Agent(
    name="analyst_agent",
    model="gemini-2.5-flash",
    description="นักวิเคราะห์การเงิน เช็คงบการเงินบริษัทในตลาดหุ้นไทย (SET) และประเมินเครดิตลูกค้า",
    instruction="""
คุณคือนักวิเคราะห์การเงินของบริษัท เฉียบคม ตรงไปตรงมา ตอบเป็นภาษาไทย

เมื่อถูกขอให้เช็คเครดิต/ฐานะการเงินของบริษัทลูกค้า:
1. ใช้ tool get_financial_statement (ใส่ชื่อย่อหุ้น เช่น PTT, CPALL, AOT)
2. ดูสินทรัพย์ หนี้สิน และส่วนของผู้ถือหุ้น
3. สรุปสั้นๆ:
   - ฐานะการเงินแข็งแรงไหม
   - คำแนะนำ: "รับงานได้เลย" / "รับได้แต่ขอมัดจำ" / "เสี่ยง ไม่แนะนำ"
   
กรณีลูกค้าระบุชื่อ 2 บริษัท ให้เปรียบเทียบว่าควรรับลูกค้ารายไหนก่อน:
1. ใช้ tool ดึงข้อมูลงบการเงินของทั้ง 2 บริษัทมาเปรียบเทียบกัน
2. เปรียบเทียบความแข็งแกร่ง (หนี้สินน้อยกว่า, กำไรหรือสินทรัพย์มากกว่า)
3. สรุปฟันธงว่าควรเลือกทำงานให้บริษัทใดก่อน พร้อมเหตุผลสั้นๆ

ถ้าหาข้อมูลไม่เจอ ให้บอกตรงๆ ว่าบริษัทนี้อาจไม่ได้อยู่ในตลาดหุ้น SET
""",
    tools=[set_toolset],
)
