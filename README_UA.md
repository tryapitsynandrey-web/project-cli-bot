# Personal Assistant CLI

![Python](https://img.shields.io/badge/Python-3.12%2B-blue)
![Architecture](https://img.shields.io/badge/Architecture-Layered-success)
![Storage](https://img.shields.io/badge/Storage-JSON-informational)
![Interface](https://img.shields.io/badge/Interface-CLI-orange)
![Validation](https://img.shields.io/badge/Validation-Strict-critical)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

Структурований консольний додаток для управління контактами й нотатками з локальним збереженням, суворою валідацією, інтелектуальними підказками команд та читабельним кольоровим інтерфейсом терміналу.

Цей проєкт розроблено як командний інженерний проєкт на Python і слідує шаруватій архітектурі з чітким розподілом між доменними моделями, бізнес-логікою, персистентністю, взаємодією CLI та спільними утилітами.

## Team

- **Andrii Triapitsyn** — <solabola@pm.me>
- **Iryna Zvirkovska** — <irene.zvirkovska@gmail.com>
- **Valeriy H** — <valeriy2006@gmail.com>
- **Oksana Levchenko** — <oksa.levchenko@gmail.com>

## Table of Contents

- [Project Goal](#project-goal)
- [Core Functionality](#core-functionality)
- [Technology Stack](#technology-stack)
- [Requirements](#requirements)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [Available Commands](#available-commands)
- [Command Aliases](#command-aliases)
- [Usage Examples](#usage-examples)
- [Data Storage](#data-storage)
- [Validation Rules](#validation-rules)
- [Project Architecture](#project-architecture)
- [Detailed Project Structure](#detailed-project-structure)
- [Design Principles](#design-principles)
- [Error Handling](#error-handling)
- [Design Principles](#design-principles)
- [Error Handling](#error-handling)
- [Залежності середовища виконання](#залежності-середовища-виконання)
- [Ліцензія проєкту](#ліцензія-проєкту)

## Project Goal

Мета проєкту — створити персонального асистента, який дозволяє користувачу:

- зберігати та керувати контактами
- зберігати та керувати нотатками
- ефективно шукати записи
- перевіряти критичні введені дані
- зберігати дані між запусками
- працювати зручніше через чистий інтерфейс командного рядка

## Core Functionality

### Contact Management

- додавати нові контакти
- перелічувати всі контакти
- шукати контакти за частковим збігом
- редагувати існуючі контакти
- видаляти контакти з підтвердженням
- зберігати кілька номерів телефону для одного контакту
- зберігати необов'язкові email, адресу, день народження, нотатку та теги
- показувати найближчі дні народження на наступні N днів
- окремо керувати тегами контактів

### Notes Management

- додавати нові нотатки
- перелічувати всі нотатки
- шукати нотатки за вмістом
- редагувати нотатки
- видаляти нотатки з підтвердженням
- додавати теги до нотаток
- шукати нотатки за одним або кількома тегами
- підтримувати режим фільтрації тегів `--any` та `--all`

### Validation

- сувора валідація імен контактів
- сувора валідація номерів телефону через `phonenumbers`
- сувора валідація email через `email-validator`
- перевірка формату дати народження `YYYY-MM-DD`
- валідація вмісту нотаток
- нормалізація та валідація тегів

### Persistence

- локальне збереження у форматі JSON
- автоматичне завантаження при запуску
- автоматичне збереження після змін
- плавний відкат при пошкодженні JSON-файлу
- створення резервних копій для пошкоджених файлів збереження

### CLI Experience

- читабельний кольоровий вивід у терміналі
- алиаси команд
- меню допомоги та детальна допомога по командах
- інтерактивні підказки для складних дій
- пропозиції при помилках у командах
- підтримка завершення команд у режимі підказок через `prompt-toolkit`, якщо він встановлений

## Technology Stack

- **Language:** Python
- **Interface:** CLI
- **Storage:** JSON
- **Validation:** `email-validator`, `phonenumbers`
- **Interactive CLI support:** `prompt-toolkit`
- **Architecture style:** layered architecture / service-oriented CLI design

## Requirements

- Python **3.12+**
- `pip`
- рекомендовано: ізольоване віртуальне середовище

## Installation

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd project-cli-bot
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
```

### 3. Activate the virtual environment

#### macOS / Linux

```bash
source .venv/bin/activate
```

#### Windows

```bash
.venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

## Running the Application

```bash
python main.py
```

Після запуску додаток відображає основне меню допомоги та запускає інтерактивний цикл команд.

## Available Commands

### Contacts

- `add-contact`
- `list-contacts`
- `search-contact <query>`
- `edit-contact <contact-name>`
- `delete-contact <contact-name>`
- `birthdays [days]`

### Contact Tags

- `add-tag`
- `edit-tag`
- `delete-tag`
- `list-tags`
- `contacts-by-tag <tag>`

### Notes

- `add-note`
- `list-notes`
- `search-notes <query>`
- `edit-note <note-id>`
- `delete-note <note-id>`
- `notes-by-tag [--any|--all] <tag1> [tag2] ...`

### System

- `help`
- `help <command>`
- `exit`
- `quit`

## Command Aliases

| Аліас | Команда |
| --- | --- |
| `h` | `help` |
| `?` | `help` |
| `q` | `quit` |
| `ac` | `add-contact` |
| `ls` | `list-contacts` |
| `sc` | `search-contact` |
| `ec` | `edit-contact` |
| `dc` | `delete-contact` |
| `bd` | `birthdays` |
| `an` | `add-note` |
| `ln` | `list-notes` |
| `sn` | `search-notes` |
| `en` | `edit-note` |
| `dn` | `delete-note` |
| `at` | `add-tag` |
| `et` | `edit-tag` |
| `dt` | `delete-tag` |
| `lt` | `list-tags` |
| `ct` | `contacts-by-tag` |
| `nbt` | `notes-by-tag` |

## Usage Examples

### Add a contact

```bash
add-contact
```

Обов'язкові поля:

- name
- принаймні один номер телефону

Необов'язкові поля:

- email
- address
- birthday
- note
- tags

### Search contacts

```bash
search-contact john
search-contact gmail
search-contact +353
```

### Show birthdays

```bash
birthdays
birthdays 30
```

### Add a note

```bash
add-note
```

### Search notes

```bash
search-notes meeting
```

### Search notes by tags

```bash
notes-by-tag work
notes-by-tag --any work personal
notes-by-tag --all urgent finance
```

### Show contacts by tag

```bash
contacts-by-tag work
```

## Data Storage

Дані додатку зберігаються локально в домашньому каталозі користувача:

```text
~/.assistant_bot/data/
```

Файли, що використовуються:

- `contacts.json`
- `notes.json`

### Storage Behavior

- дані завантажуються автоматично при запуску
- дані зберігаються автоматично після кожної модифікації
- якщо JSON-файл пошкоджений, додаток створює резервну копію та продовжує роботу безпечно
- резервні файли використовують суфікс `.backup`

## Validation Rules

### Contact Validation

#### Name

- required
- minimum 2 characters
- maximum 100 characters

#### Phone

- required
- validated through `phonenumbers`
- normalized to E.164 format

#### Email

- optional
- validated through `email-validator`
- blocked fake/test domains rejected

#### Address

- optional
- minimum 3 characters if provided
- maximum 500 characters

#### Birthday

- optional
- format: `YYYY-MM-DD`
- cannot be in the future

#### Tags

- normalized to lowercase
- deduplicated
- allowed characters: lowercase letters, digits, `_`, `-`

### Note Validation

#### Content

- required
- minimum 2 characters
- maximum 10000 characters

#### Note Tags

- optional
- normalized and validated
- duplicates removed

## Project Architecture

Проєкт дотримується шаруватої архітектури.

```text
project-cli-bot/
├── .gitattributes
├── .gitignore
├── LICENSE
├── README.md
├── requirements.txt
├── main.py
└── assistant_bot/
    ├── __init__.py
    ├── app.py
    ├── cli/
    ├── domain/
    ├── services/
    ├── storage/
    └── utils/
```

## Detailed Project Structure

### Root Files

#### `main.py`

Точка входу додатку. Створює екземпляр `PersonalAssistant` та запускає цикл CLI.

#### `requirements.txt`

Містить усі runtime-залежності, потрібні для проєкту.

#### `LICENSE`

Ліцензія MIT для проєкту.

#### `.gitignore`

Визначає файли та папки, виключені з контролю версій.

#### `.gitattributes`

Визначає нормалізацію тексту та обробку кінців рядків Git.

### `assistant_bot/`

Верхньорівневий пакет додатку.

#### `assistant_bot/__init__.py`

Файл експорту пакета.

#### `assistant_bot/app.py`

Головний оркестратор додатку.

Responsibilities:

- initialize services
- initialize storage
- initialize command handler
- build command dispatch table
- run the main CLI loop
- manage prompt session and completion support

### `assistant_bot/cli/`

Рівень CLI: парсинг введення, рендеринг виводу, текст допомоги та обробники команд.

#### `assistant_bot/cli/__init__.py`

Експортує компоненти пакета CLI.

#### `assistant_bot/cli/parser.py`

Парсить сире введення користувача в структуровані команди.

Responsibilities:

- normalize command names
- resolve aliases
- split arguments
- expose available commands and aliases
- support command completion token lists

#### `assistant_bot/cli/handlers.py`

Містить обробники для всіх команд, доступних користувачу.

Responsibilities:

- contact operations
- note operations
- tag operations
- help handling
- unknown command suggestions
- interactive input flows
- confirmation dialogs

#### `assistant_bot/cli/renderer.py`

Відповідає за форматування виводу.

Responsibilities:

- colorized terminal output
- message rendering
- contact card rendering
- note card rendering
- compact previews
- suggestion formatting

#### `assistant_bot/cli/help_text.py`

Містить визначення головного меню допомоги та детальні описи команд.

Responsibilities:

- main menu rendering
- section grouping
- command help texts
- alias mapping for help lookup

### `assistant_bot/domain/`

Ядро доменних моделей та виключень.

#### `assistant_bot/domain/__init__.py`

Експортує члени доменного пакета.

#### `assistant_bot/domain/contacts.py`

Доменна модель контакту.

Responsibilities:

- represent contact data
- validate and normalize creation data
- update contact fields safely
- manage contact tags
- convert to and from serializable dictionaries
- support text search matching

#### `assistant_bot/domain/notes.py`

Доменна модель нотатки.

Responsibilities:

- represent note data
- validate content and tags
- update note fields
- manage note tags
- serialize and deserialize notes
- support search and preview generation

#### `assistant_bot/domain/exceptions.py`

Ієрархія кастомних виключень.

Responsibilities:

- define project-specific exceptions
- separate validation, storage, and not-found errors

### `assistant_bot/services/`

Рівень бізнес-логіки.

#### `assistant_bot/services/__init__.py`

Експортує члени пакета сервісів.

#### `assistant_bot/services/contact_service.py`

Бізнес-логіка для контактів.

Responsibilities:

- create, load, update, delete contacts
- search contacts
- collect birthdays
- manage contact tags
- return sorted contact views

#### `assistant_bot/services/note_service.py`

Бізнес-логіка для нотаток.

Responsibilities:

- create, load, update, delete notes
- search notes
- filter notes by tags
- sort notes
- expose tag-based retrieval logic

#### `assistant_bot/services/birthday_service.py`

Логіка, зорієнтована на дні народження, побудована на основі контактів.

Responsibilities:

- collect upcoming birthdays
- format birthday-related output data

#### `assistant_bot/services/suggestion_service.py`

Логіка пропозицій команд.

Responsibilities:

- provide typo correction
- provide similar command suggestions
- map aliases to canonical commands

### `assistant_bot/storage/`

Рівень персистентності.

#### `assistant_bot/storage/__init__.py`

Експортує члени пакета збереження.

#### `assistant_bot/storage/base.py`

Абстрактний інтерфейс збереження.

Responsibilities:

- define required storage contract for contacts and notes

#### `assistant_bot/storage/json_storage.py`

Конкретний бекенд збереження на базі JSON.

Responsibilities:

- load contacts and notes from JSON
- save contacts and notes atomically
- create backups for corrupted files
- isolate persistence details from business logic

#### `assistant_bot/storage/paths.py`

Утиліти для шляхів збереження.

Responsibilities:

- define application data directory
- define contacts and notes JSON file paths

### `assistant_bot/utils/`

Утиліти, що використовуються в різних шарах.

#### `assistant_bot/utils/__init__.py`

Експортує утилітні функції.

#### `assistant_bot/utils/validators.py`

Централізований модуль валідації.

Responsibilities:

- validate names
- validate email addresses
- validate phone numbers
- validate birthdays
- validate note content
- validate and normalize tags

#### `assistant_bot/utils/datetime_utils.py`

Хелпери для роботи з датою і часом.

Responsibilities:

- calculate days until birthday
- format birthdays for output
- build birthday display strings

#### `assistant_bot/utils/text_utils.py`

Хелпери для обробки тексту.

Responsibilities:

- truncate text
- normalize whitespace
- pluralization
- match highlighting support

#### `assistant_bot/utils/fuzzy_match.py`

Хелпери для нечіткого порівняння.

Responsibilities:

- calculate similarity between strings
- find closest matching command
- collect similar commands above threshold

## Design Principles

Імплементація дотримується таких інженерних принципів:

- **Separation of concerns** — кожний шар має чітку роль
- **Single responsibility** — модулі зосереджені на одній задачі
- **Encapsulation** — правила валідації та бізнес-логіки залишаються всередині моделей і сервісів
- **Extensibility** — збереження та поведінку CLI можна розширювати з мінімальною залежністю
- **Explicit error handling** — передбачуваний потік виключень
- **Readable CLI UX** — допомога по командах, алиаси, кольорові повідомлення, структуроване відображення

## Error Handling

Додаток безпечно обробляє наступні випадки:

- некоректні команди
- неправильно сформовані email
- недійсні або неможливі номери телефону
- некоректні дати народження
- пусті обов'язкові поля
- відсутні записи
- пошкоджені JSON-файли збереження
- деструктивні дії тільки після явного підтвердження

## Залежності середовища виконання

Runtime-залежності, що використовуються в проєкті:

```txt
email-validator==2.3.0
dnspython==2.7.0
phonenumbers==9.0.25
prompt-toolkit==3.0.52
wcwidth==0.2.13
```

### Призначення залежностей

- **email-validator** — сувора валідація синтаксису email та перевірка доставлюваності
- **dnspython** — підтримка DNS, потрібна для перевірок доставлюваності email
- **phonenumbers** — парсинг та валідація реальних номерів телефону
- **prompt-toolkit** — інтерактивні підказки команд та автозавершення
- **wcwidth** — обробка ширини символів у терміналі, використовується `prompt-toolkit`

## Professional Notes

Цей README навмисно документує:

- установку
- runtime-залежності
- архітектуру
- відповідальність модулів
- набір команд
- правила валідації
- поведінку збереження

Такий рівень документації забезпечується для виконання вимог по доставці проєкту та для того, щоб репозиторій був зрозумілим для наставників, рецензентів, співпрацівників та майбутніх супровідників.

## Ліцензія проєкту

Цей проєкт розповсюджується під ліцензією MIT.
