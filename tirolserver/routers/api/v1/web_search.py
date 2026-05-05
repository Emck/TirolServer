"""web_fetch router"""

from dataclasses import dataclass

from fastapi import HTTPException, Request

from tirolserver.utils import logger


@dataclass
class WebSearchRequest:
	"""web search request parameters
	:param keys: The target URL to retrieve data from.
	:param timeout: The maximum time in seconds to wait for a response.
	"""

	keys: str = ""
	timeout: int = 30
	# clean: bool = True


@dataclass
class WebSearchResponse:
	"""web search response parameters
	:param content: xxx
	"""

	content: str | None = None


async def web_search(request: WebSearchRequest, raw: Request) -> WebSearchResponse:
	"""web search interface, return search content.
	:param request: request parameters (xxx, timeout, ...)
	:param raw: original request
	:return: response data
	"""
	try:
		return WebSearchResponse(content="Search Response")

	except HTTPException as e:
		raise e
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"unknow exception {str(type(e))} {str(e)}")


# async def scrape_and_clean(url: str = Query(..., description="要清洗的第三方网页 URL"), timeout: int = Query(10, description="请求第三方网页的超时时间")):
# 	import time

# 	start_time = time.time()

# 	# 第一步：异步转发请求，获取 HTML
# 	async with httpx.AsyncClient(follow_redirects=True) as client:
# 		try:
# 			headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
# 			response = await client.get(url, headers=headers, timeout=timeout)
# 			response.raise_for_status()  # 如果 4xx 或 5xx 则抛出异常
# 			html_content = response.text
# 		except httpx.HTTPStatusError as e:
# 			raise HTTPException(status_code=e.response.status_code, detail=f"第三方页面访问失败: {e}")
# 		except Exception as e:
# 			raise HTTPException(status_code=500, detail=f"请求转发错误: {str(e)}")

# 	# 第二步：执行并行清洗逻辑
# 	# 注意：decider.run 内部使用了 ProcessPoolExecutor，它是同步阻塞调用，
# 	# 在 FastAPI 异步函数中建议放在 run_in_executor 中运行，防止阻塞主线程。
# 	import asyncio
# 	from concurrent.futures import ThreadPoolExecutor

# 	loop = asyncio.get_event_loop()
# 	# 使用 run_in_executor 运行 CPU 密集型的清洗任务
# 	try:
# 		# 假设 decider.run 是您整合好的并行入口
# 		result = await loop.run_in_executor(None, decider.run, html_content)
# 	except Exception as e:
# 		raise HTTPException(status_code=500, detail=f"清洗任务执行失败: {str(e)}")

# 	elapsed = time.time() - start_time

# 	# 第三步：返回结果
# 	return CleanResponse(url=url, engine=result["engine"], score=result["score"], content=result["content"], execution_time=round(elapsed, 2))


# @app.get("/proxy-stream")  # 流式转发
# async def proxy_stream():
# 	client = httpx.AsyncClient()

# 	# 使用 httpx 的流式响应
# 	req = client.build_request("GET", "https://thirdparty.com")
# 	res = await client.send(req, stream=True)

# 	return StreamingResponse(res.aiter_raw(), status_code=res.status_code, headers=dict(res.headers))
