from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


# ==========================================================
# YouTube Videos
# ==========================================================

class YouTubeVideo(Base):
    __tablename__ = "youtube_videos"

    video_id = Column(String, primary_key=True)

    title = Column(String, nullable=False)
    url = Column(String, nullable=False)

    channel_id = Column(String, nullable=False)

    published_at = Column(DateTime, nullable=False)

    description = Column(Text)

    transcript = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)


# ==========================================================
# OpenAI Articles
# ==========================================================

class OpenAIArticle(Base):
    __tablename__ = "openai_articles"

    guid = Column(String, primary_key=True)

    title = Column(String, nullable=False)

    url = Column(String, nullable=False)

    description = Column(Text)

    published_at = Column(DateTime, nullable=False)

    category = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)


# ==========================================================
# Anthropic Articles
# ==========================================================

class AnthropicArticle(Base):
    __tablename__ = "anthropic_articles"

    guid = Column(String, primary_key=True)

    title = Column(String, nullable=False)

    url = Column(String, nullable=False)

    description = Column(Text)

    published_at = Column(DateTime, nullable=False)

    category = Column(String, nullable=True)

    markdown = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)


# ==========================================================
# AI Digests
# ==========================================================

class Digest(Base):
    __tablename__ = "digests"

    id = Column(String, primary_key=True)

    article_type = Column(String, nullable=False)

    article_id = Column(String, nullable=False)

    url = Column(String, nullable=False)

    title = Column(String, nullable=False)

    summary = Column(Text, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)


# ==========================================================
# Subscribers
# ==========================================================

class Subscriber(Base):
    __tablename__ = "subscribers"

    id = Column(Integer, primary_key=True, autoincrement=True)

    email = Column(String(255), unique=True, nullable=False, index=True)

    active = Column(Boolean, default=True)

    subscribed_at = Column(DateTime, default=datetime.utcnow)

    last_email_sent = Column(DateTime, nullable=True)