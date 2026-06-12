from flask import Flask, jsonify, request, send_from_directory
import os
import database

app = Flask(__name__, static_folder='site/public', static_url_path='')

@app.after_request
def add_security_headers(response):
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response

# ==========================================
# FRONTEND STATIC FILES SERVING
# ==========================================

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_file(path):
    static_file_path = os.path.join(app.static_folder, path)
    if os.path.exists(static_file_path):
        return send_from_directory(app.static_folder, path)
    
    # Fallback support for extension-less html requests (e.g. /dashboard)
    html_file_path = static_file_path + '.html'
    if os.path.exists(html_file_path):
        return send_from_directory(app.static_folder, path + '.html')
        
    return "Not Found", 404


# ==========================================
# REST API ENDPOINTS
# ==========================================

@app.route('/api/user', methods=['GET'])
def get_user_profile():
    user = database.get_user(user_id=1)
    return jsonify(user)


@app.route('/api/dashboard/summary', methods=['GET'])
def get_dashboard_summary():
    user = database.get_user(user_id=1)
    logs = database.get_carbon_logs(user_id=1)
    
    # Calculate some summary stats
    latest_log = logs[-1] if logs else {
        "transport_emissions": 2.5,
        "energy_emissions": 1.8,
        "diet_emissions": 0.6,
        "total_emissions": 4.9
    }
    
    return jsonify({
        "user": user,
        "latest_log": latest_log,
        "history": logs
    })


@app.route('/api/calculator/log', methods=['POST'])
def log_carbon_calculator():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid payload"}), 400
        
    try:
        log_entry = database.add_carbon_log(user_id=1, log_data=data)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
        
    updated_user = database.get_user(user_id=1)
    
    return jsonify({
        "success": True,
        "log": log_entry,
        "user": updated_user
    })


@app.route('/api/aicoach/chat', methods=['GET'])
def get_chat_logs():
    history = database.get_chat_history(user_id=1)
    return jsonify(history)


@app.route('/api/aicoach/chat', methods=['POST'])
def send_chat_message():
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({"error": "Message required"}), 400
        
    user_message = data['message']
    
    # 1. Save user message to database
    database.add_chat_message(user_id=1, sender='user', message=user_message)
    
    # 2. Analyze user profile and latest log to formulate a smart advice response
    user = database.get_user(user_id=1)
    logs = database.get_carbon_logs(user_id=1)
    
    response_text = ""
    user_text_lower = user_message.lower()
    
    # Custom tailored response selector based on message intent & carbon footprint
    if "hello" in user_text_lower or "hi" in user_text_lower or "hey" in user_text_lower:
        response_text = (
            f"Hello Explorer! I am here to help you optimize your carbon footprint. "
            f"Your current Carbon Score is {user['carbon_score']}/100. "
            "Ask me about 'transportation tips', 'renewable energy advice', or 'diet impact' to begin!"
        )
    elif "score" in user_text_lower or "status" in user_text_lower:
        if user['carbon_score'] > 85:
            response_text = (
                f"Your Carbon Score is a fantastic {user['carbon_score']}/100! "
                "You are leading the way in sustainable habits. Keep maintaining your solar settings and electric transit commutes."
            )
        elif user['carbon_score'] > 60:
            response_text = (
                f"Your Carbon Score is {user['carbon_score']}/100, which is moderate. "
                "We can improve this! Let's look at reducing fossil fuel transit or trying more flexitarian meals."
            )
        else:
            response_text = (
                f"Your Carbon Score is {user['carbon_score']}/100, which is below average. "
                "Don't worry, every small change helps! I suggest adjusting your smart calculator sliders to plan small targets."
            )
    elif "transport" in user_text_lower or "car" in user_text_lower or "bus" in user_text_lower or "transit" in user_text_lower:
        if logs:
            latest = logs[-1]
            if latest['commuting_mode'] == 'Gas Car':
                response_text = (
                    "I notice you commute using a Gas Car. This contributes heavily to your transport score. "
                    "By replacing even 2 trips a week with public transit, or upgrading to an EV, you could save up to 1.5 tons of CO2 annually!"
                )
            else:
                response_text = (
                    "Brilliant job using an Electric Commute option! To optimize further, try combining trips, "
                    "walking for short distances, or charging your EV using renewable energy sources."
                )
        else:
            response_text = "Optimizing your transport is key. Try utilizing public transit, carpooling, bicycling, or EV options to drop transport emissions."
            
    elif "energy" in user_text_lower or "solar" in user_text_lower or "electricity" in user_text_lower:
        if logs:
            latest = logs[-1]
            if latest['renewable_energy'] < 40:
                response_text = (
                    f"Your renewable energy usage is currently at {latest['renewable_energy']}%. "
                    "Upgrading to smart appliances, switching off standby devices, or contracting a local solar utility provider will drastically lower your footprint."
                )
            else:
                response_text = (
                    f"Excellent! Your renewable energy usage is high ({latest['renewable_energy']}%). "
                    "You are preventing major coal grid draw. Consider installing a smart thermostat to automate heating/cooling cycles for even higher savings."
                )
        else:
            response_text = "Try switching to LED light bulbs, choosing Energy Star appliances, or investing in community solar arrays to slash your electricity emissions."
            
    elif "diet" in user_text_lower or "food" in user_text_lower or "eat" in user_text_lower or "meat" in user_text_lower:
        if logs:
            latest = logs[-1]
            if latest['diet'] in ['Omnivore', 'Flexi']:
                response_text = (
                    f"Your diet is logged as {latest['diet']}. "
                    "Meat and dairy production account for substantial methane greenhouse output. Swapping red meat for plant-based proteins just twice a week offers rapid savings!"
                )
            else:
                response_text = (
                    f"Being on a {latest['diet']} diet is wonderful! Plant-based meals have the lowest carbon footprint index. "
                    "To optimize further, try sourcing organic, locally grown vegetables to reduce transportation food-miles."
                )
        else:
            response_text = "A plant-forward diet is one of the most powerful environmental acts. Try integrating Veggie or Vegan days into your week!"
            
    elif "tips" in user_text_lower or "advise" in user_text_lower or "help" in user_text_lower:
        response_text = (
            "Here are your top 3 personalized eco-actions:\n"
            "1. Try completing the 'Eco Commuter' challenge to earn 150 TerraCredits.\n"
            "2. Switch off home electrical appliances at the plug socket when not in use.\n"
            "3. Redeeming a 'Plant a Tree' voucher in the Rewards portal directly offsets 1 ton of carbon."
        )
    else:
        response_text = (
            "Interesting question! Reducing global emissions starts with small, daily changes in diet, "
            "transport, and electricity grid drawing. Adjust your Smart Calculator inputs to simulate different savings scenarios!"
        )
        
    # 3. Save AI response to database
    database.add_chat_message(user_id=1, sender='ai', message=response_text)
    
    return jsonify({
        "success": True,
        "reply": response_text
    })


@app.route('/api/challenges', methods=['GET'])
def get_user_challenges():
    challs = database.get_challenges(user_id=1)
    return jsonify(challs)


@app.route('/api/challenges/complete', methods=['POST'])
def complete_challenge_endpoint():
    data = request.get_json()
    if not data or 'challenge_id' not in data:
        return jsonify({"error": "Challenge ID required"}), 400
        
    res = database.complete_challenge(user_id=1, challenge_id=data['challenge_id'])
    if "error" in res:
        return jsonify(res), 400
        
    return jsonify(res)


@app.route('/api/marketplace/items', methods=['GET'])
def get_marketplace_data():
    user = database.get_user(user_id=1)
    history = database.get_transactions(user_id=1)
    return jsonify({
        "credits": user["credits"],
        "trees": user["trees"],
        "history": history
    })


@app.route('/api/marketplace/redeem', methods=['POST'])
def redeem_marketplace_voucher():
    data = request.get_json()
    if not data or 'item_title' not in data or 'cost_credits' not in data:
        return jsonify({"error": "Item title and credit cost required"}), 400
        
    item_title = data['item_title']
    try:
        cost = int(data['cost_credits'])
    except (ValueError, TypeError):
        return jsonify({"error": "Credit cost must be an integer"}), 400
    
    try:
        res = database.add_transaction(user_id=1, item_title=item_title, cost_credits=cost)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
        
    if "error" in res:
        return jsonify(res), 400
        
    # If the user redeemed planting a tree, increment their trees count
    if "plant a tree" in item_title.lower():
        user = database.get_user(user_id=1)
        database.update_user(1, {"trees": user["trees"] + 1})
        res["trees"] = user["trees"] + 1
        
    return jsonify(res)


# ==========================================
# APP EXECUTION
# ==========================================

if __name__ == '__main__':
    print("Starting TerraMind API Server on http://localhost:8000...")
    debug_mode = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(host='0.0.0.0', port=8000, debug=debug_mode)
