# Упаковка: результаты проверок (этап E, пункты 1-5 и 7)

Все проверки выполнены локально на Windows 11, `uv` (venv и установка), `PYTHONUTF8=1`,
`PYTHONDONTWRITEBYTECODE=1`, `pytest -p no:cacheprovider -o addopts=`, из корня репозитория.
Набор `tests/crosscheck` исключён (`--ignore=tests/crosscheck`). Версия пакета не менялась (0.1.0).
Артефакты сборки и окружения лежат вне репозитория (scratch-каталог сессии).

## 1. Нижние границы зависимостей (E2)

Окружение: CPython 3.10.22, `uv pip install --resolution lowest-direct ".[all,test]"`
(установка из копии репозитория, чтобы не создавать `*.egg-info` в корне), затем
`pip uninstall hydrometrics` и `python -m pytest tests --ignore=tests/crosscheck` из корня репозитория.

Установились ровно заявленные минимумы: numpy 1.24.0, pandas 2.0.0, polars 0.19.0,
xarray 2023.1.0, scipy 1.10.0, pytest 7.4.0, pytest-cov 4.1.0.

| Зависимость | Было | Стало | Комментарий |
|---|---|---|---|
| numpy | >=1.24 | >=1.24 | без изменений |
| pandas | >=2.0 | >=2.0 | без изменений |
| polars | >=0.19 | >=0.19 | без изменений |
| xarray | >=2023.1 | >=2023.1 | без изменений |
| scipy | >=1.10 | >=1.10 | без изменений |
| pytest | >=7.4 | >=7.4 | без изменений |
| pytest-cov | >=4.1 | >=4.1 | без изменений |

Результат на минимумах: 2844 passed, 44 skipped, 0 failed (44 пропуска: `sphinx` не установлен,
`test_metadata.py` использует `importorskip("sphinx.ext.napoleon.docstring")`).

Первый прогон на минимумах дал 2 падения и 1 ошибку сбора, все они были в ТЕСТАХ, а не в границах:

* `tests/test_packaging.py`: `import tomllib` (есть только с Python 3.11). Исправлено: на 3.10
  берётся `tomli` (его ставит pytest на 3.10), если его нет, модуль пропускается.
* `tests/test_axis.py`, `tests/test_exceptions.py`: `np.exceptions.AxisError` появилось в numpy 1.25.
  Библиотека уже совместима (`getattr(np, "exceptions", np).AxisError` в `backends/xarray.py`), тесты
  приведены к тому же выражению. Проверка не ослаблена.

Нижние границы выше минимально необходимых не поднимались; ниже заявленных не проверялись
(это не входило в задачу).

Только numpy (без extras), numpy 1.24.0 + pytest 7.4.0 + tomli, Python 3.10:
1279 passed, 1527 skipped, 0 failed. Пропуски: тесты, которым нужны pandas/polars/xarray/scipy,
и 44 теста sphinx.

## 2. Версии Python (E1)

Все версии взяты через `uv venv --python X`, установка `.[all,test]` без ограничения версий
(последние зависимости; для 3.10 дополнительно самые старые), прогон `pytest tests --ignore=tests/crosscheck`.

| Python | Набор зависимостей | Результат |
|---|---|---|
| 3.10.22 | lowest-direct | 2844 passed, 44 skipped |
| 3.11 | последние (numpy 2.4.6, pandas 3.1.1, polars 2.1.0, xarray 2026.9.0) | 2844 passed, 44 skipped |
| 3.12 | последние | 2844 passed, 44 skipped |
| 3.13 | последние | 2844 passed, 44 skipped |
| 3.14 | последние | 2844 passed, 44 skipped |
| 3.15.2 | последние | 2844 passed, 44 skipped |

Не проверялись: 3.9 (ниже `requires-python`; на нём `tests/test_packaging.py` и часть синтаксиса
не применимы), 3.10 с последними зависимостями.

Классификаторы в `pyproject.toml`: 3.10, 3.11, 3.12 (были) плюс 3.13, 3.14, 3.15 (проверены).
`requires-python = ">=3.10"` совпадает с самой низкой проверенной версией.

Найден дефект теста (не библиотеки): `tests/test_optional_dependencies.py::run_blocked` запускал
подпроцесс с минимальным окружением (`PYTHONPATH`, `PYTHONUTF8`, `SYSTEMROOT`) и на Python 3.11 + polars 2.1
падал с `RuntimeError: unknown feature flag: 'sse3'` (проверка CPU в polars использует переменные окружения
Windows). Теперь окружение берётся из `os.environ` с переопределением `PYTHONPATH` и `PYTHONUTF8`.

## 3. Сборка (E3)

```
python -m build --outdir <scratch>\dist .          # Python 3.12, build + twine в отдельном venv
python -m twine check <scratch>\dist\*
```

Результат: собраны `hydrometrics-0.1.0.tar.gz` (97 158 байт) и `hydrometrics-0.1.0-py3-none-any.whl`
(64 206 байт); `twine check`: PASSED для обоих файлов.

Предупреждение setuptools при сборке (не ошибка): таблица `license = {text = "MIT"}` и классификатор
`License :: OSI Approved :: MIT License` объявлены устаревшими в пользу SPDX-выражения
(`license = "MIT"`, требует `setuptools>=77`). Не менялось (правка вне разрешённой области `pyproject.toml`
в этом задании); вынесено автору.

### Содержимое wheel (26 файлов)

* `docs/`, `tests/`, `*.bak`, `__pycache__`, `*.pyc`: нет.
* `hydrometrics-0.1.0.dist-info/licenses/LICENSE`: есть.
* `METADATA`: поле `Description-Content-Type: text/markdown`, текст README включён (`pip install` в описании),
  `Requires-Python: >=3.10`, `Requires-Dist: numpy>=1.24`, extras pandas/polars/xarray/scipy/all/test/dev/docs/crosscheck.
* `hydrometrics/py.typed`: есть.

### Содержимое sdist (64 файла)

* `LICENSE`, `README.md`, `pyproject.toml`, `hydrometrics/`, `tests/` (26 файлов, включая `tests/crosscheck`),
  `hydrometrics/py.typed`: есть.
* `docs/`, `__pycache__`, `*.bak`, `*.pyc`: нет.
* `MANIFEST.in` не потребовался.

### py.typed

Публичные сигнатуры аннотированы (выборка: `metrics/hydro.py::nse`, `core/dispatch.py::get_backend_type`,
`core/grouping.py::compute_grouped`, `core/validation.py::check_choice`), поэтому добавлен пустой
`hydrometrics/py.typed` и в `pyproject.toml`:

```
[tool.setuptools.package-data]
hydrometrics = ["py.typed"]
```

Оговорка: публичные функции `hm.nse` и др. создаются диспетчером во время импорта, поэтому статические
анализаторы увидят их тип как у фабрики; рефакторинг типов не проводился.

После сборки в корне репозитория удалён `hydrometrics.egg-info` (`build/` и `dist/` не создавались, `--outdir` вне
репозитория). `.gitignore` уже содержит `*.egg-info/`; строки `build/` и `dist/` добавлять не потребовалось,
так как сборка идёт в `--outdir` (при желании их можно добавить).

## 4. Чистые окружения (E4)

Каждое окружение: новый `uv venv --python 3.12`, установка собранного wheel. Тесты запускались
исполняемым файлом `pytest.exe` из корня репозитория (текущий каталог не попадает в `sys.path`), плагин `-p hmcheck`
печатал `hydrometrics.__file__` и `__version__`: во всех случаях путь `...\<venv>\Lib\site-packages\hydrometrics\__init__.py`,
то есть тесты импортируют УСТАНОВЛЕННЫЙ wheel. Тесты, которые читают исходники репозитория по пути
(`test_packaging.py`, `test_optional_dependencies.py`), по построению работают с деревом исходников.

### (a) wheel + numpy

`pip list`: только `hydrometrics 0.1.0`, `numpy 2.5.4` (pytest 9.2.0 добавлен позже для прогона тестов); pandas, polars,
xarray, scipy отсутствуют. Скрипт проверки (`python -I`):

* `import hydrometrics` работает, `__version__ == 0.1.0`;
* `hm.nse(obs, sim)` на numpy: 0.9708571428571429, `hm.mae`: 0.25; `hm.nse([1.0, 2.0, 4.0], [1.0, 2.0, 3.0])`
  (списки) работает: 0.7857142857142857;
* `hm.compute_grouped(hm.mae, None, obs, sim, group_by={"g": [...]})` со словарём групп: `[0.133, 0.367]`;
* после этого в `sys.modules` нет pandas/polars/xarray/scipy (определение типа входа ничего не импортирует);
* `hm.spearman_r` бросает `ImportError: spearman_r and kendall_tau need scipy; install it with `pip install scipy` or `pip install hydrometrics[scipy]``.

Набор тестов: 1279 passed, 1527 skipped, 0 failed.

### (b) wheel с одним extra

| Extra | Установлено | passed | skipped | failed |
|---|---|---|---|---|
| `[pandas]` | numpy, pandas 3.1.1 | 1696 | 1110 | 0 |
| `[polars]` | numpy, polars 2.1.0 | 1693 | 1113 | 0 |
| `[xarray]` | numpy, pandas 3.1.1 (зависимость xarray), xarray 2026.9.0 | 2188 | 618 | 0 |
| `[scipy]` | numpy, scipy 1.18.1 | 1325 | 1481 | 0 |

### (c) `[all,test]`

pandas 3.1.1, polars 2.1.0, xarray 2026.9.0, scipy 1.18.1, pytest 9.2.0, pytest-cov 7.1.0:
2844 passed, 44 skipped (sphinx), 0 failed.

### Изменения в тестах для (b)

* `tests/_cases.py`: pandas/polars/xarray больше не импортируются на уровне модуля; `wrap()` вызывает
  `pytest.importorskip` для нужного бэкенда, `values()` не требует xarray. Все параметризованные по `BACKENDS`
  тесты пропускаются по отдельности.
* `tests/conftest.py` (новый): если scipy не установлен, пропускаются только параметризованные тесты, в
  параметрах которых есть `spearman_r` или `kendall_tau`.
* `tests/test_align.py`, `test_core_objects.py`, `test_core_helpers.py`: модуль целиком пропускается без
  pandas, polars или xarray (`importorskip` после импортов).
* `tests/test_kge.py`, `test_task4.py`, `test_release_a.py`, `test_backends.py`: `importorskip` внутри тех тестов,
  где используется конкретный бэкенд; цикл `for backend in BACKENDS` в
  `test_shape_mismatch_message_is_the_same_on_every_backend` превращён в `parametrize` (те же проверки).
* `tests/test_optional_dependencies.py`: `importorskip(present)`, окружение подпроцесса из `os.environ`.
* `tests/test_packaging.py` и `tests/test_axis.py`/`test_exceptions.py`: см. раздел 1.

Утверждения нигде не ослаблялись.

## 5. Версия (E5)

Источник версии: `importlib.metadata.version("hydrometrics")` в `hydrometrics/__init__.py`. Для установленного
wheel `hydrometrics.__version__ == "0.1.0"`, в `pyproject.toml` `version = "0.1.0"`; совпадает.
Тест `test_version_comes_from_the_package_metadata_and_matches_pyproject` проходит во всех окружениях.

## 6. Сборка документации в среде, похожей на Read the Docs (E7)

`.readthedocs.yaml`: `build.os: ubuntu-24.04`, `python: "3.13"`, `pip install .` с extras `docs`,
`sphinx.configuration: docs/conf.py`, `fail_on_warning: true`. Makefile `html-ru` и `html-en` не запускают
`gen_ref.py` (его вызывает только `docs/_dev/gen/build_docs.ps1`), поэтому он не запускался.

Окружение: `uv venv --python 3.13`, `uv pip install "<копия репозитория>[docs]"` (sphinx 9.2.0 и остальные пины).
Команды (как в Makefile, без `-q`, вывод в scratch-каталог):

```
python -m sphinx -b html -D language=ru -W --keep-going docs <scratch>\docs_out\ru
python -m sphinx -b html -D language=en -W --keep-going docs <scratch>\docs_out\en
```

Результат: оба раза `build succeeded`, код выхода 0, 0 строк WARNING/ERROR. Intersphinx загрузился без таймаутов,
повторов не потребовалось. Sphinx-Gallery выполнил 0 из 0 файлов (`/plot_`-примеров нет). Это не заменяет сборку
на самом Read the Docs. Сборка могла читать файлы документации, которые параллельно правит другая сессия.

## 7. Что не удалось сделать или проверить

* Сборка на Read the Docs и запуск GitHub Actions (локально невозможно).
* Python 3.9 не проверялся намеренно (ниже `requires-python`); 3.10 с последними зависимостями не прогонялся.
* Нижние границы не искались ниже заявленных (все заявленные минимумы проходят).
* Кросс-проверка (`tests/crosscheck`) в этом задании не запускалась.
* Миграция на SPDX-лицензию (`license = "MIT"`, `setuptools>=77`) не выполнена (предупреждение setuptools).
* Подпроцессные тесты `test_optional_dependencies.py` используют дерево исходников через `PYTHONPATH`, а не установленный
  wheel; для wheel те же сценарии проверены вручную в разделе 4(a).
* Команда `git` не использовалась; состояние индекса не проверялось.
