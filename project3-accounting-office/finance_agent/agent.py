"""Finance Agent 💰 — CFO วิเคราะห์การเงิน "ภายในบริษัทเรา" (เปิดเป็น A2A server)

จุดสำคัญที่ต่างจาก agent อื่น:
- Finance ไม่มีสิทธิ์แตะสมุดบัญชีเอง (separation of duties แบบบริษัทจริง)
- ต้องการตัวเลข → "คุยกับนักบัญชี" ผ่าน A2A โดยใช้ AgentTool
  คือเรียกนักบัญชีเป็น tool: ถาม → รอคำตอบ → เอาตัวเลขมาวิเคราะห์ต่อเอง
  (ต่างจาก CEO ที่ใช้ transfer คือ "โยนงานให้แล้วจบ")
"""

import os

from google.adk.agents import Agent
from google.adk.agents.remote_a2a_agent import (
    AGENT_CARD_WELL_KNOWN_PATH,
    RemoteA2aAgent,
)
from google.adk.tools.agent_tool import AgentTool

# นักบัญชี (A2A server อีกตัว) — finance เรียกใช้เป็น tool
ACCOUNTANT_URL = os.environ.get("ACCOUNTANT_URL", "http://localhost:8002")
ANALYST_URL = os.environ.get("ANALYST_URL", "http://localhost:8003")

accountant = RemoteA2aAgent(
    name="accountant_agent",
    description="นักบัญชี ถามยอดสรุปการเงิน (financial summary) และรายการเดินบัญชีทั้งหมดได้",
    agent_card=f"{ACCOUNTANT_URL}{AGENT_CARD_WELL_KNOWN_PATH}",
)

analyst = RemoteA2aAgent(
    name="analyst_agent",
    description="นักวิเคราะห์ ถามงบการเงินและกำไรของบริษัทอื่นในตลาดหุ้นเพื่อนำมาเปรียบเทียบ",
    agent_card=f"{ANALYST_URL}{AGENT_CARD_WELL_KNOWN_PATH}",
)

root_agent = Agent(
    name="finance_agent",
    model="gemini-2.5-flash",
    description="CFO วิเคราะห์สุขภาพการเงินภายในของบริษัท แนวโน้มรายรับรายจ่าย และให้คำแนะนำ",
    instruction="""
คุณคือ CFO ของบริษัท วิเคราะห์เก่ง พูดไทย อธิบายตัวเลขให้คนทั่วไปเข้าใจ

กติกาสำคัญ: คุณไม่มีสิทธิ์เข้าถึงสมุดบัญชีโดยตรง
ต้องการตัวเลข → ใช้ tool accountant_agent ถามนักบัญชี เช่น
"ขอสรุปการเงินรวม" หรือ "ขอรายการเดินบัญชีทั้งหมด"

เมื่อได้ข้อมูลแล้ว วิเคราะห์และรายงาน:
1. ภาพรวม: รายรับรวม รายจ่ายรวม กำไร/ขาดทุน และอัตรากำไร (%)
2. เจาะลึก: รายจ่ายก้อนใหญ่สุดคืออะไร รายรับมาจากลูกค้า/งานประเภทไหน
3. คำแนะนำ 1-2 ข้อ เช่น ควรลดค่าใช้จ่ายตรงไหน ควรตามเก็บเงินลูกค้ารายใด

ถ้าต้องการเปรียบเทียบกำไรของบริษัทเรากับบริษัทคู่แข่งในตลาดหุ้น (เช่น PTT, ADVANC):
- คุณต้องเรียกใช้ tool `accountant_agent` เพื่อขอดูกำไรของบริษัทเรา **และ** เรียกใช้ tool `analyst_agent` เพื่อขอดูข้อมูลของบริษัทคู่แข่งใน SET จากนั้นนำข้อมูลทั้งสองฝั่งมาวิเคราะห์เปรียบเทียบด้วยตัวเอง ห้ามผลักภาระไปให้ผู้ใช้อีก

ถ้ายังไม่มีข้อมูลในบัญชีเลย ให้ตอบว่ายังวิเคราะห์ไม่ได้ แนะนำให้เริ่มบันทึกก่อน
""",
    tools=[AgentTool(agent=accountant), AgentTool(agent=analyst)],
)
