@echo off
rem Сборка документации на Windows. Требуется: pip install -e .[docs]
setlocal
if "%PYTHON%"=="" set PYTHON=python
set SPHINX=%PYTHON% -m sphinx
set OPTS=-W --keep-going -q
set DOCS=docs
set BUILD=docs\_build

if "%1"=="html" goto html
if "%1"=="html-ru" goto html_ru
if "%1"=="html-en" goto html_en
if "%1"=="gettext" goto gettext
if "%1"=="doctest" goto doctest
if "%1"=="linkcheck" goto linkcheck
if "%1"=="check" goto check
if "%1"=="clean" goto clean
echo Цели: html html-ru html-en gettext doctest linkcheck check clean
goto end

:html
%SPHINX% -b html -D language=ru %OPTS% %DOCS% %BUILD%\html\ru || exit /b 1
%SPHINX% -b html -D language=en %OPTS% %DOCS% %BUILD%\html\en || exit /b 1
goto end
:html_ru
%SPHINX% -b html -D language=ru %OPTS% %DOCS% %BUILD%\html\ru || exit /b 1
goto end
:html_en
%SPHINX% -b html -D language=en %OPTS% %DOCS% %BUILD%\html\en || exit /b 1
goto end
:gettext
%SPHINX% -b gettext -q %DOCS% %BUILD%\gettext || exit /b 1
sphinx-intl update -p %BUILD%\gettext -d %DOCS%\locale -l en || exit /b 1
goto end
:doctest
%SPHINX% -b doctest -D language=ru -q %DOCS% %BUILD%\doctest\ru || exit /b 1
%SPHINX% -b doctest -D language=en -q %DOCS% %BUILD%\doctest\en || exit /b 1
goto end
:linkcheck
%SPHINX% -b linkcheck -q %DOCS% %BUILD%\linkcheck || exit /b 1
goto end
:check
%PYTHON% %DOCS%\_dev\check_translations.py || exit /b 1
%PYTHON% %DOCS%\_dev\check_metric_pages.py || exit /b 1
%PYTHON% %DOCS%\_dev\formula_checks.py || exit /b 1
goto end
:clean
%PYTHON% -c "import shutil; [shutil.rmtree(p, True) for p in (r'docs\_build', r'docs\api\generated', r'docs\auto_examples')]"
goto end
:end
endlocal
