# Petracore Django Starter

A batteries-included starter for Django + Django REST Framework projects.
It ships with a clean architecture, an opinionated core app, an app scaffolder (startapp_plus), and a messaging module you can import in any project.

TL;DR
* 	petracore_django new — create a Django project in the current directory, core + user apps included automatically.
* 	python manage.py startapp_plus <app_name> — generate a full CRUD app (models, services, serializers, views, urls) with consistent stubs.
* 	from petracore_django.messaging import MessagingService — import messaging; configure RESEND Variables in settings.py.




# Table of Contents
1. Why this exists (General Provisions & Benefits)
2. Installation
3. Quick Start
4. What gets generated
5. Core app features
6. URL auto-discovery
7. Service layer
8. Shared model base & serializers
9. App scaffolder: startapp_plus
10. Usage
11. Field specification format
12. Benefits
13. Messaging service
14. Importing & basic usage
15. Settings you must provide
16. Troubleshooting
17. Requirements
18. License

⸻

### Why this exists (General Provisions & Benefits)

Petracore Django Starter gives you a repeatable project skeleton that:
1. Keeps your apps consistent: each new app gets models → services → serializers → views → urls in one go.
2. Encourages a clean service layer so business logic doesn’t leak into views/serializers.
3. Wires a core URL aggregator so any local app with a urls.py is automatically available under your API prefix.
4. Exposes a messaging module you can import anywhere (email/SMS), with a simple settings-based configuration.
5. Works great for teams: predictable structure, fewer bikeshed debates, and faster onboarding.


⸻

### Installation

into your virtualenv

`pip install petracore-django-starter`

This installs:
1. 	The CLI command: petracore_django
2. 	The Python package: petracore_django (templates + scaffolder + messaging)



⸻

### Quick Start


`mkdir my_api && cd my_api`

`python3 -m venv .venv`

`source .venv/bin/activate`

`petracore_django new --name myproject`            

--name defaults to current folder name if omitted


~~~
python manage.py makemigrations
python manage.py migrate
python manage.py runserver`
~~~

You’ll now have:
1. 	core/ (the opinionated core app, including startapp_plus)
2. 	user/ (a simple custom user app wired as AUTH_USER_MODEL, serilizers, views and urls)
3. 	Your project settings.py patched with:
4. 	INSTALLED_APPS += ["core", "user", "rest_framework"]
5. 	AUTH_USER_MODEL = "user.User"
6. 	Your project urls.py patched with:

`path("api/v1/", include("core.urls")),`



##### Any local app that declares a urls.py is automatically included under /api/v1/.

⸻

### What gets generated

~~~
.
├─ manage.py
├─ myproject/                     # your Django settings/urls
│  ├─ settings.py
│  └─ urls.py
├─ core/
│  ├─ urls.py                     # auto-aggregates app urls
│  ├─ base_service.py             # Repository.create_service(...)
│  ├─ models.py                   # CreatedModified base
│  ├─ serializers.py              # basic shared serializers
│  └─ management/commands/
│     └─ startapp_plus.py         # app scaffolder
└─ user/
   ├─ models.py                   # custom User
   ├─ serializers.py
   ├─ services.py
   ├─ views.py
   └─ urls.py

~~~

<br>

### Core app features


**URL auto-discovery**

core/urls.py automatically includes every local app (under your project folder) that exposes a urls.py.
Mounting a single line in your main urls.py…

#### myproject/urls.py
~~~
from django.urls import include, path

urlpatterns = [
    path("api/v1/", include("core.urls")),  # one line to rule them all
]
~~~

…makes all app routes available under /api/v1/… with zero extra wiring.

It skips third-party apps and core itself, so you don’t get recursion or noise.

Service layer

core/base_service.py exposes a small Repository helper you can use to generate base services for your models:

~~~
from core.base_service import Repository
from .models import Thing

BaseThingService = Repository.create_service(Thing)

class ThingService(BaseThingService):
    # Put your domain logic here (hooks, guards, events, etc.)
    pass
~~~

Views call the service (not .objects) so your logic stays centralized.

Shared model base & serializers <br>
1. 	core.models.CreatedModified gives you date_created / date_modified on all models.
2. 	core.serializers includes a couple of basic response serializers for consistency.

⸻

### App scaffolder: startapp_plus

A management command that creates a full app with stubs matching the pragmatic style.

#### Usage

##### basic: derive model name from app name (drop trailing 's')
`python manage.py startapp_plus reports`

<br>

##### explicit model name
`python manage.py startapp_plus invoices --model Invoice`

<br>

##### add initial fields (CSV "name:FieldType(args)")
````
python manage.py startapp_plus tickets \
  --model Ticket \
  --fields "title:CharField(max_length=200),is_open:BooleanField(default=True)"
````
<br>

##### overwrite generated files if they exist
`python manage.py startapp_plus notes --force`

It generates:
1. 	models.py (subclassing CreatedModified, ordered by -date_created)
2. 	services.py (using Repository.create_service(Model) + a concrete ModelService)
3. 	serializers.py (a ModelSerializer + an input CreateUpdate<Model>Serializer)
4. 	views.py (DRF ModelViewSet wired to the service; separate input/output serializers)
5. 	urls.py (DRF router registering <model_name.lower()>s)

<br>
Once generated, the routes appear automatically under /api/v1/… thanks to core/urls.py.

Field specification format
<br>
`--fields` expects a CSV of name:FieldType(args) where FieldType is a Django model field.
Examples:
1. 	title:CharField(max_length=200)
2. 	is_done:BooleanField(default=False)

<br>


**Tip: If a field RHS doesn’t start with models., it will be added for you.**

Benefits
1. 	Consistency (every app looks the same)
2. 	Speed (CRUD scaffolds in seconds)
3. 	Clean layering (service layer by default)
4. 	Zero URL plumbing (core URL aggregator)

⸻

### Messaging service

A thin, importable messaging layer that you can use across apps. It supports email out of the box (via Resend), with SMS extensibility.

**Importing & basic usage**

#####  import the default classes
``````
`from petracore_django.messaging import MessagingService`

MessagingService.send_text(recipients=["09123456789"], message="hellow world")
MessagingService.send_email(recipients=["test@gmail.com"], message="Hellow world", subject="subject")
MessagingService.send_push(recipients=["3003030303"], message="the push message", subject="subject")
``````


The module defers reading django.conf.settings until runtime, so it plays nicely with Django initialization and static linters.

Settings you must provide

Email (Resend)

Add this to your settings.py:

##### Required
~~~
RESEND_API_KEY = os.getenv("RESEND_API_KEY")
RESEND_BASE_URL = os.getenv("RESEND_BASE_URL")
RESEND_SENDER_ID = os.getenv("RESEND_SENDER_ID")
~~~


⸻

### Troubleshooting

	“Unknown command: startapp_plus”
Ensure:
1. 	core is in INSTALLED_APPS
2. 	the file exists at core/management/commands/startapp_plus.py
3. 	both management/ and commands/ have __init__.py
4. 	“Templates missing” error before scaffolding

The CLI does a preflight check and will tell you which files are missing if your installation didn’t include package data. If you’re hacking locally, do:

`pip install -e /ABS/PATH/TO/petracore_django_starter`

**Django won’t startproject in non-empty director”**

petracore_django new runs django-admin startproject <name> . — run it inside an empty folder, or initialize your own project and re-run to only add scaffolding.

⸻

### Requirements

	•	Python 3.10+
	•	Django 4.2+
	•	Django REST Framework 3.15+

Runtime dependencies installed for you:

Django, djangorestframework, PyJWT, requests


⸻

License

MIT — do whatever you want, just keep the license and acknowledge the authors. 🙌

⸻

One more thing 

If you have a specific house style (lint/format/testing, CI, Docker, Celery, Postgres, etc.), this starter is intentionally small and composable—extend the templates to fit your team, and the scaffolder will keep every new app on-rails.

Made with Love by Petracore 💚.