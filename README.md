# HealthAIUsingGenAI
Health AI using GenAI with Authentication using Streamlit UI
## Initial Setup
```
> mkdir GenAIwithAuth
> cd GenAIwithAuth
> mkdir HealthAI
> cd HealthAI

> uv venv venv --python cpython-3.11.13-windows-x86_64-none
> venv\Scripts\activate

> git init
> uv pip install streamlit

> echo. > main.py  # Created main.py in windows

> git remote add origin https://github.com/RakeshBhol/HealthAIUsingGenAI.git

> git checkout main  # Updated branch to main
> git fetch origin  # Pull initial file whatever we have in our current remote URL
> uv pip freeze > requirements.txt  # Create requirements.txt
> doskey/history # Will show entire cmd history
```
## Streamlit UI server
```
> streamlit run main.py
```
