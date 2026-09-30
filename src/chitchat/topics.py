"""Curated chitchat conversation starters organized by category."""

from __future__ import annotations

import random
from dataclasses import dataclass


@dataclass
class TopicCategory:
    name: str
    emoji: str
    topics: list[str]


CATEGORIES: list[TopicCategory] = [
    TopicCategory(
        name="Ice Breakers",
        emoji="🧊",
        topics=[
            "What's the most unexpectedly useful skill you've picked up?",
            "If you could instantly master any instrument, which would it be?",
            "What's a hill you will die on that isn't about anything important?",
            "What's the best rabbit hole you've fallen into on the internet recently?",
            "What piece of advice sounded stupid at the time but turned out to be right?",
            "What's the most memorable encounter you've had with a stranger?",
            "If your life had a theme song that played when you entered a room, what would it be?",
            "What food opinion do you hold that would start a fight?",
        ],
    ),
    TopicCategory(
        name="Tech & Tools",
        emoji="🛠️",
        topics=[
            "What tool or workflow improved your life the most this year?",
            "What's a technology you wish existed but doesn't?",
            "What's the most impressive open source project you've discovered lately?",
            "What's your most controversial take on programming languages?",
            "What's a piece of software you'd delete from history if you could?",
            "What's the best keyboard shortcut nobody knows about?",
            "What's your backup strategy and how many times has it saved you?",
            "What's the worst over-engineering you've ever witnessed?",
        ],
    ),
    TopicCategory(
        name="Deep Thoughts",
        emoji="🤔",
        topics=[
            "What problem does humanity need to solve in the next 50 years?",
            "What widely held belief do you think future generations will find absurd?",
            "What's something you believed for years and later discovered was completely wrong?",
            "If you sent a tweet to 1920, what would it say?",
            "What's a beautiful idea from a field completely different from your own?",
            "What question do you wish someone would ask you?",
            "What's the most important thing you've unlearned?",
            "Is there a difference between something being 'not wrong' and being 'right'?",
        ],
    ),
    TopicCategory(
        name="Vienna & Local",
        emoji="🏰",
        topics=[
            "What's the most underrated spot in Vienna that tourists never find?",
            "Best Kaffeehaus in the city and what makes it yours?",
            "What's your least favorite U-Bahn station and why?",
            "What's the one thing about Viennese culture that outsiders never understand?",
            "Best Heuriger you've been to and what made it special?",
            "What's your strategy for surviving a Wiener summer without AC?",
            "What's the most bizarre encounter you've had on the Donauinsel?",
            "Which Viennese district would win in a fight and why?",
        ],
    ),
    TopicCategory(
        name="Creative & Weird",
        emoji="🎨",
        topics=[
            "If you could pitch a movie and get it greenlit tomorrow, what's the premise?",
            "What's a conspiracy theory you don't believe but wish were true?",
            "What would your personal flag look like?",
            "If animals could suddenly talk, which species would be the most insufferable?",
            "What's the best fake word you've invented that should be real?",
            "What mundane object would be the most confusing to explain to someone from 1700?",
            "What's the most creative insult you've ever heard?",
            "Design a new holiday. What does it celebrate and how do people observe it?",
        ],
    ),
    TopicCategory(
        name="Work & Life",
        emoji="⚖️",
        topics=[
            "What's the best career advice you've ever received?",
            "What's a work habit you've adopted that your future self will thank you for?",
            "What's the most important lesson you learned from a terrible boss?",
            "How do you know when it's time to quit vs. push through?",
            "What's your strategy for saying no without feeling guilty?",
            "What's the most valuable thing you do that isn't in your job description?",
            "What's the best meeting format you've ever experienced?",
            "How do you protect your deep work time?",
        ],
    ),
    TopicCategory(
        name="Food & Drink",
        emoji="🍽️",
        topics=[
            "What's your desert island meal - one dish forever?",
            "What ingredient do you put in everything that others find weird?",
            "What's the most overrated food trend right now?",
            "What's the best thing you've ever cooked?",
            "What's a food combination that sounds disgusting but is actually amazing?",
            "What's your ultimate hangover cure meal?",
            "What's the best restaurant experience you've ever had?",
            "Coffee, tea, or something else - and how do you take it?",
        ],
    ),
    TopicCategory(
        name="Hypotheticals",
        emoji="🔮",
        topics=[
            "You get 100 million euros but someone you don't know dies. Your move?",
            "You can undo one mistake from your past. Do you? Which one?",
            "You get to live in any fictional universe. Which one and why?",
            "Aliens land and ask you to explain humanity with one object. What do you show them?",
            "You can teleport but only to places you've already been. How do you use it?",
            "You discover the simulation is real and you're the only one who knows. Now what?",
            "You can read minds but only when the thought is about food. Useful?",
            "What would you do with a week where nobody remembers anything you did?",
        ],
    ),
]


def get_categories() -> list[dict]:
    return [{"name": c.name, "emoji": c.emoji, "count": len(c.topics)} for c in CATEGORIES]


def get_topics(category: str | None = None) -> list[dict]:
    cats = CATEGORIES
    if category:
        cats = [c for c in CATEGORIES if c.name.lower() == category.lower()]
        if not cats:
            return []
    result = []
    for cat in cats:
        for topic in cat.topics:
            result.append({"category": cat.name, "emoji": cat.emoji, "topic": topic})
    return result


def random_topic(category: str | None = None) -> dict | None:
    cats = CATEGORIES
    if category:
        cats = [c for c in CATEGORIES if c.name.lower() == category.lower()]
    if not cats:
        return None
    cat = random.choice(cats)
    topic = random.choice(cat.topics)
    return {"category": cat.name, "emoji": cat.emoji, "topic": topic}


def topic_count() -> int:
    return sum(len(c.topics) for c in CATEGORIES)
