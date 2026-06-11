import os
import datetime

# Helper to load .env variables without external dependencies
def load_dotenv():
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    key, val = line.split("=", 1)
                    os.environ[key.strip()] = val.strip()

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

# Check if credentials look like placeholders or are empty
use_supabase = bool(
    SUPABASE_URL and 
    SUPABASE_KEY and 
    "your-project" not in SUPABASE_URL and 
    "your-anon-key" not in SUPABASE_KEY
)

client = None

if use_supabase:
    try:
        from supabase import create_client
        client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print(f"Connected to Supabase project at {SUPABASE_URL}")
    except Exception as e:
        print(f"Error: Failed to connect to Supabase: {e}. Falling back to mock database.")
        use_supabase = False
else:
    print("No Supabase configuration detected in .env. Running in Mock Database mode.")


# ==========================================
# IN-MEMORY MOCK DATABASE FALLBACK
# ==========================================

class MockDB:
    def __init__(self):
        self.user = {
            "id": 1,
            "username": "Guest Explorer",
            "email": "guest@terramind.eco",
            "carbon_score": 82,
            "xp": 24500,
            "level": 24,
            "credits": 4500,
            "trees": 8,
            "created_at": str(datetime.datetime.now())
        }
        
        self.challenges = [
            {"id": 1, "title": "Eco Commuter", "description": "Log 5 public transport trips instead of driving this week.", "reward_xp": 300, "reward_credits": 150, "category": "Transport"},
            {"id": 2, "title": "Green Chef", "description": "Cook plant-based meals for 3 consecutive days.", "reward_xp": 250, "reward_credits": 100, "category": "Diet"},
            {"id": 3, "title": "Power Saver", "description": "Reduce home energy consumption by 10% this month.", "reward_xp": 500, "reward_credits": 250, "category": "Energy"},
            {"id": 4, "title": "Waste Warrior", "description": "Compost organic waste for a week.", "reward_xp": 200, "reward_credits": 100, "category": "Waste"}
        ]
        
        self.user_challenges = {
            1: [
                {"challenge_id": 1, "completed": False, "progress": 3, "completed_at": None},
                {"challenge_id": 2, "completed": True, "progress": 3, "completed_at": str(datetime.datetime.now())},
                {"challenge_id": 3, "completed": False, "progress": 0, "completed_at": None},
                {"challenge_id": 4, "completed": False, "progress": 0, "completed_at": None}
            ]
        }
        
        self.carbon_logs = [
            {"id": 101, "user_id": 1, "date": str(datetime.date.today() - datetime.timedelta(days=6)), "public_transport": 20, "renewable_energy": 10, "diet": "Omnivore", "commuting_mode": "Gas Car", "transport_emissions": 2.5, "energy_emissions": 1.8, "diet_emissions": 1.2, "total_emissions": 5.5},
            {"id": 102, "user_id": 1, "date": str(datetime.date.today() - datetime.timedelta(days=5)), "public_transport": 25, "renewable_energy": 15, "diet": "Flexi", "commuting_mode": "Gas Car", "transport_emissions": 2.2, "energy_emissions": 1.6, "diet_emissions": 0.9, "total_emissions": 4.7},
            {"id": 103, "user_id": 1, "date": str(datetime.date.today() - datetime.timedelta(days=4)), "public_transport": 30, "renewable_energy": 20, "diet": "Flexi", "commuting_mode": "Electric", "transport_emissions": 1.8, "energy_emissions": 1.5, "diet_emissions": 0.9, "total_emissions": 4.2},
            {"id": 104, "user_id": 1, "date": str(datetime.date.today() - datetime.timedelta(days=3)), "public_transport": 40, "renewable_energy": 30, "diet": "Veggie", "commuting_mode": "Electric", "transport_emissions": 1.2, "energy_emissions": 1.2, "diet_emissions": 0.5, "total_emissions": 2.9},
            {"id": 105, "user_id": 1, "date": str(datetime.date.today() - datetime.timedelta(days=2)), "public_transport": 45, "renewable_energy": 30, "diet": "Veggie", "commuting_mode": "Electric", "transport_emissions": 0.9, "energy_emissions": 1.2, "diet_emissions": 0.5, "total_emissions": 2.6},
            {"id": 106, "user_id": 1, "date": str(datetime.date.today() - datetime.timedelta(days=1)), "public_transport": 45, "renewable_energy": 30, "diet": "Veggie", "commuting_mode": "Electric", "transport_emissions": 0.9, "energy_emissions": 1.2, "diet_emissions": 0.5, "total_emissions": 2.6}
        ]
        
        self.chat_history = [
            {"id": 1, "user_id": 1, "sender": "ai", "message": "Welcome to TerraMind, Guest Explorer! I am your EcoCoach AI. Let me know if you want tips on reducing your emissions or optimizing your daily sustainability habits.", "created_at": str(datetime.datetime.now())}
        ]
        
        self.transactions = [
            {"id": 1, "user_id": 1, "item_title": "Solar Lamp Set", "cost_credits": 2200, "status": "Shipped", "created_at": str(datetime.datetime.now() - datetime.timedelta(days=30))},
            {"id": 2, "user_id": 1, "item_title": "National Park Pass", "cost_credits": 850, "status": "Completed", "created_at": str(datetime.datetime.now() - datetime.timedelta(days=45))}
        ]

mock_db = MockDB()


# ==========================================
# DATABASE INTERFACE IMPLEMENTATION
# ==========================================

def get_user(user_id=1):
    if use_supabase:
        try:
            res = client.table("users").select("*").eq("id", user_id).execute()
            if res.data:
                return res.data[0]
            # Create user if not found on cloud
            new_user = {
                "id": user_id,
                "username": "Guest Explorer",
                "email": "guest@terramind.eco",
                "carbon_score": 82,
                "xp": 24500,
                "level": 24,
                "credits": 4500,
                "trees": 8
            }
            client.table("users").insert(new_user).execute()
            return new_user
        except Exception as e:
            print(f"Supabase get_user error: {e}")
            return mock_db.user
    else:
        return mock_db.user

def update_user(user_id, update_data):
    if use_supabase:
        try:
            res = client.table("users").update(update_data).eq("id", user_id).execute()
            if res.data:
                return res.data[0]
        except Exception as e:
            print(f"Supabase update_user error: {e}")
    
    # Update local state
    for k, v in update_data.items():
        if k in mock_db.user:
            mock_db.user[k] = v
    return mock_db.user

def get_carbon_logs(user_id=1):
    if use_supabase:
        try:
            res = client.table("carbon_logs").select("*").eq("user_id", user_id).order("date").execute()
            return res.data
        except Exception as e:
            print(f"Supabase get_carbon_logs error: {e}")
            return mock_db.carbon_logs
    else:
        return mock_db.carbon_logs

def add_carbon_log(user_id, log_data):
    # Calculate emissions values
    pt = log_data.get("public_transport", 0)
    re = log_data.get("renewable_energy", 0)
    diet = log_data.get("diet", "Veggie")
    mode = log_data.get("commuting_mode", "Electric")
    
    # Simple emission formula:
    # transport: starts high, public transport and EV reduce it
    base_trans = 5.0
    pt_reduction = (pt / 100.0) * 2.0
    ev_multiplier = 0.2 if mode == "Electric" else 1.0
    transport_emissions = round(max(0.2, (base_trans - pt_reduction) * ev_multiplier), 1)
    
    # energy: starts high, renewable energy reduces it
    base_energy = 4.0
    re_reduction = (re / 100.0) * 3.2
    energy_emissions = round(max(0.4, base_energy - re_reduction), 1)
    
    # diet emissions: Omnivore (1.8), Flexi (1.2), Veggie (0.6), Vegan (0.3)
    diet_map = {"Omnivore": 1.8, "Flexi": 1.2, "Veggie": 0.6, "Vegan": 0.3}
    diet_emissions = diet_map.get(diet, 0.6)
    
    total_emissions = round(transport_emissions + energy_emissions + diet_emissions, 1)
    
    # New score calculation (starts at 100, drops as emissions grow)
    # 0 total emissions = 100 score, 12+ total emissions = 20 score
    new_score = int(max(10, 100 - (total_emissions * 7)))
    
    # Create DB payload
    db_payload = {
        "user_id": user_id,
        "date": str(datetime.date.today()),
        "public_transport": pt,
        "renewable_energy": re,
        "diet": diet,
        "commuting_mode": mode,
        "transport_emissions": transport_emissions,
        "energy_emissions": energy_emissions,
        "diet_emissions": diet_emissions,
        "total_emissions": total_emissions
    }
    
    if use_supabase:
        try:
            client.table("carbon_logs").insert(db_payload).execute()
            # Update user score
            update_user(user_id, {"carbon_score": new_score})
        except Exception as e:
            print(f"Supabase add_carbon_log error: {e}")
    
    # Mock fallback updates
    db_payload["id"] = len(mock_db.carbon_logs) + 101
    mock_db.carbon_logs.append(db_payload)
    # Remove older logs if database becomes too large for mock memory representation
    if len(mock_db.carbon_logs) > 30:
        mock_db.carbon_logs.pop(0)
        
    mock_db.user["carbon_score"] = new_score
    return db_payload

def get_chat_history(user_id=1):
    if use_supabase:
        try:
            res = client.table("chat_history").select("*").eq("user_id", user_id).order("id").execute()
            return res.data
        except Exception as e:
            print(f"Supabase get_chat_history error: {e}")
            return mock_db.chat_history
    else:
        return mock_db.chat_history

def add_chat_message(user_id, sender, message):
    db_payload = {
        "user_id": user_id,
        "sender": sender,
        "message": message
    }
    
    if use_supabase:
        try:
            client.table("chat_history").insert(db_payload).execute()
        except Exception as e:
            print(f"Supabase add_chat_message error: {e}")
            
    db_payload["id"] = len(mock_db.chat_history) + 1
    db_payload["created_at"] = str(datetime.datetime.now())
    mock_db.chat_history.append(db_payload)
    return db_payload

def get_challenges(user_id=1):
    if use_supabase:
        try:
            # Join user completion state
            challs = client.table("challenges").select("*").execute().data
            user_challs = client.table("user_challenges").select("*").eq("user_id", user_id).execute().data
            
            # Create a lookup for user challenge records
            lookup = {uc["challenge_id"]: uc for uc in user_challs}
            
            result = []
            for c in challs:
                state = lookup.get(c["id"], {"completed": False, "progress": 0})
                result.append({
                    "id": c["id"],
                    "title": c["title"],
                    "description": c["description"],
                    "reward_xp": c["reward_xp"],
                    "reward_credits": c["reward_credits"],
                    "category": c["category"],
                    "completed": state["completed"],
                    "progress": state["progress"]
                })
            return result
        except Exception as e:
            print(f"Supabase get_challenges error: {e}")
    
    # Mock database mapping
    result = []
    user_state = mock_db.user_challenges.get(user_id, [])
    lookup = {uc["challenge_id"]: uc for uc in user_state}
    for c in mock_db.challenges:
        state = lookup.get(c["id"], {"completed": False, "progress": 0})
        result.append({
            **c,
            "completed": state["completed"],
            "progress": state["progress"]
        })
    return result

def complete_challenge(user_id, challenge_id):
    challs = get_challenges(user_id)
    target = None
    for c in challs:
        if c["id"] == challenge_id:
            target = c
            break
            
    if not target or target["completed"]:
        return {"error": "Challenge already completed or invalid"}
        
    # Award credits and XP
    user = get_user(user_id)
    new_credits = user["credits"] + target["reward_credits"]
    new_xp = user["xp"] + target["reward_xp"]
    new_level = user["level"]
    
    # Every 5000 XP advances a level
    if new_xp >= new_level * 1000 + 500:
        new_level += 1
        
    update_data = {
        "credits": new_credits,
        "xp": new_xp,
        "level": new_level
    }
    
    update_user(user_id, update_data)
    
    # Update challenge completion
    if use_supabase:
        try:
            client.table("user_challenges").upsert({
                "user_id": user_id,
                "challenge_id": challenge_id,
                "completed": True,
                "progress": 5, # Max
                "completed_at": str(datetime.datetime.now())
            }).execute()
        except Exception as e:
            print(f"Supabase complete_challenge error: {e}")
            
    # Mock update
    user_states = mock_db.user_challenges.get(user_id, [])
    for uc in user_states:
        if uc["challenge_id"] == challenge_id:
            uc["completed"] = True
            uc["progress"] = 5
            uc["completed_at"] = str(datetime.datetime.now())
            
    return {
        "success": True,
        "reward_xp": target["reward_xp"],
        "reward_credits": target["reward_credits"],
        "user": {**user, **update_data}
    }

def get_transactions(user_id=1):
    if use_supabase:
        try:
            res = client.table("transactions").select("*").eq("user_id", user_id).order("id", desc=True).execute()
            return res.data
        except Exception as e:
            print(f"Supabase get_transactions error: {e}")
            return mock_db.transactions
    else:
        return mock_db.transactions

def add_transaction(user_id, item_title, cost_credits):
    user = get_user(user_id)
    if user["credits"] < cost_credits:
        return {"error": "Insufficient credits"}
        
    # Deduct credits
    new_credits = user["credits"] - cost_credits
    update_user(user_id, {"credits": new_credits})
    
    db_payload = {
        "user_id": user_id,
        "item_title": item_title,
        "cost_credits": cost_credits,
        "status": "Processing"
    }
    
    if use_supabase:
        try:
            client.table("transactions").insert(db_payload).execute()
        except Exception as e:
            print(f"Supabase add_transaction error: {e}")
            
    db_payload["id"] = len(mock_db.transactions) + 1
    db_payload["created_at"] = str(datetime.datetime.now())
    mock_db.transactions.insert(0, db_payload) # insert at top
    
    return {
        "success": True,
        "credits": new_credits,
        "transaction": db_payload
    }
