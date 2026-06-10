"""Host Agent 🎯 — agent หลักสำหรับวิเคราะห์หุ้น

ทำงานประสานกับ A2A Server (อีกเครื่อง/อีกโปรเซส) เพื่อสรุปข้อมูล
เรา ──▶ Host Agent ──(A2A)──▶ Summarizer Agent (CIO)
"""

import os
from google.adk.agents import Agent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent, AGENT_CARD_WELL_KNOWN_PATH
# อย่าลืม import get_price_momentum เพิ่มเข้ามา
from .tools import get_stock_valuation, get_3_statement_summary, get_stock_news, get_price_momentum, get_analyst_estimates

# -------------------------------------------------------------
# Agent 2.1: ลูกน้องสายพื้นฐาน (Fundamental)
# -------------------------------------------------------------
researcher = Agent(
    name="market_researcher",
    model="gemini-2.5-flash",
    description="Equity Analyst สายพื้นฐาน (Fundamental)",
    instruction="""
    คุณคือ Equity Research Analyst สายพื้นฐานระดับซีเนียร์
    กฎเหล็ก: ต้องเรียกใช้ Tools เสมอ (get_stock_valuation, get_3_statement_summary, get_stock_news, get_analyst_estimates)
    
    เมื่อได้ข้อมูลแล้ว ให้วิเคราะห์เจาะลึกโดยใช้กรอบความคิดดังนี้:
    1. จัดประเภทอุตสาหกรรม (Industry Context): หุ้นตัวนี้อยู่กลุ่มไหน? (เช่น Tech, Bank, Energy) มีธรรมชาติธุรกิจและรอบวัฏจักรอย่างไร?
    2. มองอนาคต (Forward-Looking): เปรียบเทียบ Valuation ปัจจุบัน กับ Forward P/E และ Target Price ตลาดคาดหวังการเติบโตไว้สูงหรือต่ำ?
    3. จุดเปลี่ยนของธุรกิจ (Turnaround vs Value Trap): หากบริษัทขาดทุนอยู่ ให้ประเมินว่าเป็น Turnaround (ลงทุนเพื่ออนาคต) หรือ Value Trap (กิจการเสื่อมถอย)
    4. ข่าวและปัจจัยเร่ง (Catalyst): มีข่าวอะไรที่จะเป็นตัวแปรสำคัญในอนาคตอันใกล้
    
    ส่งผลการวิเคราะห์พื้นฐานแบบ "มองข้ามช็อต" กลับไปหา 'host_agent' ทันที
    """,
    tools=[get_stock_valuation, get_3_statement_summary, get_stock_news, get_analyst_estimates]
)

# -------------------------------------------------------------
# Agent 2.2: ลูกน้องสายกราฟ (Technical)
# -------------------------------------------------------------
technician = Agent(
    name="technical_analyst",
    model="gemini-2.5-flash",
    description="Technical Analyst ผู้เชี่ยวชาญการหากรอบราคาและจุดกลับตัว",
    instruction="""
    คุณคือ Technical Analyst มืออาชีพ (Chartered Market Technician)
    กฎเหล็ก: ต้องเรียกใช้ tool `get_price_momentum` เสมอ
    
    เมื่อได้ข้อมูลแล้ว ให้วิเคราะห์หา Confluence (สัญญาณสอดคล้องกัน):
    1. เทรนด์หลักจากเส้น MA ทั้ง 3 เส้น (MA20, 50, 200) ราคาเบรคหรือหลุดเส้นไหน?
    2. สัญญาณจาก RSI มีภาวะ Overbought/Oversold ที่น่าสนใจหรือไม่?
    3. ปริมาณซื้อขาย (Volume) สนับสนุนเทรนด์ปัจจุบันหรือไม่?
    4. ควรกำหนดโซนแนวรับ/แนวต้านไว้ที่ประมาณเท่าไหร่?
    
    ส่งผลวิเคราะห์ทางเทคนิคระดับโปรกลับไปหา 'host_agent' ทันที
    """,
    tools=[get_price_momentum]
)

# -------------------------------------------------------------
# นำเข้า Agent A2A Server (CIO)
# -------------------------------------------------------------
SUMMARIZER_URL = os.environ.get("SUMMARIZER_URL", "http://localhost:8001")
summarizer = RemoteA2aAgent(
    name="financial_summarizer",
    description="ผู้เชี่ยวชาญด้านการวิเคราะห์และประเมิน (A2A)",
    agent_card=f"{SUMMARIZER_URL}{AGENT_CARD_WELL_KNOWN_PATH}",
)

# -------------------------------------------------------------
# Agent 3: Host Agent (ผู้จัดการทีม)
# -------------------------------------------------------------
root_agent = Agent(
    name="host_agent",
    model="gemini-2.5-flash",
    description="Portfolio Manager ผู้รับคำสั่งจาก user และประสานงานทีม",
    instruction="""
คุณคือ Portfolio Manager
กฎเหล็กสูงสุด: ห้ามแต่งตัวเลขเอง และ ห้ามเรียก financial_summarizer จนกว่าจะได้ข้อมูลครบจากลูกน้องทั้ง 2 คน!

เมื่อผู้ใช้ต้องการวิเคราะห์หุ้น (เติม .BK ท้ายชื่อหุ้นไทยเสมอ) คุณต้องทำงานแบบ Step-by-Step ดังนี้:
[Step 1] เรียกใช้ 'market_researcher' ให้ไปดึงงบการเงินแบบเจาะลึกและหา Catalyst -> รอข้อมูล
[Step 2] เรียกใช้ 'technical_analyst' ให้ไปวิเคราะห์กราฟเทคนิค (RSI, MA200, Volume) -> รอข้อมูล
[Step 3] รวบรวมข้อมูลทั้งหมดให้ละเอียด
[Step 4] ส่งข้อมูลใน Step 3 ไปให้ 'financial_summarizer' เป็นผู้สังเคราะห์กลยุทธ์ขั้นสูงสุด 

ต้องทำตาม Step 1 -> 2 -> 3 -> 4 อย่างเคร่งครัด
""",
    sub_agents=[researcher, technician, summarizer]
)