echo [$(date)]: "START"
echo [$(date)]: "Creating env"
python -m venv venv
echo [$(date)]: "Activate env"
source venv/bin/activate
echo [$(date)]: "Installing requirements"
pip install -r requirements.txt
echo [$(date)]: "Starting app locally"
uvicorn src.main:app --reload
echo [$(date)]: "END"