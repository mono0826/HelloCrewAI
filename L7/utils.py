# Add your utilities or helper functions to this file.

import json
import os
import re
from pathlib import Path

import requests
from crewai.tools import BaseTool
from dotenv import load_dotenv
from pydantic import BaseModel, Field

try:
    from bs4 import BeautifulSoup

    BEAUTIFULSOUP_AVAILABLE = True
except ImportError:
    BEAUTIFULSOUP_AVAILABLE = False


def load_env() -> None:
    """加载 .env：先读本课目录，再由 cwd 下 .env 覆盖。"""

    pkg_root = Path(__file__).resolve().parent
    pkg_env = pkg_root / ".env"
    cwd_env = Path.cwd() / ".env"

    if pkg_env.is_file():
        load_dotenv(pkg_env)
    if cwd_env.is_file():
        load_dotenv(cwd_env, override=True)


def get_openai_api_key():
    load_env()
    return os.getenv("OPENAI_API_KEY")


def get_serper_api_key():
    load_env()
    return os.getenv("SERPER_API_KEY")


class BaiduWebSearchInput(BaseModel):
    search_query: str = Field(..., description="要搜索的关键词")


class BaiduWebSearchTool(BaseTool):
    """百度千帆 AI 搜索（与 SerperDevTool 协议不同，勿混用）。"""

    name: str = "Search the internet"
    description: str = "在互联网上搜索信息。输入 search_query 作为搜索关键词。"
    args_schema: type[BaseModel] = BaiduWebSearchInput

    def _run(self, search_query: str = "", **kwargs) -> str:
        query = search_query or kwargs.get("query", "")
        if not query:
            raise ValueError("search_query is required")

        load_env()
        api_key = os.getenv("SERPER_API_KEY") or os.getenv("BAIDU_API_KEY")
        if not api_key:
            raise ValueError("请在 .env 中设置 SERPER_API_KEY（百度千帆 API Key）")

        url = (
            os.getenv("SERPER_BASE_URL")
            or "https://qianfan.baidubce.com/v2/ai_search/web_search"
        ).strip('"')
        if url.rstrip("/").endswith("/search"):
            url = url.rstrip("/")[:-len("/search")]

        response = requests.post(
            url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={"messages": [{"role": "user", "content": query}]},
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()

        if data.get("code"):
            raise RuntimeError(data.get("message", data))

        references = data.get("references", [])
        organic = [
            {
                "title": item.get("title", ""),
                "link": item.get("url", ""),
                "snippet": (item.get("content") or "")[:500],
            }
            for item in references[:10]
        ]
        return json.dumps({"organic": organic}, ensure_ascii=False)


class ScrapeWebsiteInput(BaseModel):
    website_url: str = Field(..., description="要抓取内容的网页 URL")


class ScrapeWebsiteTool(BaseTool):
    """抓取网页正文，接口与 crewai_tools.ScrapeWebsiteTool 兼容。"""

    name: str = "Read website content"
    description: str = "用于读取指定网页的正文内容。输入 website_url。"
    args_schema: type[BaseModel] = ScrapeWebsiteInput

    _DEFAULT_HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    }

    def _run(self, website_url: str = "", **kwargs) -> str:
        if not BEAUTIFULSOUP_AVAILABLE:
            raise ImportError(
                "未安装 beautifulsoup4，请执行: pip install beautifulsoup4"
            )

        url = website_url or kwargs.get("website_url", "")
        if not url:
            raise ValueError("website_url is required")
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        page = requests.get(
            url,
            timeout=30,
            headers=self._DEFAULT_HEADERS,
        )
        page.raise_for_status()
        page.encoding = page.apparent_encoding or page.encoding

        parsed = BeautifulSoup(page.text, "html.parser")
        for tag in parsed(["script", "style", "noscript"]):
            tag.decompose()

        text = "The following text is scraped website content:\n\n"
        text += parsed.get_text(" ")
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\s+\n\s+", "\n", text)
        return text[:15000]


def get_rag_embedding_config() -> dict:
    """RAG/MDXSearchTool 使用的 embedding 配置（适配 DashScope 等 OpenAI 兼容接口）。"""
    load_env()
    api_base = (
        os.getenv("EMBEDDINGS_OPENAI_API_BASE")
        or os.getenv("OPENAI_BASE_URL")
        or os.getenv("OPENAI_API_BASE")
    )
    return {
        "embedding_model": {
            "provider": "openai",
            "config": {
                "model_name": os.getenv(
                    "EMBEDDINGS_OPENAI_MODEL_NAME", "text-embedding-v3"
                ),
                "api_key": os.getenv("OPENAI_API_KEY"),
                "api_base": api_base,
            },
        },
    }


def create_resume_search_tool(mdx: str = "./fake_resume.md"):
    """创建简历语义搜索工具，使用 .env 中的 embedding 模型而非默认 text-embedding-3-small。"""
    from crewai_tools import MDXSearchTool
    import hashlib

    path_key = hashlib.md5(str(Path(mdx).resolve()).encode()).hexdigest()[:8]
    print(path_key)
    return MDXSearchTool(
        mdx=mdx,
        config=get_rag_embedding_config(),
        collection_name=f"resume_{path_key}",
    )


def pretty_print_result(result):
    parsed_result = []
    for line in result.split("\n"):
        if len(line) > 80:
            words = line.split(" ")
            new_line = ""
            for word in words:
                if len(new_line) + len(word) + 1 > 80:
                    parsed_result.append(new_line)
                    new_line = word
                else:
                    new_line = word if new_line == "" else new_line + " " + word
            parsed_result.append(new_line)
        else:
            parsed_result.append(line)
    return "\n".join(parsed_result)
