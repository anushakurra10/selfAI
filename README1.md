uv venv 

Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1

uv pip install --requirements requirements.txt

.\.venv\Scripts\python.exe -m ensurepip --upgrade

.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install notebook ipykernel


.\.venv\Scripts\python.exe -m ipykernel install --user --name=selfAI --display-name "Python (.venv)"

.\.venv\Scripts\jupyter.exe notebook


reactivate everytime
.\.venv\Scripts\Activate.ps1
.\.venv\Scripts\jupyter.exe notebook

execute below for pythn file
.\.venv\Scripts\python app.py


 .\.venv\Scripts\poetry add jupytext 

# Convert one notebook → plain .py (no cell markers)
 .\.venv\Scripts\poetry run jupytext --to py path/to/notebook.ipynb

# Convert all notebooks in a folder
 .\.venv\Scripts\poetry run jupytext --to py notebooks/*.ipynb


give your source code

