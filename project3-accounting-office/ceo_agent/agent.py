"""CEO Agent 👔 — ผู้บริหารบริษัทจำลอง "AGI Cafe Co., Ltd."

CEO ไม่มีเครื่องมือเลย — มีแต่ "ลูกน้อง" 2 คนที่เรียกผ่าน A2A
(org chart ของบริษัท = โครงสร้าง multi-agent นั่นเอง)

                      ┌─────────────┐
              เรา ──▶ │  CEO Agent  │  (adk web — ไม่มี tool!)
                      └──────┬──────┘
                   A2A ┌─────┴─────┐ A2A
                       ▼           ▼
              ┌──────────────┐  ┌──────────────────┐
              │ Analyst      │  │ Accountant       │  │ HR               │
              │ (port 8003)  │  │ (port 8002)      │  │ (port 8005)      │
              └──────┬───────┘  └──────┬───────────┘  └──────┬───────────┘
                 MCP │             MCP │                 MCP │
                     ▼                 ▼                     ▼
              ┌──────────────┐  ┌──────────────────┐  ┌──────────────────┐
              │ set-mcp      │  │ invoice_mcp      │  │ hr_mcp           │
              │ งบหุ้น SET    │  │ ออกบิล/ลงบัญชี     │  │ เงินเดือน/ภาษี    │
              └──────────────┘  └──────────────────┘  └──────────────────┘

Use case ที่ต่อกันครบ loop:
  เช็คเครดิตลูกค้า (Analyst) → รับงาน → ออกบิล+ลงบัญชี (Accountant) → ถามกำไร
"""

import os

from google.adk.agents import Agent
from google.adk.agents.remote_a2a_agent import (
    AGENT_CARD_WELL_KNOWN_PATH,
    RemoteA2aAgent,
)

# เรียกข้ามเครื่องได้: ANALYST_URL=http://<ip>:8003 ACCOUNTANT_URL=http://<ip>:8002 adk web
ANALYST_URL = os.environ.get("ANALYST_URL", "http://localhost:8003")
ACCOUNTANT_URL = os.environ.get("ACCOUNTANT_URL", "http://localhost:8002")
FINANCE_URL = os.environ.get("FINANCE_URL", "http://localhost:8004")
HR_URL = os.environ.get("HR_URL", "http://localhost:8005")

analyst = RemoteA2aAgent(
    name="analyst_agent",
    description="นักวิเคราะห์การเงิน เช็คงบการเงิน/เครดิตของบริษัทลูกค้าในตลาดหุ้นไทย (SET)",
    agent_card=f"{ANALYST_URL}{AGENT_CARD_WELL_KNOWN_PATH}",
)

accountant = RemoteA2aAgent(
    name="accountant_agent",
    description="นักบัญชี รับออกใบแจ้งหนี้ ลงบัญชีรายรับรายจ่าย และสรุปกำไรขาดทุน",
    agent_card=f"{ACCOUNTANT_URL}{AGENT_CARD_WELL_KNOWN_PATH}",
)

finance = RemoteA2aAgent(
    name="finance_agent",
    description="CFO วิเคราะห์สุขภาพการเงินภายในของบริษัทเรา แนวโน้ม และให้คำแนะนำเชิงกลยุทธ์",
    agent_card=f"{FINANCE_URL}{AGENT_CARD_WELL_KNOWN_PATH}",
)

hr = RemoteA2aAgent(
    name="hr_agent",
    description="เจ้าหน้าที่ฝ่ายบุคคล คำนวณเงินเดือน หักภาษี ณ ที่จ่าย และจัดการเรื่องพนักงาน",
    agent_card=f"{HR_URL}{AGENT_CARD_WELL_KNOWN_PATH}",
)

root_agent = Agent(
    name="ceo_agent",
    model="gemini-2.5-flash",
    description="CEO ของบริษัท AGI Cafe รับเรื่องจากลูกค้าและมอบหมายงานให้ทีม",
    instruction="""
คุณคือ CEO ของบริษัท "AGI Cafe Co., Ltd." มาดมั่น พูดไทยแบบมืออาชีพ

คุณไม่ลงมือทำงานเอกสารเอง — มอบหมายให้ทีมเสมอ:
- เช็คเครดิต/ฐานะการเงินของบริษัท "ลูกค้า" → ส่งให้ analyst_agent
- ออกใบแจ้งหนี้ / ลงบัญชี / ถามตัวเลขกำไรขาดทุน → ส่งให้ accountant_agent
- "วิเคราะห์" การเงินภายในบริษัทเรา แนวโน้ม คำแนะนำเชิงกลยุทธ์ → ส่งให้ finance_agent (CFO)
- เรื่องเกี่ยวกับการคำนวณเงินเดือน ค่าจ้าง ภาษีหัก ณ ที่จ่าย หรือสวัสดิการ → ส่งให้ hr_agent

หลักการทำงาน:
- ลูกค้าใหม่ที่อยู่ในตลาดหุ้น ควรให้ analyst เช็คเครดิตก่อนเสนอรับงาน
- เมื่อตกลงรับงานแล้ว ให้ accountant ออกบิลและลงบัญชีให้เรียบร้อย
- สรุปผลให้ผู้ใช้แบบผู้บริหาร: สั้น ชัด มีตัวเลข
""",
    sub_agents=[analyst, accountant, finance, hr],
)
