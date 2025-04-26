.PHONY: install install-dev compile-ui init-db run lint build clean

install:
	poetry install

install-dev:
	poetry install --with dev
	poetry run pre-commit install

compile-ui:
	poetry run python ui_uploader.py

init-db:
	poetry run python data/init_db.py

run:
	poetry run python main.py

lint:
	poetry run ruff format .
	poetry run ruff check . --fix

build:
	pyinstaller \
	  --name "AlexTodo" \
	  --icon "icons/app_icns.icns" \
	  --add-data "styles:styles" \
	  --add-data "ui:ui" \
	  --add-data "user_config.ini:." \
	  --add-data "data/todo.db:data" \
	  --windowed main.py

clean:
	rm -rf build dist *.spec