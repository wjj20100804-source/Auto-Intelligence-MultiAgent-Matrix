import schedule
import time
import feedparser
import logging
from typing import List, Optional
from openai import OpenAI
from datetime import datetime

# ================= 核心系统配置 =================
API_KEY = "sk-your-api-key-here"
BASE_URL = "https://api.deepseek.com/v1" 
MODEL_NAME = "deepseek-chat"

# 专业级日志配置
logging.basicConfig(
    level=logging.INFO, 
    format='[%(asctime)s] [%(name)s] [%(levelname)s] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("Intelligence-Agent-Matrix")

# ================= Agent 类的定义 =================
class BaseAgent:
    """Agent 基类，封装大模型调用能力"""
    def __init__(self, role_name: str, temperature: float = 0.5):
        self.role_name = role_name
        self.temperature = temperature
        self.client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

    def generate_response(self, prompt: str) -> Optional[str]:
        try:
            logger.info(f"{self.role_name} 开始执行逻辑推理...")
            response = self.client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"{self.role_name} 执行失败: {str(e)}")
            return None

class ScrapingAgent:
    """专注数据源获取与解析的Agent"""
    def __init__(self, feeds: List[str]):
        self.feeds = feeds
        self.logger = logging.getLogger("ScrapingAgent")

    def fetch_data(self) -> str:
        self.logger.info("启动全网多源数据并发抓取...")
        raw_articles = []
        for url in self.feeds:
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries[:20]:  # 扩大抓取样本量
                    raw_articles.append(f"【标题】: {entry.title}\n【内容】: {entry.get('summary', '无摘要')}\n")
            except Exception as e:
                self.logger.warning(f"抓取源 {url} 失败: {str(e)}")
                
        self.logger.info(f"数据抓取完毕，共捕获 {len(raw_articles)} 条有效原始数据。")
        return "\n---\n".join(raw_articles)

class IntelligenceOrchestrator:
    """多智能体中枢调度系统"""
    def __init__(self):
        self.rss_feeds = [
            "https://www.solidot.org/index.rss",
            "https://feed.cnblogs.com/blog/sitehome/rss"
        ]
        self.scraper = ScrapingAgent(self.rss_feeds)
        self.reasoning_agent = BaseAgent(role_name="[深度推理Agent]", temperature=0.3)
        self.writing_agent = BaseAgent(role_name="[全景撰稿Agent]", temperature=0.5)

    def run_daily_workflow(self):
        logger.info("="*60)
        logger.info("触发多智能体协作工作流...")

        # 阶段一：全网数据感知
        raw_data = self.scraper.fetch_data()
        if not raw_data:
            logger.error("未获取到基础数据，中断工作流。")
            return

        # 阶段二：清洗与长文本交叉推理
        reasoning_prompt = f"""
        作为资深情报分析中枢，请对以下非结构化文本进行清洗和长链关联推理：
        1. 识别并剔除重复冗余信息。
        2. 挖掘事件背后的深层技术趋势或商业逻辑关联。
        3. 输出严谨的推理路径和核心洞察（Chain of Thought）。
        
        原始数据集：
        {raw_data}
        """
        reasoning_result = self.reasoning_agent.generate_response(reasoning_prompt)
        if not reasoning_result: return

        # 阶段三：无限制深度成稿
        writing_prompt = f"""
        基于以下推理洞察，输出最终的《每日深度全景情报》。
        绝对核心要求：**不设任何字数上限，不限制解读的新闻条数**。彻底打破长度限制，提供详尽的背景、分析和推演。
        要求排版严谨，多级标题清晰。
        
        推理洞察结果：
        {reasoning_result}
        """
        final_report = self.writing_agent.generate_response(writing_prompt)
        
        # 阶段四：资产沉淀
        if final_report:
            filename = f"Deep_Intelligence_{datetime.now().strftime('%Y%m%d')}.md"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(final_report)
            logger.info(f"工作流完美闭环。最终报告已生成: {filename}")
        logger.info("="*60)

# ================= 守护进程启动 =================
if __name__ == "__main__":
    logger.info("系统初始化完成。核心组件已就绪。")
    orchestrator = IntelligenceOrchestrator()
    
    # 设定严格的自动化调度
    schedule.every().day.at("18:00").do(orchestrator.run_daily_workflow)
    logger.info("定时调度已激活：每日 18:00 自动执行全量搜集与长文本推理...")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(10)
    except KeyboardInterrupt:
        logger.info("接收到终止信号，系统安全退出。")