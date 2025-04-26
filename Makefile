.PHONY: install compile-ui init-db run build clean

install:
	poetry install

compile-ui:
	poetry run python ui_uploader.py

init-db:
	poetry run python data/init_db.py

run:
	poetry run python main.py

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