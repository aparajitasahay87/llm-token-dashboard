from fetchers.openai_fetcher import project_fetcher, real_fetcher
from repositories.usage_repository import usage_repository
import uuid

class OpenAIService:

    def run_project_key(self):
        print("Running project key fetch...")
        record = project_fetcher.fetch_call(
            model="gpt-3.5-turbo",
            call_type="test_call",
            session_id=str(uuid.uuid4()),
            max_tokens=10,
            temperature=0.3
        )
        if record:
            usage_repository.save(record)
            print("Project key data saved")
            return record
        return None

    def run_real_key(self):
        print("Running real key fetch...")
        record = real_fetcher.fetch_call(
            model="gpt-3.5-turbo",
            call_type="test_call",
            session_id=str(uuid.uuid4()),
            max_tokens=10,
            temperature=0.3
        )
        if record:
            usage_repository.save(record)
            print("Real key data saved")
            return record
        return None

    def simulate_analyze_session(self):
        print("\nSimulating full analyze() session...")
        print("─" * 40)
        session_id = str(uuid.uuid4())
        print(f"Session ID: {session_id}")
        print("─" * 40)

        calls = [
            {
                "call_type":        "reranker",
                "model":            "gpt-4o-mini",
                "max_tokens":       1200,
                "temperature":      0.1,
                "candidates_found": 10,
                "examples_used":    2
            },
            {
                "call_type":     "soarr_analysis",
                "model":         "gpt-4o",
                "max_tokens":    5000,
                "temperature":   0.3,
                "strength_tier": "medium"
            },
            {
                "call_type":        "critic_pass",
                "model":            "gpt-4o-mini",
                "max_tokens":       2000,
                "temperature":      0.1,
                "critic_triggered": True,
                "corrections_made": 2
            },
            {
                "call_type":   "depth_coaching",
                "model":       "gpt-4o-mini",
                "max_tokens":  1500,
                "temperature": 0.3
            }
        ]

        session_records = []
        session_cost    = 0.0
        session_tokens  = 0

        for call in calls:
            record = real_fetcher.fetch_call(
                session_id=session_id,
                messages=[
                    {"role": "user",
                     "content": "Analyse this TPM answer briefly."}
                ],
                **call
            )
            if record:
                usage_repository.save(record)
                session_records.append(record)
                session_cost   += record.cost_usd
                session_tokens += record.total_tokens

        print("─" * 40)
        print(f"Session complete:")
        print(f"  Calls:   {len(session_records)}")
        print(f"  Tokens:  {session_tokens}")
        print(f"  Cost:    ${round(session_cost, 6)}")
        print("─" * 40)

        return session_records

    def get_usage(self):
        return usage_repository.get_by_provider("openai")

    def get_usage_by_source(self, source: str):
        return usage_repository.get_by_source(source)

    def get_total_cost(self):
        return usage_repository.get_total_cost()


openai_service = OpenAIService()