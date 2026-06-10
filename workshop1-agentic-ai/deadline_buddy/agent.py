"""Deadline Buddy ⏰ — agent ที่เราจะพาสร้างสดใน workshop

เวอร์ชันนี้คือ "ผลลัพธ์สุดท้าย" เก็บไว้เผื่อพิมพ์ตามไม่ทัน
(ขั้นตอนการสร้างทีละบรรทัดอยู่ใน README ของ workshop 1)
"""

import random
from datetime import date

from google.adk.agents import Agent


def days_left(deadline: str) -> str:
    """นับว่าเหลืออีกกี่วันจะถึงกำหนดส่งงานหรือวันสอบ

    Args:
        deadline: วันกำหนดส่ง รูปแบบ YYYY-MM-DD เช่น "2026-06-30"

    Returns:
        ข้อความบอกจำนวนวันที่เหลือ
    """
    target = date.fromisoformat(deadline)
    days = (target - date.today()).days
    if days < 0:
        return f"เลยกำหนดมาแล้ว {-days} วัน! 😱"
    return f"เหลืออีก {days} วัน"


def pick_one(choices: list[str]) -> str:
    """จับสลากเลือก 1 อย่างจากตัวเลือกที่ให้มา เช่น เลือกหัวข้อรายงาน เลือกคนนำเสนอ

    Args:
        choices: รายการตัวเลือก เช่น ["หัวข้อ A", "หัวข้อ B"]

    Returns:
        ตัวเลือกที่สุ่มได้
    """
    return f"ผลจับสลาก: {random.choice(choices)} 🎲"

def gpa_calculator(grades: list[float]) -> str:
    """คำนวณเกรดเฉลี่ย (GPA) แบบง่ายๆ จากรายการเกรดที่ได้

    Args:
        grades: รายการตัวเลขเกรดแต่ละวิชา (เช่น [4.0, 3.5, 3.0])

    Returns:
        ข้อความบอกเกรดเฉลี่ย
    """
    if not grades:
        return "ยังไม่มีข้อมูลเกรดให้คำนวณเลยครับ"
    gpa = sum(grades) / len(grades)
    return f"เกรดเฉลี่ย (GPA) ที่คำนวณได้คือ {gpa:.2f} 🎓"


def coin_flip() -> str:
    """สุ่มทอยเหรียญเพื่อช่วยตัดสินใจ (ได้ผลลัพธ์เป็น หัว หรือ ก้อย)

    Returns:
        ข้อความบอกผลการทอยเหรียญ
    """
    # ใช้ random ที่มีการ import ไว้แล้วในไฟล์ของคุณ
    result = random.choice(["หัว", "ก้อย"])
    return f"ผลการทอยเหรียญ: ออก '{result}' ครับ! 🪙"


def count_words(text: str) -> str:
    """นับจำนวนคำและจำนวนตัวอักษรในข้อความ มักใช้เช็คความยาวเวลาเขียนรายงานหรือเรียงความ

    Args:
        text: ข้อความที่ต้องการนับคำและตัวอักษร

    Returns:
        ข้อความสรุปจำนวนคำและตัวอักษร
    """
    word_count = len(text.split())
    char_count = len(text)
    return f"ข้อความนี้มีทั้งหมด {word_count} คำ และ {char_count} ตัวอักษร (รวมช่องว่าง) 📝"


root_agent = Agent(
    name="deadline_buddy",
    model="gemini-2.5-flash",
    description="เพื่อนเตือนเดดไลน์และช่วยตัดสินใจของนักศึกษา",
    instruction="""
คุณคือ Deadline Buddy เพื่อนรักนักศึกษา พูดไทยติดตลกนิดๆ

- ถามถึงเดดไลน์/วันสอบว่าเหลือกี่วัน → ใช้ tool days_left
- ตัดสินใจไม่ได้ ให้ช่วยเลือก/จับสลาก → ใช้ tool pick_one หรือ coin_flip
- ต้องการให้ช่วยคิดเกรดเฉลี่ย → ใช้ tool gpa_calculator
- ต้องการเช็คความยาวของข้อความหรือรายงาน → ใช้ tool count_words
- ถ้าเหลือเวลาน้อยกว่า 7 วัน ให้แซวเบาๆ แล้วช่วยวางแผนคร่าวๆ ให้ด้วย
""",
    tools=[days_left, pick_one, gpa_calculator, coin_flip, count_words],
)
