# Сборка документации. Требуется: pip install -e .[docs]
PYTHON ?= python
SPHINXBUILD ?= $(PYTHON) -m sphinx
DOCS = docs
BUILD = docs/_build
OPTS = -W --keep-going -q

.PHONY: help html html-ru html-en gettext update-po doctest linkcheck check clean

help:
	@echo "html       обе языковые версии в docs/_build/html/{ru,en}"
	@echo "gettext    извлечь строки и обновить docs/locale/en"
	@echo "doctest    выполнить примеры кода на страницах"
	@echo "linkcheck  проверить внешние ссылки"
	@echo "check      проверки перевода, страниц метрик и формул"

html: html-ru html-en

html-ru:
	$(SPHINXBUILD) -b html -D language=ru $(OPTS) $(DOCS) $(BUILD)/html/ru

html-en:
	$(SPHINXBUILD) -b html -D language=en $(OPTS) $(DOCS) $(BUILD)/html/en

gettext:
	$(SPHINXBUILD) -b gettext -q $(DOCS) $(BUILD)/gettext
	sphinx-intl update -p $(BUILD)/gettext -d $(DOCS)/locale -l en

doctest:
	$(SPHINXBUILD) -b doctest -D language=ru -q $(DOCS) $(BUILD)/doctest/ru
	$(SPHINXBUILD) -b doctest -D language=en -q $(DOCS) $(BUILD)/doctest/en

linkcheck:
	$(SPHINXBUILD) -b linkcheck -q $(DOCS) $(BUILD)/linkcheck

check:
	$(PYTHON) $(DOCS)/_dev/check_translations.py
	$(PYTHON) $(DOCS)/_dev/check_metric_pages.py
	$(PYTHON) $(DOCS)/_dev/formula_checks.py

clean:
	$(PYTHON) -c "import shutil; shutil.rmtree('$(BUILD)', True); shutil.rmtree('$(DOCS)/api/generated', True); shutil.rmtree('$(DOCS)/auto_examples', True)"
