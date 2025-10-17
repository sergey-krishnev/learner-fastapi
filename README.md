🚀 Quick start
# 1) Clone project

# 2) Create & activate venv
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 3) Install deps
pip install --upgrade pip
pip install -r requirements.txt

# (dev) Tools incl. black
pip install -r requirements-dev.txt

# 4) Create .env in the project root:

# ==== App ====
APP_NAME=learner
DEBUG=false

# ==== Database (local) ====
APP_DB_URL=postgresql+asyncpg://user:user@localhost:5432/learner
APP_MONGO_URI=mongodb://localhost:27017
APP_MONGO_DB=quests

# ==== CORS ====
APP_CORS_ALLOWED_ORIGINS=["http://localhost:5173"]
APP_CORS_ALLOWED_METHODS=["GET","POST","PUT","DELETE"]
APP_CORS_ALLOWED_HEADERS=["*"]
APP_CORS_ALLOW_CREDENTIALS=true
APP_CORS_MAX_AGE=3600

.env is loaded by pydantic-settings + python-dotenv.
