.PHONY: install install-dev compile-ui init-db run lint build clean

install:
	poetry install

install-dev:
	poetry install --with dev
	poetry run pre-commit install

compile-ui:
	poetry run python app/ui_uploader.py

init-db:
	poetry run python app/data/init_db.py

run:
	poetry run python main.py

lint:
	poetry run ruff format .
	poetry run ruff check . --fix

build:
	pyinstaller \
	  --name "AlexTodo" \
	  --icon "app/icons/app_icns.icns" \
	  --add-data "app/styles:styles" \
	  --add-data "app/ui:ui" \
	  --add-data "app/user_config.ini:." \
	  --add-data "app/data/todo.db:data" \
	  --windowed main.py

clean:
	rm -rf build dist *.spec