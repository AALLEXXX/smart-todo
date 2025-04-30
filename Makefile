.PHONY: install install-dev compile-ui init-db run lint build clean

install:
	poetry install

install-dev:
	poetry install --with dev
	poetry run pre-commit install

compile-ui:
	poetry run python app/ui_uploader.py
	make lint

init-db:
	-rm app/data/todo.db
	poetry run python app/data/init_db.py

init-db-dev:
	-rm app/data/todo.db
	poetry run python app/data/init_db.py
	poetry run python app/data/init_data.py

run:
	poetry run python main.py

lint:
	poetry run ruff format .
	poetry run ruff check . --fix

build-prod-mac: clean build build-dmg-clean

build-prod-win: clean
	pyinstaller \
	  --name "AlexTodo" \
	  --icon "app/icons/app_icon.ico" \
	  --add-data "app/styles;app/styles" \
	  --add-data "app/ui;app/ui" \
	  --add-data "app/icons;app/icons" \
	  --add-data "app/user_config.ini;." \
	  --add-data "app/data/todo.db;data" \
	  --windowed main.py

build:
	pyinstaller \
	  --name "AlexTodo" \
	  --icon "app/icons/app_icns.icns" \
	  --add-data "app/styles:app/styles" \
	  --add-data "app/ui:app/ui" \
	  --add-data "app/icons:app/icons" \
	  --add-data "app/user_config.ini:." \
	  --add-data "app/data/todo.db:data" \
	  --windowed main.py

build-dmg-clean:
	@rm -rf "dist/AlexTodo.dmg"
	@rm -rf dist/dmg
	@mkdir -p dist/dmg
	@cp -R "dist/AlexTodo.app" dist/dmg/
	create-dmg \
	  --volname "AlexTodo" \
	  --window-size 500 300 \
	  --icon-size 128 \
	  --icon "AlexTodo.app" 100 100 \
	  --icon "Applications" 350 100 \
	  --app-drop-link 350 100 \
	  "dist/AlexTodo.dmg" \
	  "dist/dmg/"
	@rm -rf dist/dmg

clean:
	rm -rf build dist *.spec
	hdiutil detach /Volumes/AlexTodo 2>/dev/null || true
