# AI Career Counsellor

An AI-driven web application that helps students discover personalized career paths based on their interests and preferences.

## 🔍 Features
- 🔐 User Registration & Login (Flask + Firebase)
- ✅ 6-question career assessment
- 🎯 Personalized career recommendations using a scoring algorithm
- 💡 Dynamic frontend built with React.js + Tailwind CSS
- 🔁 Persistent state with localStorage and Firebase Firestore

## 🛠️ Tech Stack

| Layer       | Tools                                 |
|-------------|----------------------------------------|
| Backend     | Flask, Firebase Admin SDK, Firestore  |
| Frontend    | React.js, Tailwind CSS, Babel         |
| Utilities   | UUID, hashlib, Flask-CORS             |

## ⚙️ Setup Instructions

### 1. Clone the repo
```bash
git clone https://github.com/yourusername/ai-career-counsellor.git
cd ai-career-counsellor
```

### 2. Backend Setup
- Ensure Python 3.7+ is installed.
- Install dependencies:
```bash
pip install flask firebase-admin flask-cors
```
- Place your Firebase `serviceAccountKey.json` in the root folder.
- Run the backend:
```bash
python app.py
```

### 3. Frontend
- Open `index.html` in your browser.
- Ensure the backend is running on `http://localhost:5000`.

## 📁 Project Structure
```
├── app.py                    # Flask backend API
├── serviceAccountKey.json    # Firebase credentials
├── index.html                # React frontend with Tailwind via CDN
├── README.md                 # Project info
└── AI_Career_Counsellor_Summary.docx  # Project report
```

## 🤝 Contributing
Feel free to fork this repo, file issues, or suggest improvements!

## 📜 License
MIT License
