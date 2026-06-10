"""Finance MCP Server 📈 — เครื่องมือวิเคราะห์หุ้นที่ "ใครก็มาต่อใช้ได้"
"""

import yfinance as yf
import pandas as pd
import numpy as np
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("finance-server")

@mcp.tool()
def get_stock_valuation(ticker: str) -> str:
    """ดึงข้อมูลมูลค่าหุ้นและอัตราส่วนทางการเงินที่สำคัญ (Valuation & Ratios)
    
    Args:
        ticker (str): สัญลักษณ์หุ้น เช่น 'AAPL' หรือถ้าเป็นหุ้นไทยให้เติม '.BK' ต่อท้าย เช่น 'PTT.BK'
    """
    try:
        info = yf.Ticker(ticker).info
        pe = info.get('trailingPE', 'N/A')
        pb = info.get('priceToBook', 'N/A')
        roe = info.get('returnOnEquity', 'N/A')
        div_yield = info.get('dividendYield', 'N/A')
        
        # Advanced Valuation
        ev_ebitda = info.get('enterpriseToEbitda', 'N/A')
        ps = info.get('priceToSalesTrailing12Months', 'N/A')
        peg = info.get('pegRatio', 'N/A')
        
        roe_str = f"{roe * 100:.2f}%" if isinstance(roe, (int, float)) else "N/A"
        div_str = f"{div_yield * 100:.2f}%" if isinstance(div_yield, (int, float)) else "N/A"
        
        return (
            f"📊 ข้อมูล Valuation ขั้นสูง ของ {ticker}:\n"
            f"- P/E Ratio: {pe}\n"
            f"- P/B Ratio: {pb}\n"
            f"- EV/EBITDA: {ev_ebitda}\n"
            f"- Price-to-Sales (P/S): {ps}\n"
            f"- PEG Ratio: {peg}\n"
            f"- ROE: {roe_str}\n"
            f"- Dividend Yield: {div_str}\n"
            f"- ธุรกิจ: {info.get('industry', 'N/A')}"
        )
    except Exception as e:
        return f"ดึงข้อมูลอัตราส่วนไม่ได้: {e}"

@mcp.tool()
def get_3_statement_summary(ticker: str) -> str:
    """ดึงสรุปงบการเงิน 3 ด้าน ย้อนหลัง 3 ปี พร้อมอัตราส่วนสภาพคล่องและกำไร
    
    Args:
        ticker (str): สัญลักษณ์หุ้น เช่น 'AAPL' หรือถ้าเป็นหุ้นไทยให้เติม '.BK' ต่อท้าย เช่น 'PTT.BK'
    """
    try:
        stock = yf.Ticker(ticker)
        
        def _get_clean_df(df, metrics):
            if df is None or df.empty:
                return "ไม่มีข้อมูล"
            avail = [m for m in metrics if m in df.index]
            if not avail: return "ไม่มีข้อมูล"
            return (df.loc[avail].iloc[:, :3] / 1_000_000).round(2).to_string()

        # 1. งบกำไรขาดทุน & Margins
        inc_metrics = ['Total Revenue', 'Gross Profit', 'Operating Income', 'Net Income']
        inc_str = _get_clean_df(stock.financials, inc_metrics)
        
        # 2. งบดุล & Liquidity
        bal_metrics = ['Total Assets', 'Total Liabilities Net Minority Interest', 'Total Debt', 'Cash And Cash Equivalents', 'Current Assets', 'Current Liabilities']
        bal_str = _get_clean_df(stock.balance_sheet, bal_metrics)
        
        # 3. กระแสเงินสด
        cf_metrics = ['Operating Cash Flow', 'Capital Expenditure', 'Free Cash Flow']
        cf_str = _get_clean_df(stock.cashflow, cf_metrics)

        return (
            f"📈 สรุปงบการเงิน 3 ปีล่าสุดของ {ticker} (หน่วย: ล้านอ้างอิงตามสกุลเงินหลัก):\n\n"
            f"[งบกำไรขาดทุน]\n{inc_str}\n\n"
            f"[งบดุล]\n{bal_str}\n\n"
            f"[งบกระแสเงินสด]\n{cf_str}"
        )
    except Exception as e:
        return f"เกิดข้อผิดพลาดในการดึงงบการเงิน: {e}"

@mcp.tool()
def get_stock_news(ticker: str) -> str:
    """ดึงข่าวล่าสุดเพื่อหา Catalyst
    
    Args:
        ticker (str): สัญลักษณ์หุ้น เช่น 'AAPL' หรือถ้าเป็นหุ้นไทยให้เติม '.BK' ต่อท้าย เช่น 'PTT.BK'
    """
    try:
        news = yf.Ticker(ticker).news
        if not news: 
            return f"ไม่มีข่าวล่าสุดของ {ticker}"
        news_list = [f"- {n.get('title', 'ไม่มีหัวข้อ')} ({n.get('publisher', 'ไม่ระบุ')})" for n in news[:5]]
        return f"📰 ข่าวและ Catalyst ล่าสุดของ {ticker}:\n" + "\n".join(news_list)
    except Exception as e:
        return f"ดึงข่าวไม่ได้: {e}"

@mcp.tool()
def get_price_momentum(ticker: str) -> str:
    """ดึงข้อมูล Technical Analysis ขั้นสูง (MA20/50/200, RSI, Volume) เพื่อหาจุดเข้าซื้อ
    
    Args:
        ticker (str): สัญลักษณ์หุ้น เช่น 'AAPL' หรือถ้าเป็นหุ้นไทยให้เติม '.BK' ต่อท้าย เช่น 'PTT.BK'
    """
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1y")
        if hist is None or hist.empty or 'Close' not in hist.columns:
            return f"ไม่มีข้อมูลราคาย้อนหลังของ {ticker}"
            
        current_price = hist['Close'].iloc[-1]
        high_52w = hist['High'].max()
        low_52w = hist['Low'].min()
        
        # Moving Averages
        ma20 = hist['Close'].tail(20).mean() if len(hist) >= 20 else current_price
        ma50 = hist['Close'].tail(50).mean() if len(hist) >= 50 else current_price
        ma200 = hist['Close'].tail(200).mean() if len(hist) >= 200 else current_price
        
        # Volume Analysis
        current_volume = hist['Volume'].iloc[-1]
        avg_volume_20 = hist['Volume'].tail(20).mean() if len(hist) >= 20 else current_volume
        volume_surge = "พุ่งสูง" if current_volume > avg_volume_20 * 1.5 else "ปกติ"
        
        # RSI 14-day calculation
        if len(hist) > 14:
            delta = hist['Close'].diff()
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)
            avg_gain = gain.ewm(com=13, adjust=False).mean()
            avg_loss = loss.ewm(com=13, adjust=False).mean()
            rs = avg_gain / avg_loss
            rsi = (100 - (100 / (1 + rs))).iloc[-1]
            if rsi > 70: rsi_status = f"{rsi:.1f} (Overbought - แรงซื้อมากไป)"
            elif rsi < 30: rsi_status = f"{rsi:.1f} (Oversold - น่าสะสม)"
            else: rsi_status = f"{rsi:.1f} (Neutral - กลางๆ)"
        else:
            rsi_status = "N/A"
            
        # Trend Analysis
        if current_price > ma50 and ma50 > ma200:
            trend = "ขาขึ้นแข็งแกร่ง (Strong Uptrend)"
        elif current_price < ma50 and ma50 < ma200:
            trend = "ขาลงชัดเจน (Strong Downtrend)"
        elif current_price > ma200:
            trend = "ฟื้นตัวหรือพักตัวในขาขึ้น (Recovery / Pullback)"
        else:
            trend = "ไซด์เวย์ หรือเตรียมเปลี่ยนเทรนด์ (Sideways / Transition)"
        
        return (
            f"📈 ข้อมูล Technical Analysis ของ {ticker}:\n"
            f"- ราคาปัจจุบัน: {current_price:.2f}\n"
            f"=== แนวโน้มและเส้นค่าเฉลี่ย ===\n"
            f"- เทรนด์หลัก: {trend}\n"
            f"- MA20 (ระยะสั้น): {ma20:.2f}\n"
            f"- MA50 (ระยะกลาง): {ma50:.2f}\n"
            f"- MA200 (ระยะยาว): {ma200:.2f}\n"
            f"=== โมเมนตัมและวอลุ่ม ===\n"
            f"- RSI (14): {rsi_status}\n"
            f"- ปริมาณซื้อขายล่าสุด: {current_volume:,.0f} (เทียบกับเฉลี่ย 20 วัน: {avg_volume_20:,.0f} -> {volume_surge})\n"
            f"=== กรอบราคา 1 ปี ===\n"
            f"- 52-Week High: {high_52w:.2f}\n"
            f"- 52-Week Low: {low_52w:.2f}"
        )
    except Exception as e:
        return f"ดึงข้อมูลราคาไม่ได้: {e}"

@mcp.tool()
def get_analyst_estimates(ticker: str) -> str:
    """ดึงข้อมูลคาดการณ์จากนักวิเคราะห์ (Forward Estimates & Target Price) เพื่อดูมุมมองในอนาคต
    
    Args:
        ticker (str): สัญลักษณ์หุ้น เช่น 'AAPL' หรือถ้าเป็นหุ้นไทยให้เติม '.BK' ต่อท้าย เช่น 'PTT.BK'
    """
    try:
        info = yf.Ticker(ticker).info
        forward_pe = info.get('forwardPE', 'N/A')
        target_price = info.get('targetMeanPrice', 'N/A')
        recommendation = info.get('recommendationKey', 'N/A')
        num_analysts = info.get('numberOfAnalystOpinions', 'N/A')
        
        return (
            f"🔮 ข้อมูลคาดการณ์ในอนาคตจากนักวิเคราะห์ (Consensus Estimates) ของ {ticker}:\n"
            f"- Forward P/E (เทียบกำไรปีหน้า): {forward_pe}\n"
            f"- ราคาเป้าหมายเฉลี่ย (Mean Target Price): {target_price}\n"
            f"- คำแนะนำจากนักวิเคราะห์ (Recommendation): {recommendation.upper() if isinstance(recommendation, str) else recommendation} (จาก {num_analysts} นักวิเคราะห์)\n"
            f"*หมายเหตุ: ตลาดมองข้ามอดีตและให้มูลค่ากับอนาคต โปรดใช้ Forward P/E เทียบกับ Trailing P/E เพื่อดูการเติบโต*"
        )
    except Exception as e:
        return f"ดึงข้อมูลคาดการณ์ไม่ได้ (อาจไม่มีข้อมูลสำหรับหุ้นตัวนี้): {e}"

if __name__ == "__main__":
    mcp.run()
