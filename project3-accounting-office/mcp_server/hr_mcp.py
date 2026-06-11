"""HR MCP Server 👥 — เครื่องมือฝ่ายบุคคล
มีเครื่องมือคำนวณเงินเดือนและหักภาษี ณ ที่จ่าย
"""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("hr-server")

@mcp.tool()
def calculate_salary_and_tax(base_salary: float, tax_rate_percent: float) -> dict:
    """คำนวณเงินเดือนสุทธิหลังจากหักภาษี ณ ที่จ่าย และประกันสังคม (สมมติคงที่ 750 บาท หรือ 5% ไม่เกิน 15,000 บาท)
    
    Args:
        base_salary: เงินเดือนฐาน (บาท)
        tax_rate_percent: อัตราภาษีหัก ณ ที่จ่าย (%)
    """
    # คำนวณประกันสังคม (5% ของเงินเดือน สูงสุดไม่เกิน 750 บาท)
    social_security = min(base_salary * 0.05, 750.0)
    
    # หักภาษี ณ ที่จ่าย (คิดจากเงินเดือนหลังหักประกันสังคม หรือจากยอดเต็มก็ได้ ในที่นี้คิดจาก base_salary)
    tax_deduction = base_salary * (tax_rate_percent / 100)
    
    net_salary = base_salary - social_security - tax_deduction
    
    return {
        "base_salary": base_salary,
        "social_security_deduction": social_security,
        "tax_rate_percent": tax_rate_percent,
        "tax_deduction": tax_deduction,
        "net_salary": net_salary
    }

if __name__ == "__main__":
    mcp.run()
