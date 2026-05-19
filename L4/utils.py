# Add your utilities or helper functions to this file.

import json
import os
from pathlib import Path

import requests
from crewai.tools import BaseTool
from dotenv import load_dotenv, find_dotenv
from pydantic import BaseModel, Field
# these expect to find a .env file at the directory above the lesson.                                                                                                                     # the format for that file is (without the comment)                                                                                                                                       #API_KEYNAME=AStringThatIsTheLongAPIKeyFromSomeService
# def load_env():
#     _ = load_dotenv(find_dotenv())

def load_env() -> None:
    """加载 .env：先读与 mini_claude 包同级的项目目录（含 pyproject 的 python/），再由 cwd 下 .env 覆盖。"""

    pkg_root = Path(__file__).resolve().parent
    pkg_env = pkg_root / ".env"
    cwd_env = Path.cwd() / ".env"

    if pkg_env.is_file():
        load_dotenv(pkg_env)
    if cwd_env.is_file():
        load_dotenv(cwd_env, override=True)

def get_openai_api_key():
    load_env()
    openai_api_key = os.getenv("OPENAI_API_KEY")
    return openai_api_key

def get_serper_api_key():
    load_env()
    openai_api_key = os.getenv("SERPER_API_KEY")
    return openai_api_key

def get_serper_base_url():
    load_env()
    serper_base_url = os.getenv("SERPER_BASE_URL")
    return serper_base_url


class BaiduWebSearchInput(BaseModel):
    search_query: str = Field(..., description="要搜索的关键词")


class BaiduWebSearchTool(BaseTool):
    """百度千帆 AI 搜索（与 SerperDevTool 协议不同，勿混用）。"""

    name: str = "Search the internet"
    description: str = (
        "在互联网上搜索信息。输入 search_query 作为搜索关键词。"
    )
    args_schema: type[BaseModel] = BaiduWebSearchInput

    def _run(self, search_query: str = "", **kwargs) -> str:
        query = search_query or kwargs.get("query", "")
        if not query:
            raise ValueError("search_query is required")

        load_env()
        api_key = os.getenv("SERPER_API_KEY") or os.getenv("BAIDU_API_KEY")
        if not api_key:
            raise ValueError("请在 .env 中设置 SERPER_API_KEY（百度千帆 API Key）")

        url = (os.getenv("SERPER_BASE_URL") or "https://qianfan.baidubce.com/v2/ai_search/web_search").strip('"')
        # SerperDevTool 会追加 /search；千帆接口不需要该后缀
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


# break line every 80 characters if line is longer than 80 characters
# don't break in the middle of a word
def pretty_print_result(result):
  parsed_result = []
  for line in result.split('\n'):
      if len(line) > 80:
          words = line.split(' ')
          new_line = ''
          for word in words:
              if len(new_line) + len(word) + 1 > 80:
                  parsed_result.append(new_line)
                  new_line = word
              else:
                  if new_line == '':
                      new_line = word
                  else:
                      new_line += ' ' + word
          parsed_result.append(new_line)
      else:
          parsed_result.append(line)
  return "\n".join(parsed_result)
