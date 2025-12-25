import asyncio
import re
import time
from pathlib import Path
import httpx
from .utils import log_info, log_error, log_warn

class StructureCleaner:
    def __init__(self, config_manager):
        self.config = config_manager

    def _get_config(self):
        return {
            "enabled": self.config.get("struct_clean_enabled", False),
            "api_base": self.config.get("struct_clean_api_base", "https://api.openai.com/v1"),
            "api_key": self.config.get("struct_clean_api_key", ""),
            "model": self.config.get("struct_clean_model", "gpt-3.5-turbo"),
        }

    def _strip_markdown(self, content: str) -> str:
        """
        Normalize text content by removing Markdown markers and collapsing whitespace.
        This allows verifying that the textual content remains unchanged while ignoring formatting changes.
        """
        text = content
        
        # 1. Expand links/images to preserve both alt text and URL in the comparison
        # ![alt](url) -> alt url
        # [text](url) -> text url
        # We assume the LLM should not change the URL or the alt text.
        text = re.sub(r'!\[(.*?)\]\((.*?)\)', r'\1 \2', text)
        text = re.sub(r'\[(.*?)\]\((.*?)\)', r'\1 \2', text)
        
        # 2. Remove Headers markers (e.g. "## ")
        # Allow optional space to handle cases where LLM fixes "#Title" to "# Title"
        text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)
        
        # 3. Remove Bold/Italic/Strike markers (*, _, ~)
        text = re.sub(r'(\*\*|__|\*|_|~~)', '', text)
        
        # 4. Remove Code fences and backticks
        text = re.sub(r'```\w*', '', text)
        text = re.sub(r'`', '', text)
        
        # 5. Remove Blockquotes markers
        text = re.sub(r'^>\s*', '', text, flags=re.MULTILINE)
        
        # 6. Remove List markers (-, *, +, 1.)
        # Allow optional space to handle cases where LLM fixes "-Item" to "- Item"
        text = re.sub(r'^\s*[-*+]\s*', '', text, flags=re.MULTILINE)
        text = re.sub(r'^\s*\d+\.\s*', '', text, flags=re.MULTILINE)
        
        # 7. Remove Table delimiters (| and -)
        # Note: We just remove | characters. We also remove lines that are just dashes/pipes (table separators)
        text = re.sub(r'^[|\-\s:]+$', '', text, flags=re.MULTILINE) # Remove separator lines
        text = text.replace('|', ' ')
        
        # 8. Collapse whitespace (newlines, tabs, spaces -> single space)
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text

    async def _call_llm(self, content: str, cfg: dict) -> str:
        async with httpx.AsyncClient(timeout=120.0) as client:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {cfg['api_key']}",
            }
            
            system_prompt = (
                "You are a Markdown formatting expert.\n"
                "Task: Reformat the provided Markdown content to strictly follow best practices (CommonMark/GFM).\n"
                "Rules:\n"
                "1. Fix heading levels (ensure hierarchy is logical).\n"
                "2. Fix list indentation and markers.\n"
                "3. Fix table formatting.\n"
                "4. Ensure code blocks are properly fenced.\n"
                "5. CRITICAL: DO NOT CHANGE, ADD, OR REMOVE ANY TEXT CONTENT. DO NOT CHANGE PUNCTUATION.\n"
                "6. CRITICAL: Preserve all original text including language-specific punctuation (e.g. Chinese full-width punctuation).\n"
                "7. CRITICAL: KEEP ALL IMAGES AND LINKS EXACTLY AS IS.\n"
                "8. Output ONLY the cleaned Markdown content, no explanations."
            )

            payload = {
                "model": cfg["model"],
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": content}
                ],
                "temperature": 0.1, # Low temperature for determinism
            }
            
            # Construct URL
            base_url = cfg["api_base"].rstrip("/")
            if not base_url.endswith("/v1"):
                # Basic heuristic for common endpoints
                pass 
                
            url = f"{base_url}/chat/completions"
            
            try:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
            except Exception as e:
                log_error(f"LLM Call failed: {e}")
                return None

    async def _clean_markdown_async(self, md_path: Path) -> bool:
        cfg = self._get_config()
        if not cfg["enabled"] or not cfg["api_key"]:
            return False

        log_info(f"Starting Structure Cleaning for {md_path.name}...")
        
        try:
            original_content = md_path.read_text(encoding="utf-8")
        except Exception as e:
            log_error(f"Failed to read file {md_path}: {e}")
            return False

        start_time = time.perf_counter()
        cleaned_content = await self._call_llm(original_content, cfg)
        
        if not cleaned_content:
            log_warn(f"Structure Cleaning skipped: LLM returned no content.")
            return False

        # Verification
        original_norm = self._strip_markdown(original_content)
        cleaned_norm = self._strip_markdown(cleaned_content)
        
        if original_norm == cleaned_norm:
            elapsed = time.perf_counter() - start_time
            # Backup original
            # md_path.rename(md_path.with_suffix(".md.bak")) # Optional: backup
            md_path.write_text(cleaned_content, encoding="utf-8")
            log_info(f"Structure Cleaning successful for {md_path.name} in {elapsed:.2f}s.")
            return True
        else:
            log_warn(f"Structure Cleaning REJECTED for {md_path.name}: Content integrity check failed.")
            
            # Debug: Dump normalized content for investigation
            try:
                debug_dir = md_path.parent / "debug_cleaning"
                debug_dir.mkdir(exist_ok=True)
                (debug_dir / f"{md_path.name}.orig_norm.txt").write_text(original_norm, encoding="utf-8")
                (debug_dir / f"{md_path.name}.clean_norm.txt").write_text(cleaned_norm, encoding="utf-8")
                (debug_dir / f"{md_path.name}.cleaned.md").write_text(cleaned_content, encoding="utf-8")
                log_warn(f"Debug files dumped to {debug_dir}")
            except Exception as e:
                log_warn(f"Failed to dump debug files: {e}")
                
            return False

    def clean_markdown(self, md_path: Path):
        """Synchronous wrapper for async execution"""
        try:
            return asyncio.run(self._clean_markdown_async(md_path))
        except Exception as e:
            log_error(f"Structure Cleaning failed with exception: {e}")
            return False
