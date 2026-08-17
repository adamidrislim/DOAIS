import json
import re
from typing import Optional

import httpx

from app.config import settings
from app.dto.classification_response import ClassificationResponse
from app.dto.intent_response import IntentResponse
from app.dto.sentiment_response import SentimentResponse
from app.dto.summary_response import SummaryResponse
from app.router.model_router import ModelRouter, TaskType, model_router


class AIService:
    def __init__(
        self,
        http_client: Optional[httpx.Client] = None,
        router: Optional[ModelRouter] = None,
    ):
        self.http_client = http_client or httpx.Client(timeout=120.0)
        self.base_url = settings.OLLAMA_BASE_URL
        self.temperature = settings.OLLAMA_TEMPERATURE
        self.api_key = settings.OLLAMA_API_KEY
        self.router = router or model_router

    def _chat(self, prompt: str, model: str) -> str:
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        response = self.http_client.post(
            f"{self.base_url}/api/chat",
            headers=headers,
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
                "temperature": self.temperature,
            },
        )
        response.raise_for_status()
        return response.json()["message"]["content"]

    def classify_text(self, text: str) -> ClassificationResponse:
        model = self.router.get_model(TaskType.CLASSIFY)
        prompt = (
            "Analyze the following text and classify it with appropriate labels and tags. "
            "Respond with ONLY valid JSON, no additional text or explanation.\n\n"
            f"Text: {text}\n\n"
            "Return JSON in this exact format:\n"
            '{"labels": ["label1", "label2"], "primaryCategory": "category", "confidence": 0.9}'
        )
        response = self._chat(prompt, model)
        return self._parse_json(response, ClassificationResponse)

    def analyze_sentiment(self, text: str) -> SentimentResponse:
        model = self.router.get_model(TaskType.SENTIMENT)
        prompt = (
            "Analyze the sentiment of the following text. "
            "Respond with ONLY valid JSON, no additional text or explanation.\n\n"
            f"Text: {text}\n\n"
            "sentimentScore must be a number from -1 to 1 that is numerically "
            "consistent with overallSentiment: strongly negative text should score "
            "close to -1, strongly positive text should score close to 1, neutral "
            "text should score close to 0, and mixed text (containing both clearly "
            "positive and clearly negative elements) should score close to 0, "
            "reflecting the balance between the positive and negative elements "
            "rather than only the negative ones. Do not default to positive scores "
            "for negative or neutral text, and do not default to negative scores "
            "for mixed text.\n\n"
            "emotions must include at least one emotion representing each distinct "
            "sentiment present in the text — for mixed text, include emotions for "
            "both the positive elements (e.g. admiration, satisfaction) and the "
            "negative elements (e.g. disappointment, frustration), not just one side.\n\n"
            "Examples:\n"
            'Negative text -> {"overallSentiment": "negative", "sentimentScore": -0.8, '
            '"emotions": ["anger", "disappointment"], "confidence": 0.9}\n'
            'Positive text -> {"overallSentiment": "positive", "sentimentScore": 0.8, '
            '"emotions": ["joy", "excitement"], "confidence": 0.9}\n'
            'Mixed text -> {"overallSentiment": "mixed", "sentimentScore": 0.1, '
            '"emotions": ["admiration", "disappointment"], "confidence": 0.9}\n\n'
            "Return JSON in this exact format:\n"
            '{"overallSentiment": "positive|negative|neutral|mixed", "sentimentScore": 0.0, '
            '"emotions": ["emotion1", "emotion2"], "confidence": 0.9}'
        )
        response = self._chat(prompt, model)
        return self._parse_json(response, SentimentResponse)

    def summarize_text(self, text: str) -> SummaryResponse:
        model = self.router.get_model(TaskType.SUMMARIZE)
        prompt = (
            "Summarize the following text concisely. "
            "Respond with ONLY valid JSON, no additional text or explanation.\n\n"
            f"Text: {text}\n\n"
            "Return JSON in this exact format:\n"
            '{"summary": "your summary here", "keyPoints": ["point1", "point2", "point3"], "wordCount": 25}'
        )
        response = self._chat(prompt, model)
        return self._parse_json(response, SummaryResponse)

    def detect_intent(self, text: str) -> IntentResponse:
        model = self.router.get_model(TaskType.INTENT)
        prompt = (
            "Detect the intent behind the following text. "
            "Respond with ONLY valid JSON, no additional text or explanation.\n\n"
            f"Text: {text}\n\n"
            "intentCategory must be exactly one of:\n"
            "- question: the text asks for information\n"
            "- request: the text politely asks someone to do something\n"
            "- command: the text gives a direct order or instruction\n"
            "- statement: the text declares facts or information\n\n"
            "primaryIntent must be a short, specific phrase describing what the "
            "text is actually about or trying to accomplish (the topic/purpose), "
            "NOT a restatement of intentCategory. For example, for a command about "
            "smart home devices, primaryIntent should be something like 'home "
            "automation control', not 'command'.\n\n"
            "secondaryIntents must list other distinct purposes present in the "
            "text, if any. Do not repeat primaryIntent or intentCategory in this "
            "list; return an empty array if there are none.\n\n"
            "Example:\n"
            'Text: "Turn off the lights and lock the doors." -> '
            '{"primaryIntent": "home automation control", "secondaryIntents": [], '
            '"intentCategory": "command", "confidence": 0.9}\n\n'
            "Return JSON in this exact format:\n"
            '{"primaryIntent": "specific purpose description", "secondaryIntents": ["intent1"], '
            '"intentCategory": "question", "confidence": 0.9}'
        )
        response = self._chat(prompt, model)
        return self._parse_json(response, IntentResponse)

    @staticmethod
    def _parse_json(raw: str, model_class: type):
        cleaned = raw.strip()
        # Strip markdown code blocks if present
        cleaned = re.sub(r"^```json\s*", "", cleaned)
        cleaned = re.sub(r"^```\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
        cleaned = cleaned.strip()
        try:
            data = json.loads(cleaned)
            return model_class(**data)
        except Exception as e:
            raise RuntimeError(f"Failed to parse AI response as JSON: {raw}") from e
