# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from firebase_admin import credentials, firestore, initialize_app
import os
import hashlib # For password hashing
import uuid # For generating user IDs
import json
import re # For email validation

# Initialize Flask app
app = Flask(__name__)
CORS(app) # Enable Cross-Origin Resource Sharing for frontend integration

# --- Firebase Initialization ---
db = None # Initialize db to None by default

try:
    # Attempt to get service account JSON content from environment variable
    # This is the RECOMMENDED way for deployment platforms like Render.
    firebase_credentials_json = os.getenv('FIREBASE_CREDENTIALS_JSON')

    if firebase_credentials_json:
        # If environment variable is set, parse its content as JSON
        cred = credentials.Certificate(json.loads(firebase_credentials_json))
        if not initialize_app(): # Check if app is already initialized
            initialize_app(cred)
        db = firestore.client()
        print("SUCCESS: Firebase Admin SDK initialized using environment variable credentials.")
    else:
        # Fallback for local development if not using env var, expects a local file.
        # Ensure 'serviceAccountKey.json' is in your backend directory for local testing.
        service_account_path = './serviceAccountKey.json'
        if os.path.exists(service_account_path):
            cred = credentials.Certificate(service_account_path)
            if not initialize_app():
                initialize_app(cred)
            db = firestore.client()
            print(f"SUCCESS: Firebase Admin SDK initialized using local service account file: {service_account_path}")
        else:
            print("ERROR: FIREBASE_CREDENTIALS_JSON environment variable not set and local serviceAccountKey.json not found.")
            print("Firestore database connection is NOT available. API routes requiring DB will fail.")
            db = None # Ensure db is None if initialization fails

except Exception as e:
    print(f"CRITICAL ERROR: An unexpected error occurred during Firebase initialization: {e}")
    db = None
    print("WARNING: Firestore database connection is NOT available. API routes requiring DB will fail.")


# --- Helper Functions ---
def hash_password(password):
    """Hashes a password using SHA256."""
    return hashlib.sha256(password.encode()).hexdigest()

def is_valid_email(email):
    """Basic email format validation."""
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

# --- Firestore Collection References ---
# Ensure db is not None before attempting to get collections
users_ref = db.collection('users') if db else None
career_paths_ref = db.collection('career_paths') if db else None
assessments_ref = db.collection('assessments') if db else None

# --- Dummy Career Paths (if Firestore collection is empty) ---
# Expanded dummy data for more meaningful recommendations
DUMMY_CAREER_PATHS = [
    {"id": "cp1", "name": "Software Engineer", "description": "Develops software applications, focusing on logic and problem-solving.", "skills_needed": ["Python", "Java", "Algorithms", "Problem Solving"], "average_salary_usd": 120000, "interests": ["Math", "Science", "Problem Solving"], "work_environment": ["Independent", "Collaborative"], "impact_areas": ["Innovate and create new technologies", "Analyze data and solve complex problems"]},
    {"id": "cp2", "name": "Data Scientist", "description": "Analyzes large datasets to extract insights and build predictive models.", "skills_needed": ["Statistics", "Machine Learning", "SQL", "Python/R"], "average_salary_usd": 135000, "interests": ["Math", "Science", "Problem Solving"], "work_environment": ["Independent", "Collaborative"], "impact_areas": ["Analyze data and solve complex problems", "Innovate and create new technologies"]},
    {"id": "cp3", "name": "UI/UX Designer", "description": "Designs user interfaces and experiences, focusing on creativity and user empathy.", "skills_needed": ["Figma", "User Research", "Prototyping", "Creativity"], "average_salary_usd": 110000, "interests": ["Arts", "Creative"], "work_environment": ["Collaborative", "Dynamic"], "impact_areas": ["Express creativity and design", "Help people and improve communities"]},
    {"id": "cp4", "name": "Digital Marketing Specialist", "description": "Plans and executes digital marketing campaigns, requiring creativity and social interaction.", "skills_needed": ["SEO", "Content Marketing", "Social Media", "Analytics"], "average_salary_usd": 75000, "interests": ["Arts", "Social"], "work_environment": ["Dynamic", "Collaborative"], "impact_areas": ["Express creativity and design", "Lead and manage projects/teams"]},
    {"id": "cp5", "name": "Financial Analyst", "description": "Evaluates financial data and advises on investments, requiring strong analytical skills.", "skills_needed": ["Excel", "Financial Modeling", "Economics", "Attention to Detail"], "average_salary_usd": 90000, "interests": ["Math", "Problem Solving"], "work_environment": ["Independent", "Collaborative"], "impact_areas": ["Analyze data and solve complex problems"]},
    {"id": "cp6", "name": "Biomedical Researcher", "description": "Conducts scientific research to develop new medical treatments and technologies.", "skills_needed": ["Biology", "Chemistry", "Research Methods", "Lab Skills"], "average_salary_usd": 100000, "interests": ["Science", "Problem Solving"], "work_environment": ["Independent", "Collaborative"], "impact_areas": ["Innovate and create new technologies", "Help people and improve communities"]},
    {"id": "cp7", "name": "Content Writer", "description": "Creates engaging written content for various platforms, demanding creativity and strong communication.", "skills_needed": ["Writing", "Editing", "Research", "Creativity"], "average_salary_usd": 60000, "interests": ["Arts", "Creative"], "work_environment": ["Independent", "Dynamic"], "impact_areas": ["Express creativity and design"]},
    {"id": "cp8", "name": "Social Worker", "description": "Helps individuals and families cope with challenges, requiring strong social and empathetic skills.", "skills_needed": ["Empathy", "Communication", "Problem Solving", "Crisis Intervention"], "average_salary_usd": 55000, "interests": ["Social"], "work_environment": ["Dynamic", "Collaborative"], "impact_areas": ["Help people and improve communities"]},
    {"id": "cp9", "name": "Environmental Scientist", "description": "Investigates environmental problems and develops solutions for conservation and sustainability.", "skills_needed": ["Ecology", "Chemistry", "Data Analysis", "Fieldwork"], "average_salary_usd": 80000, "interests": ["Science", "Problem Solving"], "work_environment": ["Independent", "Dynamic"], "impact_areas": ["Analyze data and solve complex problems", "Help people and improve communities"]},
    {"id": "cp10", "name": "Game Developer", "description": "Designs and programs video games, blending technical skills with creative vision.", "skills_needed": ["Programming (C++/C#)", "Game Design", "Graphics", "Problem Solving", "Creativity"], "average_salary_usd": 95000, "interests": ["Math", "Science", "Creative", "Problem Solving"], "work_environment": ["Collaborative", "Dynamic"], "impact_areas": ["Innovate and create new technologies", "Express creativity and design"]},
    {"id": "cp11", "name": "Architect", "description": "Plans and designs buildings and other structures, combining artistic vision with engineering principles.", "skills_needed": ["Drafting", "Design Software (CAD)", "Problem Solving", "Creativity", "Physics"], "average_salary_usd": 90000, "interests": ["Arts", "Math", "Problem Solving", "Creative"], "work_environment": ["Independent", "Collaborative"], "impact_areas": ["Express creativity and design", "Innovate and create new technologies"]},
    {"id": "cp12", "name": "Journalist", "description": "Researches, writes, and reports news stories, requiring strong communication and social skills.", "skills_needed": ["Writing", "Research", "Interviewing", "Communication", "Social"], "average_salary_usd": 50000, "interests": ["Arts", "Social"], "work_environment": ["Dynamic", "Independent"], "impact_areas": ["Help people and improve communities"]},
    {"id": "cp13", "name": "Mechanical Engineer", "description": "Designs, develops, builds, and tests mechanical devices and systems.", "skills_needed": ["Physics", "Math", "CAD", "Problem Solving", "Design"], "average_salary_usd": 98000, "interests": ["Science", "Math", "Problem Solving"], "work_environment": ["Independent", "Collaborative"], "impact_areas": ["Innovate and create new technologies", "Analyze data and solve complex problems"]},
    {"id": "cp14", "name": "Graphic Designer", "description": "Creates visual concepts using computer software or by hand, to communicate ideas that inspire, inform, or captivate consumers.", "skills_needed": ["Adobe Creative Suite", "Typography", "Color Theory", "Creativity"], "average_salary_usd": 65000, "interests": ["Arts", "Creative"], "work_environment": ["Independent", "Collaborative"], "impact_areas": ["Express creativity and design"]},
    {"id": "cp15", "name": "Teacher", "description": "Educates students in various subjects, requiring strong communication and social skills.", "skills_needed": ["Communication", "Patience", "Subject Matter Expertise", "Social"], "average_salary_usd": 60000, "interests": ["Social"], "work_environment": ["Collaborative", "Dynamic"], "impact_areas": ["Help people and improve communities", "Lead and manage projects/teams"]}
]


# --- API Routes ---

@app.route('/')
def home():
    """Basic home route to confirm server is running."""
    return jsonify({"message": "Career Guidance Backend API is running!"}), 200

@app.route('/register', methods=['POST'])
def register():
    """
    User registration endpoint.
    Expects JSON: {"email": "user@example.com", "password": "securepassword123"}
    """
    if not users_ref:
        return jsonify({"error": "Database not initialized"}), 500

    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400
    if not is_valid_email(email):
        return jsonify({"error": "Invalid email format"}), 400
    if len(password) < 6: # Basic password length validation
        return jsonify({"error": "Password must be at least 6 characters long"}), 400

    try:
        existing_users = users_ref.where('email', '==', email).limit(1).get()
        if existing_users:
            return jsonify({"error": "User with this email already exists"}), 409

        hashed_password = hash_password(password)
        user_id = str(uuid.uuid4()) 

        user_data = {
            "user_id": user_id,
            "email": email,
            "password_hash": hashed_password,
            "created_at": firestore.SERVER_TIMESTAMP
        }
        users_ref.document(user_id).set(user_data)

        return jsonify({"message": "User registered successfully", "user_id": user_id}), 201
    except Exception as e:
        print(f"Error during registration: {e}")
        return jsonify({"error": f"Internal server error during registration: {e}"}), 500

@app.route('/login', methods=['POST'])
def login():
    """
    User login endpoint.
    Expects JSON: {"email": "user@example.com", "password": "securepassword123"}
    """
    if not users_ref:
        return jsonify({"error": "Database not initialized"}), 500

    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400
    if not is_valid_email(email):
        return jsonify({"error": "Invalid email format"}), 400

    try:
        users = users_ref.where('email', '==', email).limit(1).get()
        if not users:
            return jsonify({"error": "Invalid email or password"}), 401

        user_doc = users[0]
        user_data = user_doc.to_dict()
        
        if hash_password(password) == user_data.get('password_hash'):
            return jsonify({"message": "Login successful", "user_id": user_data.get('user_id')}), 200
        else:
            return jsonify({"error": "Invalid email or password"}), 401
    except Exception as e:
        print(f"Error during login: {e}")
        return jsonify({"error": f"Internal server error during login: {e}"}), 500

@app.route('/submit-assessment', methods=['POST'])
def submit_assessment():
    """
    Endpoint to submit user assessment answers.
    Expects JSON: {"user_id": "user123", "answers": {"q1": "A", "q2": "B", "q3": "C", "q4": "D", "q5": "E", "q6": "F"}}
    """
    if not assessments_ref:
        return jsonify({"error": "Database not initialized"}), 500

    data = request.get_json()
    user_id = data.get('user_id')
    answers = data.get('answers')

    if not user_id or not answers:
        return jsonify({"error": "User ID and answers are required"}), 400
    
    # Validate that all expected questions are answered (now 6 questions)
    required_questions = ['q1', 'q2', 'q3', 'q4', 'q5', 'q6']
    if not all(q in answers and answers[q] for q in required_questions):
        return jsonify({"error": "All assessment questions must be answered"}), 400

    try:
        assessment_data = {
            "user_id": user_id,
            "answers": answers,
            "submitted_at": firestore.SERVER_TIMESTAMP
        }
        assessments_ref.add(assessment_data) 
        
        return jsonify({"message": "Assessment submitted successfully"}), 201
    except Exception as e:
        print(f"Error submitting assessment: {e}")
        return jsonify({"error": f"Internal server error during assessment submission: {e}"}), 500

@app.route('/recommend-career', methods=['GET'])
def recommend_career():
    """
    Endpoint to recommend career paths based on user ID and their latest assessment.
    """
    if not career_paths_ref or not assessments_ref:
        print("ERROR: Database references (career_paths_ref or assessments_ref) are not initialized.")
        return jsonify({"error": "Database not initialized"}), 500

    user_id = request.args.get('user_id')
    
    try: # <--- Start of the main try block for the function
        all_career_paths = []
        try:
            # Attempt to fetch all career paths from Firestore
            docs = career_paths_ref.get()
            for doc in docs:
                career_data = doc.to_dict()
                if 'id' not in career_data: # Ensure 'id' field is present for frontend key prop
                    career_data['id'] = doc.id
                all_career_paths.append(career_data)
            
            if not all_career_paths:
                print("DEBUG: Firestore 'career_paths' collection is empty. Using global DUMMY_CAREER_PATHS.")
                all_career_paths = DUMMY_CAREER_PATHS
            else:
                print(f"DEBUG: Fetched {len(all_career_paths)} career paths from Firestore.")

        except Exception as e:
            print(f"ERROR: Error fetching career paths from Firestore: {e}. Falling back to global DUMMY_CAREER_PATHS.")
            all_career_paths = DUMMY_CAREER_PATHS

        # Now, apply personalization based on user assessment if available
        user_answers = {}
        if user_id and assessments_ref:
            try:
                # Fetch the latest assessment for the given user_id
                latest_assessment_query = assessments_ref.where('user_id', '==', user_id).order_by('submitted_at', direction=firestore.Query.DESCENDING).limit(1)
                user_assessments = latest_assessment_query.get()
                
                if user_assessments:
                    user_answers = user_assessments[0].to_dict().get('answers', {})
                    print(f"DEBUG: User {user_id} latest assessment answers: {user_answers}")
                else:
                    print(f"DEBUG: No assessment found for user {user_id}.")
            except Exception as e:
                print(f"ERROR: Could not fetch assessment for user {user_id}: {e}")

        scored_recommendations = []
        if user_answers: # Only score if user answers are available
            print(f"DEBUG: Applying scoring logic for user {user_id} with answers: {user_answers}")
            for rec in all_career_paths:
                score = 0
                
                # Score based on Q1: Subjects enjoyed
                if user_answers.get('q1') and user_answers['q1'] in rec.get('interests', []):
                    score += 3
                
                # Score based on Q2: Activities preferred
                if user_answers.get('q2') and user_answers['q2'] in rec.get('interests', []):
                    score += 3
                
                # Score based on Q3: Work environment
                if user_answers.get('q3') and user_answers['q3'] in rec.get('work_environment', []):
                    score += 2
                
                # Q4: Problem Solving Preference
                if user_answers.get('q4') == 'Yes' and 'Problem Solving' in rec.get('interests', []):
                    score += 4
                elif user_answers.get('q4') == 'No' and 'Problem Solving' not in rec.get('interests', []):
                    score += 1 # Small positive for non-match if user prefers not to solve problems

                # Q5: Learning Style
                if user_answers.get('q5') == 'Hands-on' and ('Independent' in rec.get('work_environment', []) or 'Dynamic' in rec.get('work_environment', [])):
                    score += 3
                elif user_answers.get('q5') == 'Structured' and 'Collaborative' in rec.get('work_environment', []):
                    score += 2
                
                # NEW Q6: Impact Aspiration
                if user_answers.get('q6') and user_answers['q6'] in rec.get('impact_areas', []):
                    score += 5 # Higher score for direct impact match

                # Add a base score to ensure all paths appear, even if low match
                if score == 0:
                    score = 1 # Ensure a minimal score if no direct matches

                scored_recommendations.append({**rec, "score": score})
            
            # Sort recommendations by score in descending order
            scored_recommendations.sort(key=lambda x: x['score'], reverse=True)
            print(f"DEBUG: Scored recommendations for user {user_id} being sent: {scored_recommendations}")
            return jsonify({"user_id": user_id, "recommendations": scored_recommendations}), 200
        else:
            print(f"DEBUG: No user answers for scoring. Returning general career paths.")
            # If no user answers, return all available career paths sorted by salary or a default score
            general_recommendations = sorted(all_career_paths, key=lambda x: x.get('average_salary_usd', 0) if 'average_salary_usd' in x else 0, reverse=True)
            for rec in general_recommendations:
                if 'score' not in rec:
                    rec['score'] = 0 # Assign a default score if missing
            print(f"DEBUG: General recommendations being sent: {general_recommendations}")
            return jsonify({"user_id": user_id or "guest", "recommendations": general_recommendations}), 200

    except Exception as e: # <--- End of the main try block for the function
        print(f"ERROR: Error recommending career: {e}")
        return jsonify({"error": f"Internal server error during career recommendation: {e}"}), 500

# --- Main Entry Point ---
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

