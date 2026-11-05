param([string]$Python = "python", [switch]$Html, [switch]$Doctest)
# Regenerate the reference pages, refresh the .po catalogs and (optionally) build and test both languages.
$root = (Resolve-Path "$PSScriptRoot\..\..\..").Path
$env:PYTHONUTF8 = "1"; $env:PYTHONIOENCODING = "utf-8"; $env:PYTHONDONTWRITEBYTECODE = "1"
$env:PYTHONPATH = "$root;$root\docs\_dev\gen;$root\docs\_dev"
Set-Location $root
& $Python "$root\docs\_dev\gen\gen_ref.py"; if ($LASTEXITCODE) { exit 1 }
& $Python -m sphinx -b gettext -q docs docs\_build\gettext
& $Python -m sphinx_intl update -p docs\_build\gettext -d docs\locale -l en
& $Python "$root\docs\_dev\gen\fill_po.py"
if ($Html) { foreach ($l in "ru", "en") { & $Python -m sphinx -b html -D language=$l -W --keep-going -q docs "docs\_build\html\$l"; "html $l exit: $LASTEXITCODE" } }
if ($Doctest) { foreach ($l in "ru", "en") { & $Python -m sphinx -b doctest -D language=$l -q docs "docs\_build\doctest\$l"; "doctest $l exit: $LASTEXITCODE" } }
