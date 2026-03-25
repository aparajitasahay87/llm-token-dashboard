import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

def setup():
    print("═" * 50)
    print("  LLM Token Dashboard — Setup")
    print("═" * 50)

    # Step 1 — Connect to Supabase
    print("\n1. Connecting to Supabase...")
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    if not url or not key:
        print("❌ Missing SUPABASE_URL or SUPABASE_KEY in .env")
        return

    db = create_client(url, key)
    print("✅ Connected")

    # Step 2 — Create tables
    print("\n2. Creating tables...")
    tables = [
        """
        CREATE TABLE IF NOT EXISTS projects (
            id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            name        TEXT,
            description TEXT,
            total_requests INT DEFAULT 0,
            created_at  TIMESTAMPTZ DEFAULT NOW()
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS api_keys (
            id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            project_id  UUID REFERENCES projects(id),
            provider    TEXT,
            alias       TEXT,
            tier        TEXT,
            key_hash    TEXT,
            created_at  TIMESTAMPTZ DEFAULT NOW()
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS usage_logs (
            id                    UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            project_id            UUID REFERENCES projects(id),
            api_key_id            UUID REFERENCES api_keys(id),
            session_id            TEXT,
            provider              TEXT,
            model                 TEXT,
            tier                  TEXT DEFAULT 'paid',
            call_type             TEXT,
            input_tokens          INT DEFAULT 0,
            output_tokens         INT DEFAULT 0,
            total_tokens          INT DEFAULT 0,
            cost_usd              DECIMAL(10,6) DEFAULT 0,
            latency_ms            INT DEFAULT 0,
            status                TEXT DEFAULT 'success',
            critic_triggered      BOOLEAN DEFAULT FALSE,
            strength_tier         TEXT,
            corrections_made      INT DEFAULT 0,
            hallucinations_caught INT DEFAULT 0,
            candidates_found      INT DEFAULT 0,
            examples_used         INT DEFAULT 0,
            temperature           DECIMAL(3,2),
            max_tokens_set        INT,
            created_at            TIMESTAMPTZ DEFAULT NOW(),
            timestamp             TIMESTAMPTZ DEFAULT NOW()
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS daily_usage (
            id                   UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            project_id           UUID REFERENCES projects(id),
            api_key_id           UUID REFERENCES api_keys(id),
            provider             TEXT,
            model                TEXT,
            usage_date           DATE,
            total_calls          INT DEFAULT 0,
            total_sessions       INT DEFAULT 0,
            input_tokens         INT DEFAULT 0,
            output_tokens        INT DEFAULT 0,
            total_tokens         INT DEFAULT 0,
            cost_usd             DECIMAL(10,6) DEFAULT 0,
            avg_latency_ms       INT DEFAULT 0,
            avg_cost_per_session DECIMAL(10,6) DEFAULT 0,
            critic_rate          DECIMAL(4,2) DEFAULT 0,
            hallucinations_caught INT DEFAULT 0,
            created_at           TIMESTAMPTZ DEFAULT NOW()
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS budgets (
            id            UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            project_id    UUID REFERENCES projects(id),
            api_key_id    UUID REFERENCES api_keys(id),
            provider      TEXT,
            monthly_limit DECIMAL(10,2) DEFAULT 0,
            alert_at_pct  INT DEFAULT 80,
            created_at    TIMESTAMPTZ DEFAULT NOW()
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS insights (
            id           UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            project_id   UUID REFERENCES projects(id),
            insight_text TEXT,
            insight_type TEXT,
            generated_at TIMESTAMPTZ DEFAULT NOW()
        );
        """
    ]

    for sql in tables:
        try:
            db.rpc("exec_sql", {"sql": sql}).execute()
            print(f"  ✅ Table created")
        except Exception as e:
            print(f"  ℹ️  Table may already exist: {e}")

    # Step 3 — Create first project
    print("\n3. Creating your first project...")
    project_name = input("   Enter project name (e.g. My AI App): ").strip()
    if not project_name:
        project_name = "My First Project"

    try:
        result = db.table("projects").insert({
            "name": project_name,
            "description": "Created by LLM Dashboard setup"
        }).execute()

        project_id = result.data[0]["id"]
        print(f"  ✅ Project created")
        print(f"  Project ID: {project_id}")

        # Step 4 — Save project_id to .env
        print("\n4. Saving project ID to .env...")
        with open(".env", "a") as f:
            f.write(f"\nPROJECT_ID={project_id}")
        print(f"  ✅ PROJECT_ID saved to .env")

    except Exception as e:
        print(f"  ❌ Error creating project: {e}")
        return

    # Step 5 — Done
    print("\n" + "═" * 50)
    print("  Setup complete!")
    print("═" * 50)
    print("\nNext steps:")
    print("  1. Run proxy:     python proxy.py")
    print("  2. Run dashboard: python app.py")
    print("  3. Change one line in your project:")
    print('     baseURL: "http://localhost:8000/proxy/openai"')
    print("\nYour data stays on your machine. Always.")
    print("═" * 50)

if __name__ == "__main__":
    setup()