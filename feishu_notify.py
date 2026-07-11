import os
import requests
from dotenv import load_dotenv

load_dotenv()

FEISHU_WEBHOOK_URL = os.getenv("FEISHU_WEBHOOK_URL")
PROXY_URL = os.getenv("PROXY_URL")

proxies = {"http": PROXY_URL, "https": PROXY_URL} if PROXY_URL else None


def send_feishu_message(title: str, content: str) -> bool:
    if not FEISHU_WEBHOOK_URL:
        print("飞书 Webhook 未配置")
        return False

    try:
        payload = {
            "msg_type": "text",
            "content": {
                "text": f"{title}\n\n{content}"
            }
        }
        resp = requests.post(FEISHU_WEBHOOK_URL, json=payload, proxies=proxies, timeout=10)
        resp.raise_for_status()
        print("飞书消息发送成功")
        return True
    except Exception as e:
        print(f"飞书消息发送失败: {e}")
        return False


def format_feishu_report(coin_type: str, price: float, direction: str, direction_desc: str,
                          confidence: float, range_data: dict, regime: str, regime_desc: str,
                          verification: dict = None) -> str:
    coin_name = "BTC" if coin_type == "btc" else "ETH"

    report = f"💰 **{coin_name} 价格预测报告**\n"
    report += f"-----------------------------------\n\n"
    report += f"📊 当前价格: **${price:,.2f}**\n\n"
    report += f"🎯 方向判断: **{direction_desc}**\n"
    report += f"   置信度: **{confidence * 100:.1f}%**\n\n"
    report += f"📏 波动区间: **${range_data['lower']:,.2f} ~ ${range_data['upper']:,.2f}**\n"
    report += f"   区间宽度: **{range_data['range_pct']:.2f}%** ({range_data['width']})\n\n"
    report += f"📈 市场状态: **{regime_desc}**\n\n"

    if verification and verification.get("verified"):
        report += f"✅ 上小时验证结果:\n"
        report += f"   {verification['message']}\n"

    report += f"-----------------------------------\n"
    report += f"💡 提示: BTC 在 1 小时周期上 82% 的时间是中性随机游走\n"
    report += f"         宁可少做、不错做 —— neutral 预测准确率 74%\n"

    return report