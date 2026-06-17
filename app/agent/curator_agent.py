import os
import json
from typing import List
from groq import Groq
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()


class RankedArticle(BaseModel):
    digest_id: str = Field(
        description="The ID of the digest"
    )
    relevance_score: float = Field(
        ge=0.0,
        le=10.0
    )
    rank: int = Field(
        ge=1
    )
    reasoning: str


class RankedDigestList(BaseModel):
    articles: List[RankedArticle]


CURATOR_PROMPT = """
You are an expert AI news curator.

Return ONLY valid JSON.

Format:

{
  "articles": [
    {
      "digest_id": "id",
      "relevance_score": 8.5,
      "rank": 1,
      "reasoning": "Reason"
    }
  ]
}
"""


class CuratorAgent:
    def __init__(self, user_profile: dict):
        self.client = Groq(
            api_key=os.getenv("GROQ_API_KEY")
        )

        self.model = "llama-3.1-8b-instant"
        self.user_profile = user_profile
        self.system_prompt = self._build_system_prompt()

    def _build_system_prompt(self) -> str:
        interests = "\n".join(
            f"- {interest}"
            for interest in self.user_profile["interests"]
        )

        preferences = self.user_profile["preferences"]

        pref_text = "\n".join(
            f"- {k}: {v}"
            for k, v in preferences.items()
        )

        return f"""
{CURATOR_PROMPT}

User Profile:
Name: {self.user_profile["name"]}
Background: {self.user_profile["background"]}
Expertise Level: {self.user_profile["expertise_level"]}

Interests:
{interests}

Preferences:
{pref_text}
"""

    def rank_digests(
        self,
        digests: List[dict]
    ) -> List[RankedArticle]:

        if not digests:
            return []

        digest_list = "\n\n".join([
            f"ID: {d['id']}\n"
            f"Title: {d['title']}\n"
            f"Summary: {d['summary']}\n"
            f"Type: {d['article_type']}"
            for d in digests
        ])

        user_prompt = f"""
Rank these AI news digests.

{digest_list}

Return JSON only.
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                temperature=0.3,
                messages=[
                    {
                        "role": "system",
                        "content": self.system_prompt
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

            ranked = RankedDigestList(**result)

            return ranked.articles

        except Exception as e:
            print(f"Error ranking digests: {e}")
            return []