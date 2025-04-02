echo [$(date)]: "START"
echo [$(date)]: "Creating conda env with python 3.11" # CHANGE THE VERSION BASE DON YOUR WORK
conda create --prefix ./venv python=3.11 -y
echo [$(date)]: "activate virtual env"
source activate ./venv
echo [$(date)]: "Install UV for python"
pip install uv
echo [$(date)]: "installing dev requirements with latest version"
uv pip install -r requirements.txt
echo [$(date)]: "END"
