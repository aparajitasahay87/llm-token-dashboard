import requests
from datetime import datetime, timedelta
from config.settings import settings

class OpenAIHistoryFetcher:

    def __init__(self):
        self.api_key = settings.OPENAI_REAL_KEY
        self.base_url = "https://api.openai.com/v1/usage"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}"
        }

    def fetch_day(self, date: datetime) -> dict:
        try:
            date_str = date.strftime("%Y-%m-%d")
            response = requests.get(
                self.base_url,
                headers=self.headers,
                params={"date": date_str}
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    "date": date_str,
                    "status": "success",
                    "data": data
                }
            else:
                return {
                    "date": date_str,
                    "status": "error",
                    "code": response.status_code,
                    "message": response.text
                }

        except Exception as e:
            return {
                "date": date_str,
                "status": "error",
                "message": str(e)
            }

    def fetch_last_n_days(self, days: int = 10) -> list:
        results = []
        for i in range(days):
            date = datetime.utcnow() - timedelta(days=i)
            result = self.fetch_day(date)
            results.append(result)
            print(f"Fetched: {result['date']} → {result['status']}")
        return results

    def summarize(self, results: list) -> dict:
        summary = {
            "total_days": len(results),
            "successful_days": 0,
            "total_requests": 0,
            "total_tokens": 0,
            "daily_breakdown": []
        }

        for r in results:
            if r["status"] == "success":
                summary["successful_days"] += 1
                data = r.get("data", {})
                daily_requests = sum(
                    item.get("n_requests", 0)
                    for item in data.get("data", [])
                )
                daily_tokens = sum(
                    item.get("n_context_tokens_total", 0) +
                    item.get("n_generated_tokens_total", 0)
                    for item in data.get("data", [])
                )
                summary["total_requests"] += daily_requests
                summary["total_tokens"]   += daily_tokens
                summary["daily_breakdown"].append({
                    "date": r["date"],
                    "requests": daily_requests,
                    "tokens": daily_tokens
                })

        return summary


openai_history_fetcher = OpenAIHistoryFetcher()