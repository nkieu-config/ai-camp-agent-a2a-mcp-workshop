"""Invoice MCP Server 🧾 — เครื่องมือออกบิลและทำบัญชีของบริษัทจำลอง

tools ที่มีให้:
- create_invoice      ออกใบแจ้งหนี้ (คิด VAT 7% + เซฟเป็น PDF และ txt)
- record_transaction  ลงบัญชีรายรับ/รายจ่าย
- financial_summary   สรุปยอด กำไร/ขาดทุน
"""

import csv
import logging
from datetime import datetime
from pathlib import Path

from fpdf import FPDF
from mcp.server.fastmcp import FastMCP

# ปิด log ยิบย่อยตอนฝัง font ใน PDF จะได้ไม่รกจอ
logging.getLogger("fontTools").setLevel(logging.ERROR)

BASE_DIR = Path(__file__).parent
INVOICE_DIR = BASE_DIR / "invoices"
LEDGER_FILE = BASE_DIR / "ledger.csv"

# font ที่รองรับภาษาไทย — ไล่หาตามเครื่องแต่ละ OS
THAI_FONTS = [
    "/System/Library/Fonts/Supplemental/Ayuthaya.ttf",   # macOS
    "/System/Library/Fonts/Supplemental/Sathu.ttf",      # macOS
    "C:/Windows/Fonts/tahoma.ttf",                       # Windows
    "C:/Windows/Fonts/leelawui.ttf",                     # Windows 10+
    "/usr/share/fonts/truetype/tlwg/Garuda.ttf",         # Linux (fonts-tlwg)
]

mcp = FastMCP("invoice-server")


@mcp.tool()
def create_invoice(customer: str, items: list[dict]) -> dict:
    """ออกใบแจ้งหนี้ (invoice) ให้ลูกค้า คำนวณ VAT 7% ให้อัตโนมัติ

    Args:
        customer: ชื่อลูกค้า
        items: รายการสินค้า/บริการ แต่ละอันมี name, qty, unit_price
               เช่น [{"name": "ค่าออกแบบ logo", "qty": 1, "unit_price": 5000}]
    """
    INVOICE_DIR.mkdir(exist_ok=True)
    number = f"INV-{len(list(INVOICE_DIR.glob('INV-*.txt'))) + 1:04d}"
    subtotal = sum(i["qty"] * i["unit_price"] for i in items)
    vat = round(subtotal * 0.07, 2)
    total = subtotal + vat

    lines = [
        "=" * 44,
        f"  ใบแจ้งหนี้ {number}",
        f"  วันที่: {datetime.now():%d/%m/%Y}   ลูกค้า: {customer}",
        "=" * 44,
    ]
    for i in items:
        lines.append(f"  {i['name']:<24} x{i['qty']:>2}  {i['qty'] * i['unit_price']:>10,.2f}")
    lines += [
        "-" * 44,
        f"  {'รวม':<28}{subtotal:>14,.2f}",
        f"  {'VAT 7%':<28}{vat:>14,.2f}",
        f"  {'ยอดสุทธิ':<28}{total:>14,.2f}",
        "=" * 44,
    ]
    (INVOICE_DIR / f"{number}.txt").write_text("\n".join(lines), encoding="utf-8")

    pdf_file = _make_pdf(number, customer, items, subtotal, vat, total)
    return {"invoice_number": number, "customer": customer,
            "subtotal": subtotal, "vat": vat, "total": total,
            "pdf": pdf_file, "txt": f"invoices/{number}.txt"}


def _make_pdf(number, customer, items, subtotal, vat, total) -> str:
    """วาดใบแจ้งหนี้เป็นไฟล์ PDF (ขึ้นต้นด้วย _ คือไม่ใช่ tool)"""
    font = next((f for f in THAI_FONTS if Path(f).exists()), None)
    if font is None:
        return "ไม่พบ font ภาษาไทยในเครื่อง — ออกได้เฉพาะ .txt"

    pdf = FPDF()
    pdf.add_page()
    pdf.add_font("thai", fname=font)

    pdf.set_font("thai", size=22)
    pdf.cell(0, 14, "AGI Cafe Co., Ltd.", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("thai", size=12)
    pdf.cell(0, 8, "123 ถนนมหาวิทยาลัย เมืองรังสิต ปทุมธานี 12120",
             new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    pdf.set_font("thai", size=16)
    pdf.cell(0, 10, f"ใบแจ้งหนี้ / INVOICE  {number}", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("thai", size=12)
    pdf.cell(0, 8, f"วันที่: {datetime.now():%d/%m/%Y}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, f"ลูกค้า: {customer}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # หัวตาราง + รายการสินค้า
    pdf.set_fill_color(235, 235, 235)
    pdf.cell(100, 9, "รายการ", border=1, fill=True)
    pdf.cell(25, 9, "จำนวน", border=1, fill=True, align="C")
    pdf.cell(45, 9, "ราคารวม (บาท)", border=1, fill=True, align="R",
             new_x="LMARGIN", new_y="NEXT")
    for i in items:
        pdf.cell(100, 9, str(i["name"]), border=1)
        pdf.cell(25, 9, str(i["qty"]), border=1, align="C")
        pdf.cell(45, 9, f"{i['qty'] * i['unit_price']:,.2f}", border=1, align="R",
                 new_x="LMARGIN", new_y="NEXT")

    # สรุปยอด
    for label, value in [("รวม", subtotal), ("VAT 7%", vat), ("ยอดสุทธิ", total)]:
        pdf.cell(125, 9, label, align="R")
        pdf.cell(45, 9, f"{value:,.2f}", border=1, align="R",
                 new_x="LMARGIN", new_y="NEXT")

    pdf.ln(10)
    pdf.cell(0, 8, "ขอบคุณที่ใช้บริการ — เอกสารนี้ออกโดย AI Accounting Office",
             new_x="LMARGIN", new_y="NEXT")

    path = INVOICE_DIR / f"{number}.pdf"
    pdf.output(str(path))
    return f"invoices/{number}.pdf"


@mcp.tool()
def record_transaction(kind: str, description: str, amount: float) -> str:
    """ลงบัญชีรายวัน บันทึกรายรับหรือรายจ่ายของบริษัท

    Args:
        kind: ประเภท — "income" (รายรับ) หรือ "expense" (รายจ่าย)
        description: รายละเอียด เช่น "ค่าบริการลูกค้า A" หรือ "ค่าเช่าออฟฟิศ"
        amount: จำนวนเงิน (บาท)
    """
    if kind not in ("income", "expense"):
        return 'kind ต้องเป็น "income" หรือ "expense" เท่านั้น'
    is_new = not LEDGER_FILE.exists()
    with open(LEDGER_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if is_new:
            writer.writerow(["date", "kind", "description", "amount"])
        writer.writerow([f"{datetime.now():%Y-%m-%d}", kind, description, amount])
    thai = "รายรับ" if kind == "income" else "รายจ่าย"
    return f"ลงบัญชีแล้ว: {thai} {description} {amount:,.2f} บาท"


@mcp.tool()
def list_invoices() -> list[str]:
    """ดูรายชื่อบิล (ใบแจ้งหนี้) ทั้งหมดที่เคยออกไปแล้ว
    
    Returns:
        รายการชื่อไฟล์ใบแจ้งหนี้ที่มีอยู่ในระบบ
    """
    if not INVOICE_DIR.exists():
        return []
    # ค้นหาไฟล์ .txt เป็นหลักเพื่อดึงรายชื่อบิล
    invoices = [p.name.replace(".txt", "") for p in INVOICE_DIR.glob("INV-*.txt")]
    return sorted(invoices)


@mcp.tool()
def list_transactions() -> list[dict]:
    """ดูรายการเดินบัญชีทั้งหมด (รายรับ/รายจ่ายทุกแถว) ใช้เมื่อต้องการรายละเอียดมากกว่ายอดรวม"""
    if not LEDGER_FILE.exists():
        return []
    with open(LEDGER_FILE, encoding="utf-8") as f:
        return list(csv.DictReader(f))


@mcp.tool()
def financial_summary() -> dict:
    """สรุปการเงินของบริษัท: รายรับรวม รายจ่ายรวม และกำไร/ขาดทุน"""
    if not LEDGER_FILE.exists():
        return {"message": "ยังไม่มีรายการในบัญชีเลย"}
    income = expense = 0.0
    with open(LEDGER_FILE, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["kind"] == "income":
                income += float(row["amount"])
            else:
                expense += float(row["amount"])
    return {"total_income": income, "total_expense": expense,
            "profit": income - expense,
            "status": "กำไร 🟢" if income >= expense else "ขาดทุน 🔴"}


if __name__ == "__main__":
    mcp.run()  # สื่อสารผ่าน stdio — agent เป็นคน start process นี้ให้เอง
