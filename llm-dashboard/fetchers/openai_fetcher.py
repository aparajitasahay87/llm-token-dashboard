from openai import OpenAI
from config.settings import settings
from llm_models import UsageLogModel
from datetime import datetime
import time

class OpenAIFetcher:

    def __init__(self, api_key: str, source: str,
                 project_id: str = None, api_key_id: str = None):
        self.client = OpenAI(api_key=api_key)
        self.provider = "openai"
        self.tier = "paid"
        self.source = source
        self.project_id = project_id
        self.api_key_id = api_key_id

    def fetch_call(self,
                   model: str = "gpt-3.5-turbo",
                   messages: list = None,
                   call_type: str = "test_call",
                   session_id: str = None,
                   max_tokens: int = 10,
                   temperature: float = 0.3,
                   critic_triggered: bool = False,
                   strength_tier: str = None,
                   corrections_made: int = 0,
                   hallucinations_caught: int = 0,
                   candidates_found: int = 0,
                   examples_used: int = 0):
        try:
            if messages is None:
                messages = [
                    {"role": "user", "content": "Say hello in one word"}
                ]

            start_time = time.time()

            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )

            latency_ms = int((time.time() - start_time) * 1000)

            input_tokens  = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens
            total_tokens  = response.usage.total_tokens
            cost_usd      = self._calculate_cost(
                                input_tokens,
                                output_tokens,
                                model
                            )

            record = UsageLogModel(
                project_id=self.project_id,
                api_key_id=self.api_key_id,
                session_id=session_id,
                provider=self.provider,
                model=model,
                tier=self.tier,
                call_type=call_type,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=total_tokens,
                cost_usd=cost_usd,
                latency_ms=latency_ms,
                status="success",
                critic_triggered=critic_triggered,
                strength_tier=strength_tier,
                corrections_made=corrections_made,
                hallucinations_caught=hallucinations_caught,
                candidates_found=candidates_found,
                examples_used=examples_used,
                temperature=temperature,
                max_tokens_set=max_tokens,
                timestamp=datetime.utcnow()
            )

            print(f"✅ {call_type} → {model}")
            print(f"   Tokens:  {total_tokens}")
            print(f"   Cost:    ${cost_usd}")
            print(f"   Latency: {latency_ms}ms")

            return record

        except Exception as e:
            print(f"❌ OpenAI error: {e}")
            return None

    def _calculate_cost(self, input_tokens, output_tokens, model):
        pricing = {
            "gpt-3.5-turbo": {
                "input": 0.0000005,
                "output": 0.0000015
            },
            "gpt-4o": {
                "input": 0.000005,
                "output": 0.000015
            },
            "gpt-4o-mini": {
                "input": 0.00000015,
                "output": 0.0000006
            }
        }

        if model in pricing:
            cost = (
                input_tokens * pricing[model]["input"] +
                output_tokens * pricing[model]["output"]
            )
            return round(cost, 6)
        return 0.0


project_fetcher = OpenAIFetcher(
    api_key=settings.OPENAI_API_KEY,
    source="project_key"
)

real_fetcher = OpenAIFetcher(
    api_key=settings.OPENAI_REAL_KEY,
    source="real_key"
)