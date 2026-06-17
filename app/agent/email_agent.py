import os
import json
from datetime import datetime
from typing import List, Optional

from groq import Groq
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()


class EmailIntroduction(BaseModel):
    greeting: str
    introduction: str


class RankedArticleDetail(BaseModel):
    digest_id: str
    rank: int
    relevance_score: float
    title: str
    summary: str
    url: str
    article_type: str
    reasoning: Optional[str] = None


class EmailDigestResponse(BaseModel):
    introduction: EmailIntroduction
    articles: List[RankedArticleDetail]
    total_ranked: int
    top_n: int

    def to_markdown(self) -> str:
        markdown = f"{self.introduction.greeting}\n\n"
        markdown += f"{self.introduction.introduction}\n\n"
        markdown += "---\n\n"

        for article in self.articles:
            markdown += f"## {article.title}\n\n"
            markdown += f"{article.summary}\n\n"
            markdown += f"[Read more →]({article.url})\n\n"
            markdown += "---\n\n"

        return markdown


class EmailDigest(BaseModel):
    introduction: EmailIntroduction
    ranked_articles: List[dict]


EMAIL_PROMPT = """
You are an expert email writer.

Return ONLY valid JSON.

Format:

{
  "greeting": "Dear Sameer, June 16, 2026",
  "introduction": "Introduction text"
}

Rules:
- Address the user by their exact name.
- Never use generic greetings such as:
  "Dear Valued Colleagues"
  "Dear Partners"
  "To whom it may concern"
- Always start with "Dear <name>,"
- Mention the current date.
- Write a short 2-3 sentence introduction.
- Professional but friendly tone.

Return JSON only.
"""


class EmailAgent:
    def __init__(self, user_profile: dict):
        self.client = Groq(
            api_key=os.getenv("GROQ_API_KEY")
        )

        self.model = "llama-3.1-8b-instant"
        self.user_profile = user_profile

    def generate_introduction(
        self,
        ranked_articles: List
    ) -> EmailIntroduction:

        current_date = datetime.now().strftime("%B %d, %Y")

        if not ranked_articles:
            return EmailIntroduction(
                greeting=f"Dear {self.user_profile['name']}, {current_date}",
                introduction="No articles were ranked today."
            )

        top_articles = ranked_articles[:10]

        article_summaries = "\n".join([
            f"{idx + 1}. {article.title if hasattr(article, 'title') else article.get('title', 'N/A')}"
            for idx, article in enumerate(top_articles)
        ])

        user_prompt = f"""
Create an email introduction for:

Name: {self.user_profile['name']}
Date: {current_date}

Top Articles:
{article_summaries}

Return JSON only.
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                temperature=0.7,
                messages=[
                    {
                        "role": "system",
                        "content": EMAIL_PROMPT
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

            # Force greeting
            result["greeting"] = (
                f"Dear {self.user_profile['name']}, {current_date}"
            )

            return EmailIntroduction(
                greeting=result["greeting"],
                introduction=result["introduction"]
            )

        except Exception as e:
            print(f"Error generating introduction: {e}")

            return EmailIntroduction(
                greeting=f"Dear {self.user_profile['name']}, {current_date}",
                introduction="Here are today's top AI news stories."
            )

    def create_email_digest(
        self,
        ranked_articles: List[dict],
        limit: int = 10
    ) -> EmailDigest:

        top_articles = ranked_articles[:limit]

        introduction = self.generate_introduction(
            top_articles
        )

        return EmailDigest(
            introduction=introduction,
            ranked_articles=top_articles
        )

    def create_email_digest_response(
        self,
        ranked_articles: List[RankedArticleDetail],
        total_ranked: int,
        limit: int = 10
    ) -> EmailDigestResponse:

        top_articles = ranked_articles[:limit]

        introduction = self.generate_introduction(
            top_articles
        )

        return EmailDigestResponse(
            introduction=introduction,
            articles=top_articles,
            total_ranked=total_ranked,
            top_n=limit
        )