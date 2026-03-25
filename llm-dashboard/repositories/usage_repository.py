from config.database import db
from llm_models import UsageLogModel

class UsageRepository:

    def save(self, record: UsageLogModel):
        try:
            data = record.to_dict()
            response = db.client.table("usage_logs").insert(data).execute()
            print(f"Saved: {record.provider} - {record.model}")
            return response
        except Exception as e:
            print(f"Error saving: {e}")
            return None

    def get_all(self):
        try:
            response = db.client.table("usage_logs")\
                .select("*")\
                .execute()
            return response.data
        except Exception as e:
            print(f"Error fetching all: {e}")
            return []

    def get_by_provider(self, provider: str):
        try:
            response = db.client.table("usage_logs")\
                .select("*")\
                .eq("provider", provider)\
                .execute()
            return response.data
        except Exception as e:
            print(f"Error fetching by provider: {e}")
            return []

    def get_by_project(self, project_id: str):
        try:
            response = db.client.table("usage_logs")\
                .select("*")\
                .eq("project_id", project_id)\
                .execute()
            return response.data
        except Exception as e:
            print(f"Error fetching by project: {e}")
            return []

    def get_by_api_key(self, api_key_id: str):
        try:
            response = db.client.table("usage_logs")\
                .select("*")\
                .eq("api_key_id", api_key_id)\
                .execute()
            return response.data
        except Exception as e:
            print(f"Error fetching by api key: {e}")
            return []

    def get_total_cost(self):
        try:
            response = db.client.table("usage_logs")\
                .select("cost_usd")\
                .execute()
            total = sum(row["cost_usd"] for row in response.data)
            return round(total, 6)
        except Exception as e:
            print(f"Error calculating cost: {e}")
            return 0.0

    def get_total_cost_by_project(self, project_id: str):
        try:
            response = db.client.table("usage_logs")\
                .select("cost_usd")\
                .eq("project_id", project_id)\
                .execute()
            total = sum(row["cost_usd"] for row in response.data)
            return round(total, 6)
        except Exception as e:
            print(f"Error calculating cost by project: {e}")
            return 0.0


usage_repository = UsageRepository()