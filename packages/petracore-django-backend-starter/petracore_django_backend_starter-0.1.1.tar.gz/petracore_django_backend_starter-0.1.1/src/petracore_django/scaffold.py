from __future__ import annotations
import re
from pathlib import Path

def _write(path: Path, content: str, *, exist_ok: bool = False):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not exist_ok:
        return
    path.write_text(content, encoding="utf-8")

def _append_installed_apps(settings_txt: str, apps: list[str]) -> str:
    """Append missing apps to INSTALLED_APPS, fixing comma placement.

    - Does not touch existing entries.
    - Adds a leading comma *only* if the existing block's last non-whitespace
      character is not already a comma and the block is non-empty.
    - Always commas after each newly-added app (trailing comma OK in Python lists).
    """
    m = re.search(r"INSTALLED_APPS\s*=\s*\[(.*?)\]", settings_txt, flags=re.S | re.M)
    if not m:
        return settings_txt

    block = m.group(1)

    # Determine which apps are missing
    missing = [a for a in apps if re.search(rf"['\"]{re.escape(a)}['\"]", block) is None]
    if not missing:
        return settings_txt

    # Determine if a comma is needed before inserting the first new app
    block_rstrip = block.rstrip()
    trimmed = block_rstrip.rstrip()
    needs_leading_comma = bool(trimmed and not trimmed.endswith(','))

    insertion = (',' if needs_leading_comma else '') + ''.join(f"\n    '{a}'," for a in missing)

    new_block = block_rstrip + insertion
    return settings_txt[:m.start(1)] + new_block + settings_txt[m.end(1):]

def _ensure_middleware(settings_txt: str) -> str:
    """Ensure auth middleware is present and add a REST_FRAMEWORK block if missing."""
    # --- Ensure AuthenticationMiddleware inside MIDDLEWARE (list or tuple)
    m = re.search(r"MIDDLEWARE\s*=\s*\[(.*?)\]", settings_txt, flags=re.S | re.M)
    paren = False
    if not m:
        m = re.search(r"MIDDLEWARE\s*=\s*\((.*?)\)", settings_txt, flags=re.S | re.M)
        paren = bool(m)
    if m:
        block = m.group(1)
        if re.search(r"['\"]django\.contrib\.auth\.middleware\.AuthenticationMiddleware['\"]", block) is None:
            block_rstrip = block.rstrip()
            trimmed = block_rstrip.rstrip()
            needs_leading_comma = bool(trimmed and not trimmed.endswith(','))
            insertion = (',' if needs_leading_comma else '') + "\n    'django.contrib.auth.middleware.AuthenticationMiddleware',"
            new_block = block_rstrip + insertion
            settings_txt = settings_txt[:m.start(1)] + new_block + settings_txt[m.end(1):]

    # --- Ensure REST_FRAMEWORK config exists
    if re.search(r"\bREST_FRAMEWORK\s*=", settings_txt) is None:
        rf_block = (
            "\nREST_FRAMEWORK = {\n"
            "    'DEFAULT_AUTHENTICATION_CLASSES': [\n"
            "        'core.custom_authentication.CustomUserJWTAuthentication',\n"
            "    ],\n\n"
            "    'DEFAULT_PARSER_CLASSES': ['rest_framework.parsers.JSONParser'],\n\n"
            "    # 'DEFAULT_PERMISSION_CLASSES': [\n"
            "    #     'rest_framework.permissions.IsAuthenticated',\n"
            "    #     # 'rest_framework.permissions.IsAdminUser',\n"
            "    # ]\n"
            "}\n"
        )
        if not settings_txt.endswith('\n'):
            settings_txt += '\n'
        settings_txt += rf_block

    return settings_txt

def _set_auth_user_model(settings_txt: str, app_label_model: str) -> str:
    if "AUTH_USER_MODEL" not in settings_txt:
        settings_txt += f"\nAUTH_USER_MODEL = '{app_label_model}'\n"
    return settings_txt

def _include_urls(urls_txt: str, pattern_stmt: str) -> str:
    """Ensure urls.py imports include/path and contains the given pattern.

    - If there's no `from django.urls import ...`, insert `from django.urls import include, path`.
    - If imports exist but are missing either `include` or `path`, *add separate import lines* without
      rewriting existing ones (safe for multiline/parenthesized imports).
    - Prepend the `pattern_stmt` into `urlpatterns` if it's not already present.
    """
    def _has_import(name: str) -> bool:
        # True if any 'from django.urls import ...' line (single or multi-line) includes the name
        pattern_single = rf"^from\s+django\.urls\s+import\s+.*\b{name}\b"
        pattern_multi = rf"from\s+django\.urls\s+import\s*\((?:.|\n)*?\b{name}\b(?:.|\n)*?\)"
        return bool(re.search(pattern_single, urls_txt, flags=re.M)) or bool(re.search(pattern_multi, urls_txt, flags=re.S))

    def _insert_after_anchor(text: str, addition: str) -> str:
        # Prefer inserting after admin import if present, else at top
        anchor = "from django.contrib import admin"
        if anchor in text:
            idx = text.find(anchor)
            endline = text.find("\n", idx)
            if endline == -1:
                endline = idx + len(anchor)
            return text[: endline + 1] + addition + ("" if addition.endswith("\n") else "\n") + text[endline + 1 :]
        else:
            return addition + ("" if addition.endswith("\n") else "\n") + text

    # Ensure import line exists and includes both include and path
    if "from django.urls import" not in urls_txt:
        addition = "from django.urls import include, path\n"
        urls_txt = _insert_after_anchor(urls_txt, addition)
    else:
        missing: list[str] = []
        if not _has_import("include"):
            missing.append("from django.urls import include\n")
        if not _has_import("path"):
            missing.append("from django.urls import path\n")
        if missing:
            urls_txt = _insert_after_anchor(urls_txt, "".join(missing))

    # Ensure pattern is present inside urlpatterns
    if pattern_stmt not in urls_txt:
        urls_txt = urls_txt.replace(
            "urlpatterns = [",
            "urlpatterns = [\n    " + pattern_stmt + ","
        )

    return urls_txt

def _tpl(name: str) -> str:
    here = Path(__file__).parent / "templates" / name
    return here.read_text(encoding="utf-8")


def _render_project_readme_from_template(project_name: str) -> str:
    """Load README content from templates/project_readme.md.tmpl and substitute the project name.
    Falls back to a minimal message if the template is missing.
    """
    try:
        template = _tpl("project_readme.md.tmpl")
        return template.replace("{{PROJECT_NAME}}", project_name)
    except FileNotFoundError:
        return (
            "# BACKEND DOCUMENTATION\n\n"
            "*This project was created by **petracore-django-backend-starter***.\n\n"
            f"This is the {project_name} backend. It is a [Django](https://www.djangoproject.com/) project.\n"
        )


def _write_readme_md(project_dir: Path, project_name: str) -> None:
    """Create README.md next to manage.py if it doesn't already exist (idempotent)."""
    readme_path = project_dir / "README.md"
    if readme_path.exists():
        return
    readme_path.write_text(_render_project_readme_from_template(project_name), encoding="utf-8")


def create_project_with_core_and_user(project_dir: Path):
    """
    project_dir/
      manage.py
      <project_name>/
        settings.py   <-- we patch
        urls.py       <-- we patch
    We add apps under project_dir/
    """
    project_pkg = next((p for p in project_dir.iterdir() if (p / "settings.py").exists()), None)
    assert project_pkg, "Could not locate project package (missing settings.py)."

    # --- Create core app with base_service, models, serializers, management/commands/startapp_plus.py
    core_dir = project_dir / "core"
    _write(core_dir / "__init__.py", "", exist_ok=True)
    _write(core_dir / "apps.py", "from django.apps import AppConfig\n\nclass CoreConfig(AppConfig):\n    name = 'core'\n")
    _write(core_dir / "utils.py", _tpl("core_utils.py.tmpl"))
    _write(core_dir / "custom_authentication.py", _tpl("core_custom_authentication.py.tmpl"))
    _write(core_dir / "exceptions.py", _tpl("core_exceptions.py.tmpl"))
    _write(core_dir / "models.py", _tpl("core_models.py.tmpl"))
    _write(core_dir / "serializers.py", _tpl("core_serializers.py.tmpl"))
    _write(core_dir / "urls.py", _tpl("core_urls.py.tmpl"))
    mgmt = core_dir / "management" / "commands"
    _write(mgmt / "__init__.py", "", exist_ok=True)
    _write(mgmt.parent / "__init__.py", "", exist_ok=True)
    _write(mgmt / "startapp_plus.py", _tpl("startapp_plus.py.tmpl"))
    _write(core_dir / "base_service.py", _tpl("core_base_service.py.tmpl"))

    # --- Create user app
    user_dir = project_dir / "user"
    _write(user_dir / "__init__.py", "", exist_ok=True)
    _write(user_dir / "apps.py", "from django.apps import AppConfig\n\nclass UserConfig(AppConfig):\n    default_auto_field = 'django.db.models.BigAutoField'\n    name = 'user'\n")
    _write(user_dir / "models.py", _tpl("user_models.py.tmpl"))
    _write(user_dir / "services.py", _tpl("user_services.py.tmpl"))
    _write(user_dir / "serializers.py", _tpl("user_serializers.py.tmpl"))
    _write(user_dir / "views.py", _tpl("user_views.py.tmpl"))
    _write(user_dir / "urls.py", _tpl("user_urls.py.tmpl"))

    # --- Patch settings.py
    settings_path = project_pkg / "settings.py"
    settings_txt = settings_path.read_text(encoding="utf-8")
    settings_txt = _append_installed_apps(settings_txt, ["core", "user", "rest_framework"])
    settings_txt = _set_auth_user_model(settings_txt, "user.User")
    settings_txt = _ensure_middleware(settings_txt)
    settings_path.write_text(settings_txt, encoding="utf-8")

    # --- Patch urls.py to include core aggregate endpoints
    urls_path = project_pkg / "urls.py"
    urls_txt = urls_path.read_text(encoding="utf-8")
    urls_txt = _include_urls(
        urls_txt,
        pattern_stmt="path('api/v1/', include('core.urls'))"
    )
    urls_path.write_text(urls_txt, encoding="utf-8")


    _write_readme_md(project_dir, project_pkg.name)