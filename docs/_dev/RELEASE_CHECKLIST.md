# Чек-лист первого выпуска

Пошаговая инструкция с командами: `PUBLISHING.md`. Здесь краткий список.

Версия в `pyproject.toml` не менялась (`0.1.0`). Всё ниже выполняется автором вручную: у агента нет доступа к GitHub,
PyPI и TestPyPI.

## Перед тегом

1. В `CHANGELOG.md` переименовать раздел `Unreleased` в `0.1.0 (дата)`, проверить подразделы «Изменено поведение»,
   «Удалено», «Исправлено».
2. Убедиться, что в `main` зелёные все job'ы `.github/workflows/tests.yml` (тесты, кросс-проверка, документация, упаковка).
   Сам GitHub Actions агентом не запускался, файлы проверены только как YAML.
3. Прочитать `docs/_dev/RELEASE_PREP_REPORT.md`, `KNOWN_ISSUES.md`, `OPEN_QUESTIONS.md`; принять решения по открытым
   вопросам.
4. До сборки заменить в `README.md` и в `docs/` формулировки о том, что публикация на PyPI не проверялась: `README.md`
   становится описанием пакета на PyPI. Команда установки должна стать `pip install hydrometrics`.
5. Локально: `python -m build`, `python -m twine check dist/*`, установка колеса в чистый venv, `pytest`.

## Настройка доверенной публикации PyPI

1. Зарегистрировать проект `hydrometrics` на pypi.org (при первой публикации через *pending publisher*):
   *Your account → Publishing → Add a new pending publisher*.
2. Указать: PyPI project name `hydrometrics`; owner и repository GitHub; workflow `release.yml`; environment `pypi`.
3. То же на test.pypi.org (отдельная учётная запись), если нужна пробная публикация. Для неё нужна копия workflow
   с `repository-url: https://test.pypi.org/legacy/` и отдельным environment `testpypi`.
4. В репозитории GitHub: *Settings → Environments → New environment* с именем `pypi`; при желании включить обязательное
   подтверждение публикации.
5. Секретов в репозиторий добавлять не нужно: `release.yml` использует OIDC (`id-token: write`).

## Проверка через TestPyPI

1. Собрать и загрузить пробный выпуск (вручную `twine upload --repository testpypi dist/*` с API-токеном TestPyPI либо
   через копию workflow).
2. В чистом venv:

   ```
   python -m venv check && check\Scripts\activate
   pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ hydrometrics
   python -c "import hydrometrics as hm; print(hm.__version__)"
   pip install "hydrometrics[all]" --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/
   ```

3. Выполнить пример из README, проверить `hm.__version__`, `hm.nse_bounded`, `hm.nse(..., align="inner")`.

## Релиз

1. Создать аннотированный тег `v0.1.0` на нужном коммите `main` и отправить его: `git tag -a v0.1.0 -m "0.1.0"`,
   `git push origin v0.1.0`.
2. На GitHub: *Releases → Draft a new release*, выбрать тег, вставить раздел `0.1.0` из `CHANGELOG.md`, нажать
   *Publish release*. Это запускает `release.yml` (сборка, `twine check`, публикация).
3. Проверить страницу проекта на pypi.org: описание (README), классификаторы, ссылки, файлы (sdist и колесо).
4. `pip install hydrometrics` в чистом venv, проверить версию.
5. Активировать версию `v0.1.0` на Read the Docs (см. `RTD_CHECKLIST.md`).
6. Открыть ветку для следующей версии: поднять версию в `pyproject.toml` и завести раздел `Unreleased` в
   `CHANGELOG.md`.
