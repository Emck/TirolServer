import re
from concurrent.futures import ProcessPoolExecutor, as_completed

from selectolax.parser import HTMLParser

from tirolserver.core.clean import ReadabilityCleaner, SimpleRemoveCleaner, TrafilaturaCleaner, UnstructuredCleaner


class HtmlToMarkdown:
	def toMarkdown(self, html: str, title: str = "", url: str = "") -> tuple[str, dict]:
		"""Convert HTML to Markdown string
		:param html: original HTML content
		:param title: title of the document, defaults to ""
		:param url: html url, defaults to ""
		:return: Markdown string and result dict
		"""

		# if title is empty, get title from html
		mtitle = title if title else self._get_title(html)

		results = []
		# Parallel execution all engines, using the process pool
		engines = {
			"trafilatura": self._worker_Trafilatura,
			"readability": self._worker_Readability,
			"unstructured": self._worker_Unstructured,
			"simple_remove": self._worker_SimpleRemove,  # Fallback
		}
		with ProcessPoolExecutor(max_workers=len(engines)) as executor:
			future_to_engine = {executor.submit(func, html, mtitle): name for name, func in engines.items()}
			for future in as_completed(future_to_engine):
				try:
					name, content = future.result(timeout=10)
					results.append({"name": name, "content": content, "len": len(content)})
				except Exception:
					results.append({"name": future_to_engine[future], "content": "", "len": 0})

		# sort by len in ascending order
		results.sort(key=lambda x: x.get("len", 0))

		# calculate quality (ratio of valid content)
		min_ratio = results[0]["len"] / len(html)  # shortest content proportion
		max_ratio = results[-1]["len"] / len(html)  # longest content proportion
		result: dict = {"url": url, "title": mtitle, "html_len": len(html)}
		qualitys: list = []
		if min_ratio <= 0.01:  # min ratio is less than 0.01%
			if max_ratio < 0.1:  # max ratio is less than 0.1%
				qualitys.extend([results[-1], results[-2]])
			else:  # max ratio is greater than 0.1%
				qualitys.extend([results[-2], results[-3]])
		else:
			if max_ratio < 0.05:  # max ratio is less than 0.05%
				qualitys.extend([results[-1], results[-2]])
			else:  # max ratio is greater than 0.05%
				qualitys.extend([results[-2], results[-3]])

		result["min_ratio"] = f"{min_ratio:.4f}"  # save min ratio
		result["max_ratio"] = f"{max_ratio:.4f}"  # save max ratio
		result["engines"] = results  # save all engines
		result["quality"] = qualitys  # save quality engines

		# calculate quality score
		for quality in qualitys:
			quality["score"] = self._quality_score(html, quality["content"])  # score

		# set the star mark
		if abs(qualitys[0]["score"] - qualitys[1]["score"]) < 10:  # score difference is less than 10
			result["star"] = 1  # choose the shorter content
		else:  # highest score
			if qualitys[0]["score"] >= qualitys[1]["score"]:
				result["star"] = 0
			else:
				result["star"] = 1

		result["content"] = result["quality"][result["star"]]["content"]  # save the content of the star mark
		return result["content"], result  # return content and result dict

	def _quality_score(self, html: str, content: str):
		"""Calculate quality score of the content
		:param html: original HTML content
		:param content: markdown content
		:return: int quality score
		"""

		if not content:
			return 0
		score = 0
		length = len(content)
		htmllen = len(html)

		# 1. punctuation density (ideal range 0.03 - 0.08)
		punc_count = len(re.findall(r"[，。！？,.!?]", content))
		punc_ratio = punc_count / length
		if 0.03 <= punc_ratio <= 0.08:
			score += 40
		elif 0.01 <= punc_ratio <= 0.12:
			score += 20

		# 2. link density
		links = re.findall(r"\[.*?\]\(.*?\)", content)
		link_text_len = sum(len(l) for l in links)  # noqa: E741
		link_ratio = link_text_len / length
		if link_ratio < 0.1:
			score += 20
		elif link_ratio < 0.25:
			score += 10
		else:
			score -= 20  # link too many, maybe list or footer

		# 3. paragraph sense
		if content.count("\n\n") > length / 200:
			score += 20

		# 4. content ratio
		content_ratio = length / htmllen
		if content_ratio > 0.20:
			score -= 10
		elif content_ratio > 0.10:
			score += 40
		elif content_ratio > 0.05:
			score += 20
		else:
			score -= 30

		return score

	def printresult(self, result: list):
		"""Print result dict in a formatted way
		:param result: result dict
		"""
		for key, value in result.items():
			if key == "engines":
				print("engines: --- [sort by length in ascending order]")
				for item in value:
					print(f"  name: '{item['name']:15}', 'len': {item['len']:6d}")
			elif key == "quality":
				print("quality: --- [sort by quality in descending order (ignore score)]")
				for item in value:
					print(f"  name: '{item['name']:15}', 'len': {item['len']:6d}, 'score': {item['score']:3d}")
			elif key == "star":
				print(f"star: {value}  --- [index in quality]")
			elif key == "content":
				print(f'content: {len(value)}, "{value[:40]}..."')
			else:
				print(f"{key}: {value}")  # print other key

	def _get_title(self, html: str) -> str:
		"""Get title from html.
		:param html: html string
		:return: title string
		"""
		tree = HTMLParser(html)
		title = tree.css_first("title")
		return title.text().strip() if title else ""

	# define the cleaner wrapper
	def _worker_Trafilatura(self, html, title: str = ""):
		return TrafilaturaCleaner().run(html, title)

	def _worker_Readability(self, html, title: str = ""):
		return ReadabilityCleaner().run(html, title)

	def _worker_Unstructured(self, html, title: str = ""):
		return UnstructuredCleaner().run(html, title)

	def _worker_SimpleRemove(self, html, title: str = ""):
		return SimpleRemoveCleaner().run(html, title)
