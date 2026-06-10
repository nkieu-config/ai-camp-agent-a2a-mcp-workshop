import yfinance as yf
import pandas as pd
from functools import lru_cache

@lru_cache(maxsize=32)
def get_cached_ticker(ticker: str) -> yf.Ticker:
    """แคช Ticker object เพื่อป้องกันการเรียกข้อมูลซ้ำซ้อน"""
    return yf.Ticker(ticker)

def get_stock_info(ticker: str) -> str:
    """ดึงข้อมูลพื้นฐานและราคาปัจจุบันของหุ้น"""
    try:
        stock = get_cached_ticker(ticker)
        info = stock.info
        
        if "shortName" not in info:
            return f"ไม่พบข้อมูลของหุ้น {ticker} โปรดตรวจสอบสัญลักษณ์หุ้นอีกครั้ง"
            
        summary = info.get('longBusinessSummary', 'ไม่มีข้อมูลรายละเอียดธุรกิจ')
        
        return (
            f"บริษัท: {info.get('shortName', 'N/A')}\n"
            f"อุตสาหกรรม: {info.get('industry', 'N/A')}\n"
            f"ราคาปัจจุบัน: {info.get('currentPrice', 'N/A')} {info.get('currency', '')}\n"
            f"รายละเอียดธุรกิจ: {summary[:500]}..."
        )
    except Exception as e:
        return f"เกิดข้อผิดพลาดในการดึงข้อมูลพื้นฐาน: {e}"

def get_financial_ratios(ticker: str) -> str:
    """ดึงข้อมูลอัตราส่วนทางการเงินที่สำคัญ (P/E, P/B, ROE, Dividend Yield)"""
    try:
        stock = get_cached_ticker(ticker)
        info = stock.info
        
        pe_ratio = info.get('trailingPE', 'N/A')
        pb_ratio = info.get('priceToBook', 'N/A')
        
        roe = info.get('returnOnEquity')
        div_yield = info.get('dividendYield')
        
        roe_str = f"{roe * 100:.2f}%" if isinstance(roe, (int, float)) else "N/A"
        div_yield_str = f"{div_yield * 100:.2f}%" if isinstance(div_yield, (int, float)) else "N/A"
        
        return (
            f"ข้อมูลทางการเงินของ {ticker}:\n"
            f"- P/E Ratio: {pe_ratio}\n"
            f"- P/B Ratio: {pb_ratio}\n"
            f"- ROE: {roe_str}\n"
            f"- Dividend Yield: {div_yield_str}"
        )
    except Exception as e:
        return f"เกิดข้อผิดพลาดในการดึงข้อมูลทางการเงิน: {e}"

def get_recent_news(ticker: str) -> str:
    """ดึงข่าวสารล่าสุดของบริษัท"""
    try:
        stock = get_cached_ticker(ticker)
        news = stock.news
        
        if not news:
            return f"ไม่มีข่าวล่าสุดของ {ticker}"
            
        news_summary = []
        for n in news[:3]:
            title = n.get('title', 'ไม่มีหัวข้อข่าว')
            publisher = n.get('publisher', 'ไม่ระบุสำนักข่าว')
            news_summary.append(f"- {title} ({publisher})")
            
        return f"ข่าวล่าสุดของ {ticker}:\n" + "\n".join(news_summary)
    except Exception as e:
        return f"เกิดข้อผิดพลาดในการดึงข่าวสาร: {e}"

def _format_financial_df(df: pd.DataFrame, metrics: list[str], ticker: str, statement_name: str) -> str:
    """[ฟังก์ชันตัวช่วย (Helper)] เพื่อลดโค้ดซ้ำซ้อนในการจัดการ DataFrame"""
    if df is None or df.empty:
        return f"ไม่มีข้อมูล{statement_name}ของ {ticker}"
        
    available_metrics = [m for m in metrics if m in df.index]
    if not available_metrics:
        return f"ไม่มีข้อมูล{statement_name}ของ {ticker}"
        
    recent_years = df.loc[available_metrics].iloc[:, :3]
    
    recent_years = (recent_years / 1_000_000).round(2)
    
    return f"{statement_name} 3 ปีล่าสุดของ {ticker} (หน่วย: ล้าน):\n{recent_years.to_markdown()}"

def get_income_trend(ticker: str) -> str:
    """ดึงข้อมูลแนวโน้มรายได้และกำไรย้อนหลัง 3-4 ปี"""
    try:
        stock = get_cached_ticker(ticker)
        metrics = ['Total Revenue', 'Gross Profit', 'Operating Income', 'Net Income']
        return _format_financial_df(stock.financials, metrics, ticker, "งบกำไรขาดทุน")
    except Exception as e:
        return f"เกิดข้อผิดพลาดในการดึงงบกำไรขาดทุน: {e}"

def get_balance_sheet_health(ticker: str) -> str:
    """ดึงข้อมูลสินทรัพย์ หนี้สิน และทุน (งบดุล) ปีล่าสุด"""
    try:
        stock = get_cached_ticker(ticker)
        
        metrics = ['Total Assets', 'Total Liabilities Net Minority Interest', 'Total Liabilities', 'Total Debt', 'Cash And Cash Equivalents']
        return _format_financial_df(stock.balance_sheet, metrics, ticker, "งบดุล")
    except Exception as e:
         return f"เกิดข้อผิดพลาดในการดึงงบดุล: {e}"

def get_cash_flow_analysis(ticker: str) -> str:
    """ดึงข้อมูลงบกระแสเงินสด 3 ปีล่าสุด"""
    try:
        stock = get_cached_ticker(ticker)
        metrics = ['Operating Cash Flow', 'Free Cash Flow', 'Capital Expenditure']
        return _format_financial_df(stock.cashflow, metrics, ticker, "งบกระแสเงินสด")
    except Exception as e:
         return f"เกิดข้อผิดพลาดในการดึงงบกระแสเงินสด: {e}"