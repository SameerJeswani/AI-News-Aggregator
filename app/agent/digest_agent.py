import os
import json
from typing import Optional
from groq import Groq
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()


class DigestOutput(BaseModel):
    title: str
    summary: str


PROMPT = """You are an expert AI news analyst specializing in summarizing technical articles, research papers, and video content about artificial intelligence.

Return ONLY valid JSON in this format:
{
  "title": "Short title",
  "summary": "2-3 sentence summary"
}

Guidelines:
- Create a compelling title (5-10 words)
- Write a 2-3 sentence summary
- Focus on actionable insights
- Avoid marketing fluff
"""


class DigestAgent:
    def __init__(self):
        self.client = Groq(
            api_key=os.getenv("GROQ_API_KEY")
        )
        self.model = "llama-3.3-70b-versatile"

    def generate_digest(
        self,
        title: str,
        content: str,
        article_type: str
    ) -> Optional[DigestOutput]:

        try:
            user_prompt = f"""
Create a digest for this {article_type}

Title:
{title}

Content:
{content[:8000]}
"""

            response = self.client.chat.completions.create(
                model=self.model,
                temperature=0.7,
                messages=[
                    {
                        "role": "system",
                        "content": PROMPT
                    },
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ],
                response_format={"type": "json_object"}
            )

            result = json.loads(
                response.choices[0].message.content
            )

            return DigestOutput(
                title=result["title"],
                summary=result["summary"]
            )

        except Exception as e:
            print(f"Error generating digest: {e}")
            return None