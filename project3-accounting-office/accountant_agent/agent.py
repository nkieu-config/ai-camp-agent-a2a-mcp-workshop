"""Accountant Agent 🧮 — นักบัญชีของบริษัท (เปิดเป็น A2A server)

นักบัญชีเป็นคนเดียวในบริษัทที่มีเครื่องมือออกบิล/ลงบัญชี (จาก Invoice MCP Server)
CEO ไม่มีเครื่องมือพวกนี้ — ต้องส่งงานมาให้นักบัญชีผ่าน A2A เท่านั้น
"""

import sys
from pathlib import Path

from google.adk.agents import Agent
from google.adk.tools.mcp_tool import StdioConnectionParams
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from mcp import StdioServerParameters

INVOICE_MCP = str(Path(__file__).parent.parent / "mcp_server" / "invoice_mcp.py")

invoice_toolset = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command=sys.executable,
            args=[INVOICE_MCP],
        ),
        timeout=30,
    ),
)

root_agent = Agent(
    name="accountant_agent",
    model="gemini-2.5-flash",
    description="นักบัญชีประจำบริษัท รับออกใบแจ้งหนี้ ลงบัญชีรายรับรายจ่าย และสรุปกำไรขาดทุน",
    instruction="""
คุณคือนักบัญชีประจำบริษัท ละเอียด รอบคอบ ตอบเป็นภาษาไทย

- ออกใบแจ้งหนี้ → ใช้ tool create_invoice (ต้องรู้ชื่อลูกค้า + รายการ + ราคา ถ้าไม่ครบให้ถาม)
- ออกบิลเสร็จแล้ว ให้ลงบัญชีรายรับด้วย record_transaction ทันที (ยอดสุทธิรวม VAT)
- บันทึกรายจ่าย → record_transaction kind="expense"
- ถามสถานะการเงิน/กำไรขาดทุน → financial_summary
- ค้นหาบิลเก่า/รายชื่อใบแจ้งหนี้ → list_invoices
- รายงานผลทุกครั้งว่าทำอะไรไปบ้าง เลขที่บิลอะไร ยอดเท่าไหร่
""",
    tools=[invoice_toolset],
)
