## How to Build and Run

### Prerequisites
- Node.js 18 or higher  
- Python 3.10 or higher  
- MySQL Server  
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/jacness12334/ncsu-csc510-2025-s1-g1-p1.git
cd ncsu-csc510-2025-s1-g1-p1
```
test

### 2. Backend Setup (Flask)

#### Switch to backend branch and navigate to backend directory:
```bash
cd proj2/backend
```

#### Set up Python environment:
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

#### Install Python dependencies:
```bash
pip install -r requirements.txt
```

#### Database Setup:
1. Create MySQL database:
```bash
python database.py
```

2. Import Dummy data for usage:
```bash
python load_database.pu
``` 

3. The backend uses MySQL connection with these credentials (update in `app/app.py` if needed):
   - User: `root`
   - Password: `` (empty)
   - Host: `localhost`

#### Start the backend:
```bash
python run.py
```
Backend runs on `http://localhost:5000`

### 3. Frontend Setup (Next.js)

#### Switch to frontend branch and navigate to frontend directory:
```bash
cd proj2/frontend
```

#### Install dependencies and start:
```bash
npm install
npm run dev
```
Frontend runs on `http://localhost:3000`

### 4. Run Tests
**Note**: Test configurations may need verification
Frontend:
```bash
cd proj2/frontend
npm test
```
Backend:
```bash
cd proj2/backend
python -m pytest
```

### 5. Build for Production (Frontend only)
```bash
cd proj2/frontend
npm run build
npm start
```

### 6. Generate Documentation (Frontend)
```bash
cd proj2/frontend
npm run docs:serve
```
Documentation available at `http://localhost:3000`
