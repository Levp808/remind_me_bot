PYTHON = .venv/Scripts/python.exe
PIP = .venv/Scripts/pip.exe

install:
	$(PIP) install -r requirements.txt

run:
	$(PYTHON) -m bot.bot

upgrade-pip:
	$(PYTHON) -m pip install --upgrade pip

clean:
	del /s /q __pycache__ 2>nul || exit 0
	del /s /q */__pycache__ 2>nul || exit 0
