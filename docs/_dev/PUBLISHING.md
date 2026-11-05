# Публикация: GitHub, Read the Docs, PyPI

Порядок действий для первого выпуска `hydrometrics` 0.1.0, от локальной папки до `pip install hydrometrics`.
Команды рассчитаны на PowerShell и выполняются из корня проекта.

Шаги идут в таком порядке не случайно: документация на Read the Docs собирается из GitHub, а описание пакета на PyPI берётся
из `README.md` в момент сборки и после загрузки не меняется до следующей версии.

## Что проверено на 2026-11-05

| Проверка | Результат |
|---|---|
| Имя `hydrometrics` на PyPI и TestPyPI | свободно; похожие `hydro-metrics`, `hydro_metrics`, `hydrometric` тоже свободны. Окончательный ответ PyPI даст только при первой загрузке |
| Репозиторий `github.com/SergeyIglin/hydrometrics` | не существует, аккаунт `SergeyIglin` существует |
| Адрес `hydrometrics.readthedocs.io` | свободен |
| Документация из чистой копии репозитория, ru и en, `-W --keep-going` | без предупреждений |
| Сборка sdist и колеса из чистой копии, `twine check`, классификаторы | проходят |
| Поиск токенов и паролей в файлах репозитория | ничего не найдено; проверено текущее состояние файлов, не вся история |

Не проверялись и могут дать сюрпризы при первом запуске: GitHub Actions, сборка на самом Read the Docs, загрузка на PyPI.

## Что понадобится

- [Git для Windows](https://git-scm.com/download/win): сейчас в системе `git` нет, история велась библиотекой dulwich.
  Обычный `git` работает с этим репозиторием.
- Аккаунты: GitHub, [pypi.org](https://pypi.org/account/register/), [test.pypi.org](https://test.pypi.org/account/register/)
  (отдельная регистрация), [readthedocs.org](https://readthedocs.org/) (удобно войти через GitHub). На PyPI и TestPyPI нужна
  двухфакторная аутентификация.

Если репозиторий будет не в аккаунте `SergeyIglin` или адрес на Read the Docs окажется другим, исправьте ссылки в
`pyproject.toml` (`[project.urls]`) и `README.md` до шага 4.5: метаданные выпущенной версии изменить нельзя.

## Шаг 1. Подготовить репозиторий

### 1.1. Настроить git

Настройка `core.autocrlf` нужна, иначе Git для Windows может показать все файлы изменёнными из-за окончаний строк.

```powershell
git config core.autocrlf false
git config user.name "Ваше имя"
git config user.email "адрес@example.com"
git status
```

`git status` должен показать чистое дерево на ветке `fix/inventory-report`. Адрес из `user.email` будет виден в истории
публично; у GitHub есть скрытый адрес вида `...@users.noreply.github.com` (*Settings → Emails*).

### 1.2. Убрать внутренние файлы

В репозитории лежат ваши задания: `Task.txt`, `task_2.txt` … `task_5.txt`. Для публикации они не нужны. Команда уберёт их
из git и оставит на диске.

```powershell
git rm --cached Task.txt task_2.txt task_3.txt task_4.txt task_5.txt
Add-Content .gitignore "`n# internal task notes`n/Task.txt`n/task_*.txt"
git add .gitignore
git commit -m "chore: remove internal task notes from the repository"
```

Каталог `docs/_dev/` (отчёты, генератор страниц) и `docs/_legacy/` останутся в репозитории, но в колесо не попадают. Без
`docs/_dev/gen/` страницы документации перегенерировать нельзя, поэтому удалять его не стоит.

### 1.3. Обновить тексты

Эти правки нужны до сборки: сейчас текст говорит, что пакет на PyPI не публиковался, и это попало бы на страницу пакета.

1. `README.md`, раздел *Installation*: команда `pip install hydrometrics`, убрать фразу *Publication on PyPI has not been
   checked...*.
2. `README.md`, раздел *Documentation*: убрать фразу *The address is a placeholder...*.
3. `docs/_dev/gen/userguide_pages2.py`, функция `quickstart`: заменить установку из каталога на `pip install hydrometrics` и
   убрать фразу про PyPI в обоих языках.
4. `CHANGELOG.md`: переименовать `## Unreleased (ветка ...)` в `## 0.1.0 (дата выпуска)`.

После правки генератора пересоберите страницы и закоммитьте:

```powershell
py -m pip install -e ".[docs]"
powershell -NoProfile -File docs\_dev\gen\build_docs.ps1 -Python py -Html -Doctest
git add -A
git commit -m "docs: prepare 0.1.0 release notes and installation text"
```

В выводе должно быть `html ru exit: 0` и `html en exit: 0`.

### 1.4. Выбрать историю и назвать ветку `main`

CI и Read the Docs рассчитаны на ветку `main`. Сейчас есть `master` (один начальный коммит) и `fix/inventory-report` (вся
работа). Выберите один вариант.

**Вариант А: сохранить историю.** Видны все коммиты, их автор указан как `Claude Code`. Файлы заданий останутся доступны в
старых коммитах, шаг 1.2 скрывает их только из текущего состояния.

```powershell
git branch -M main
git branch -d master
```

**Вариант Б: начать с одного коммита.** Подходит, если задания и рабочая история не должны быть публичными. Сначала сделайте
копию всей папки проекта: старая история останется только в ней.

```powershell
git checkout --orphan new-main
git add -A
git commit -m "Initial public release"
git branch -M main
git branch -D fix/inventory-report master
```

## Шаг 2. GitHub

1. На [github.com/new](https://github.com/new) создайте репозиторий `hydrometrics`, Public, **без** README, `.gitignore` и
   лицензии: они уже есть.
2. Отправьте код. При первом запросе откроется вход через браузер.

   ```powershell
   git remote add origin https://github.com/SergeyIglin/hydrometrics.git
   git push -u origin main
   ```

3. Откройте вкладку *Actions*: push запускает `tests.yml`. Дождитесь зелёного статуса всех job'ов: `test`, `crosscheck`, `docs`,
   `package`. Если вкладка просит разрешить workflows, разрешите.
4. Если что-то упало, исправляйте до шага 3. Это первый запуск CI, ошибки на Linux и macOS здесь возможны: локально всё
   проверялось только на Windows.

## Шаг 3. Read the Docs

Основным будет русский проект, английский подключается к нему как перевод. Названия разделов ниже взяты из документации Read
the Docs, расположение пунктов в интерфейсе может отличаться.

1. Войдите на readthedocs.org и импортируйте `SergeyIglin/hydrometrics` как проект `hydrometrics`. В поле *Language* выберите
   **Russian**.
2. Дождитесь сборки `latest`. Проверьте `https://hydrometrics.readthedocs.io/ru/latest/`.
3. Импортируйте тот же репозиторий ещё раз как проект `hydrometrics-en`, *Language*: **English**.
4. В проекте `hydrometrics` откройте страницу *Translations* и добавьте `hydrometrics-en`.
5. Проверьте `https://hydrometrics.readthedocs.io/en/latest/`. В логе сборки английского проекта должно быть
   `-D language=en`: язык задаётся настройкой проекта, а в `docs/conf.py` по умолчанию стоит `ru`. В документации Read the
   Docs этот механизм не описан, поэтому проверить его нужно по логу. Если в логе `ru`, сообщите мне: потребуется правка
   конфигурации.

Что посмотреть глазами после сборки: `docs/_dev/RTD_CHECKLIST.md`, раздел «Проверить глазами».

## Шаг 4. PyPI

Публикация идёт через доверенную публикацию: GitHub Actions подтверждает себя перед PyPI, токены в репозитории не хранятся.
Файл `.github/workflows/release.yml` уже настроен.

### 4.1. Пробная загрузка на TestPyPI

Необязательно, но это единственный способ увидеть страницу пакета и проверить установку до настоящего выпуска. Версию на PyPI
нельзя загрузить повторно, даже удалив её, поэтому ошибку лучше поймать здесь.

1. Создайте токен на [test.pypi.org/manage/account/#api-tokens](https://test.pypi.org/manage/account/#api-tokens), область
   *Entire account*.
2. Соберите пакет и загрузите. На запрос токена вставьте его целиком, с префиксом `pypi-`; ввод не отображается.

   ```powershell
   py -m pip install --upgrade build twine
   Remove-Item -Recurse -Force dist -ErrorAction SilentlyContinue
   py -m build
   py -m twine check dist/*
   py -m twine upload --repository testpypi dist/*
   ```

3. Проверьте установку в чистом окружении. `--no-deps` нужен, потому что на TestPyPI может не быть подходящего numpy.

   ```powershell
   $check = "$env:TEMP\check_test"
   py -m venv $check
   & "$check\Scripts\python" -m pip install numpy
   & "$check\Scripts\python" -m pip install --index-url https://test.pypi.org/simple/ --no-deps hydrometrics
   Push-Location $env:TEMP
   & "$check\Scripts\python" -c "import numpy as np, hydrometrics as hm; print(hm.__version__, hm.__file__); print(float(hm.nse(np.array([1.,2.,3.]), np.array([1.1,1.9,3.2]))))"
   Pop-Location
   Remove-Item -Recurse -Force $check
   ```

4. Посмотрите страницу [test.pypi.org/project/hydrometrics](https://test.pypi.org/project/hydrometrics/): описание, ссылки,
   классификаторы.

Чтобы загрузить на TestPyPI ещё раз, нужна другая версия, например временная `0.1.0rc2` в `pyproject.toml`. Такую правку не
коммитьте.

### 4.2. Разрешить публикацию с GitHub

На pypi.org: аккаунт → *Publishing* (раздел аккаунта, а не проекта: проекта ещё нет) → форма для GitHub. Заполните:

| Поле | Значение |
|---|---|
| PyPI project name | `hydrometrics` |
| Owner | `SergeyIglin` |
| Repository name | `hydrometrics` |
| Workflow name | `release.yml` |
| Environment name | `pypi` |

Нажмите *Add*. Запись не резервирует имя: пока пакет не опубликован, его может занять кто-то другой, и тогда запись перестанет
действовать. Поэтому не откладывайте шаг 4.4 надолго.

### 4.3. Создать окружение на GitHub

В репозитории: *Settings → Environments → New environment*, имя `pypi`. Рекомендую включить *Required reviewers* и указать
себя: публикация будет ждать вашего подтверждения.

### 4.4. Поставить тег

```powershell
git tag -a v0.1.0 -m "hydrometrics 0.1.0"
git push origin v0.1.0
```

Версия в теге должна совпадать с `version` в `pyproject.toml` (сейчас `0.1.0`).

### 4.5. Выпустить

1. На GitHub: *Releases → Draft a new release*, выберите тег `v0.1.0`, вставьте раздел `0.1.0` из `CHANGELOG.md`, нажмите
   *Publish release*.
2. Откройте *Actions*: запустится `release`. Если включено подтверждение, одобрите job `publish`.
3. После зелёного статуса пакет появится на [pypi.org/project/hydrometrics](https://pypi.org/project/hydrometrics/).

### 4.6. Проверить установку

Команды переходят во временную папку: из корня проекта Python взял бы локальную папку `hydrometrics`, а не установленный пакет.

```powershell
$check = "$env:TEMP\check_pypi"
py -m venv $check
& "$check\Scripts\python" -m pip install "hydrometrics[all]"
Push-Location $env:TEMP
& "$check\Scripts\python" -c "import numpy as np, hydrometrics as hm; print(hm.__version__, hm.__file__); print(float(hm.nse(np.array([1.,2.,3.]), np.array([1.1,1.9,3.2]))))"
Pop-Location
Remove-Item -Recurse -Force $check
```

Должны напечататься версия `0.1.0`, путь внутри `check_pypi` и число. После этого пакет доступен всем:

```
pip install hydrometrics            # только numpy
pip install "hydrometrics[pandas]"  # также [polars], [xarray], [scipy]
pip install "hydrometrics[all]"     # все бэкенды и scipy
```

### 4.7. Включить версию документации

На Read the Docs новые теги создаются неактивными. На вкладке *Versions* активируйте `v0.1.0` **в обоих проектах**.
Read the Docs также создаст версию `stable`, которая следует за последним выпуском; проверьте, что она активна, и при желании
назначьте её версией по умолчанию.

## Следующие выпуски

1. Поднимите `version` в `pyproject.toml`, заполните раздел в `CHANGELOG.md`, закоммитьте в `main`, дождитесь зелёного CI.
2. `git tag -a vX.Y.Z -m "hydrometrics X.Y.Z"`, `git push origin vX.Y.Z`.
3. *Releases → Draft a new release → Publish release*.
4. Активируйте версию на Read the Docs в обоих проектах.

Шаги 4.1–4.3 повторять не нужно.

## Если что-то пошло не так

| Симптом | Причина и действие |
|---|---|
| `git status` показывает все файлы изменёнными | не выполнен `git config core.autocrlf false` |
| `git push` отклонён, в удалённом репозитории уже есть коммиты | репозиторий создан с README или лицензией; удалите и создайте его пустым |
| Сборка на Read the Docs упала с предупреждением `intersphinx inventory ... not fetchable` | сбой сети при загрузке с внешнего сайта, а `fail_on_warning: true` превращает его в ошибку; запустите сборку ещё раз |
| Английская версия на русском языке | см. шаг 3.5 |
| `release` падает с `invalid-publisher` | значения на PyPI (шаг 4.2) не совпадают с репозиторием, файлом workflow или окружением |
| PyPI: `File already exists` | версия уже загружена, повторно её загрузить нельзя; поднимите версию и выпустите заново |
| PyPI: имя занято или слишком похоже на существующее | выберите другое имя в `pyproject.toml`; это меняет команду установки, импорт `hydrometrics` остаётся прежним |
| `pip install hydrometrics` не находит пакет сразу после выпуска | подождите несколько минут, индекс обновляется не мгновенно |
| `spearman_r` или `kendall_tau` дают `ImportError` | это ожидаемо без scipy: `pip install "hydrometrics[scipy]"` |
