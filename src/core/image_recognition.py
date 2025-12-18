import asyncio
import base64
import re
import os
import time
from pathlib import Path
import httpx
from urllib.parse import unquote
from .utils import log_info, log_error, log_warn


class ImageRecognizer:
    def __init__(self, config_manager):
        self.config = config_manager

    def _get_config(self):
        return {
            "enabled": self.config.get("img_rec_enabled", False),
            "api_base": self.config.get(
                "img_rec_api_base", "https://api.openai.com/v1"
            ),
            "api_key": self.config.get("img_rec_api_key", ""),
            "model": self.config.get("img_rec_model", "gpt-4-vision-preview"),
            "concurrency": int(self.config.get("img_rec_concurrency", 2)),
        }

    async def _encode_image(self, image_path: Path) -> str:
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode("utf-8")
        except Exception as e:
            log_error(f"Failed to encode image {image_path}: {e}")
            return None

    async def _process_single_image(
        self,
        image_path: Path,
        client: httpx.AsyncClient,
        semaphore: asyncio.Semaphore,
        index: int,
        total: int,
    ) -> str:
        cfg = self._get_config()
        if not image_path.exists():
            log_warn(f"[{index}/{total}] Image not found: {image_path}")
            return ""

        async with semaphore:
            log_info(f"[{index}/{total}] Processing image: {image_path.name}...")
            start_time = time.perf_counter()
            try:
                base64_image = await self._encode_image(image_path)
                if not base64_image:
                    return ""

                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {cfg['api_key']}",
                }

                payload = {
                    "model": cfg["model"],
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": """Please analyze this image and provide a structured description in the following format:
- **Visual Type**: [e.g., Chart, Diagram, Screenshot, Photo, Table]
- **Title**: [Title of the chart or image if available]
- **Data Points**: [Key data values, text content, or specific numbers visible]
- **Trends / Insights**: [Analysis of what the image shows, trends, or the main message]

If a field is not applicable, mark it as N/A. Ensure the description is detailed and captures all text and visual elements. Please provide the content in the same language as the text in the image (default to Chinese if uncertain).""",
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{base64_image}"
                                    },
                                },
                            ],
                        }
                    ],
                    "max_tokens": 1000,
                }

                # Construct URL (handle trailing slash)
                base_url = cfg["api_base"].rstrip("/")
                if not base_url.endswith("/v1"):
                    # Some users might put base url without /v1, but standard is /v1/chat/completions
                    # If user put https://api.openai.com, we append /v1/chat/completions
                    # If user put https://api.openai.com/v1, we append /chat/completions
                    # Let's assume user provides base url compatible with OpenAI client usually ending in /v1
                    pass

                url = f"{base_url}/chat/completions"

                response = await client.post(
                    url, headers=headers, json=payload, timeout=60.0
                )
                response.raise_for_status()

                data = response.json()
                content = data["choices"][0]["message"]["content"]

                elapsed = time.perf_counter() - start_time
                log_info(
                    f"[{index}/{total}] Successfully processed {image_path.name} in {elapsed:.2f}s."
                )
                return content

            except httpx.HTTPStatusError as e:
                log_error(
                    f"[{index}/{total}] API Error for {image_path.name}: Status {e.response.status_code}, Response: {e.response.text}"
                )
                return ""
            except Exception as e:
                log_error(
                    f"[{index}/{total}] Failed to recognize image {image_path.name}: {e}"
                )
                return ""

    async def _process_markdown_async(self, md_path: Path):
        cfg = self._get_config()
        if not cfg["enabled"] or not cfg["api_key"]:
            log_info("Image recognition disabled or API key missing.")
            return

        try:
            content = md_path.read_text(encoding="utf-8")
        except Exception as e:
            log_error(f"Failed to read markdown file {md_path}: {e}")
            return

        # Find all images: ![alt](path)
        # Non-greedy match for alt and path
        pattern = re.compile(r"!\[(.*?)\]\((.*?)\)")
        matches = list(pattern.finditer(content))

        if not matches:
            return

        log_info(
            f"Found {len(matches)} images in {md_path.name}. Starting recognition..."
        )

        semaphore = asyncio.Semaphore(cfg["concurrency"])
        async with httpx.AsyncClient() as client:
            tasks = []
            replacements = {}  # start_index -> (end_index, replacement_text)

            total_images = len(matches)
            for index, match in enumerate(matches, 1):
                alt_text = match.group(1)
                img_rel_path = match.group(2)
                
                # Decode URL-encoded path characters (e.g., %E5%AE%87 -> 宇)
                img_rel_path = unquote(img_rel_path)
                
                # Resolve image path
                # Image path in MD is relative to MD file location
                img_full_path = (md_path.parent / img_rel_path).resolve()

                tasks.append(
                    self._process_single_image(
                        img_full_path, client, semaphore, index, total_images
                    )
                )

            results = await asyncio.gather(*tasks)

            # Construct replacements
            # We process from last to first to avoid index shifting, or rebuild string
            # Rebuilding string is safer

            new_content = ""
            last_idx = 0

            for match, description in zip(matches, results):
                start, end = match.span()
                new_content += content[last_idx:end]  # Include the original image tag

                if description:
                    # Append description
                    # Format:
                    # ![alt](path)
                    # > **图解**:
                    # > Line 1
                    # > Line 2

                    # Prefix every line with "> " to keep it in the blockquote
                    formatted_desc = f"\n\n> **图解**:\n"
                    for line in description.split("\n"):
                        formatted_desc += f"> {line}\n"
                    formatted_desc += "\n"
                    new_content += formatted_desc

                last_idx = end

            new_content += content[last_idx:]

            md_path.write_text(new_content, encoding="utf-8")
            log_info(f"Updated {md_path.name} with image descriptions.")

    def process_markdown(self, md_path: Path):
        """Sync wrapper for async processing"""
        try:
            asyncio.run(self._process_markdown_async(md_path))
        except Exception as e:
            log_error(f"Error in image recognition process: {e}")
