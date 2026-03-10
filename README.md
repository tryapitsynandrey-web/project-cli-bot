# Personal Assistant CLI

![Python](https://img.shields.io/badge/Python-3.12%2B-blue)
![Architecture](https://img.shields.io/badge/Architecture-Layered-success)
![Storage](https://img.shields.io/badge/Storage-JSON-informational)
![Interface](https://img.shields.io/badge/Interface-CLI-orange)
![Validation](https://img.shields.io/badge/Validation-Strict-critical)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

A structured command-line application for managing contacts and notes with persistent local storage, strict validation, intelligent command suggestions, and a readable colored terminal interface.

This project was developed as a team Python engineering project and follows a layered architecture with clear separation between domain models, business logic, persistence, CLI interaction, and shared utilities.

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
- [Runtime Dependencies](#runtime-dependencies)
- [Project License](#project-license)

## Project Goal

The goal of the project is to build a personal assistant application that allows a user to:

- store and manage contacts
- store and manage notes
- search records efficiently
- validate critical user input
- persist data between launches
- work comfortably through a clean command-line interface

## Core Functionality

### Contact Management

- add new contacts
- list all contacts
- search contacts by partial match
- edit existing contacts
- delete contacts with confirmation
- store multiple phone numbers for one contact
- store optional email, address, birthday, note, and tags
- show upcoming birthdays for the next N days
- manage contact tags separately

### Notes Management

- add new notes
- list all notes
- search notes by content
- edit notes
- delete notes with confirmation
- attach tags to notes
- search notes by one or multiple tags
- support `--any` and `--all` tag filtering modes

### Validation

- strict contact name validation
- strict phone validation using `phonenumbers`
- strict email validation using `email-validator`
- birthday validation in `YYYY-MM-DD` format
- note content validation
- tag normalization and validation

### Persistence

- local JSON storage
- automatic load on startup
- automatic save after changes
- graceful fallback if JSON storage becomes corrupted
- backup creation for damaged storage files

### CLI Experience

- readable colored terminal output
- command aliases
- help menu and detailed command help
- interactive prompts for complex actions
- command typo suggestions
- prompt-time completion support through `prompt-toolkit` when installed

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
- recommended: isolated virtual environment

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

After launch, the application displays the main help menu and starts an interactive command loop.

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

| Alias | Command |
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

Required fields:

- name
- at least one phone number

Optional fields:

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

Application data is stored locally in the user home directory:

```text
~/.assistant_bot/data/
```

Files used:

- `contacts.json`
- `notes.json`

### Storage Behavior

- data is loaded automatically on startup
- data is saved automatically after each modification
- if a JSON file is corrupted, the application creates a backup and continues safely
- backup files use `.backup` suffixes

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

The project follows a layered architecture.

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

Application entry point. Creates the `PersonalAssistant` instance and starts the CLI loop.

#### `requirements.txt`

Contains all runtime dependencies required for the project.

#### `LICENSE`

MIT license for the project.

#### `.gitignore`

Defines files and folders excluded from version control.

#### `.gitattributes`

Defines Git text normalization and line ending handling.

### `assistant_bot/`

Top-level application package.

#### `assistant_bot/__init__.py`

Package export file.

#### `assistant_bot/app.py`

Main application orchestrator.

Responsibilities:

- initialize services
- initialize storage
- initialize command handler
- build command dispatch table
- run the main CLI loop
- manage prompt session and completion support

### `assistant_bot/cli/`

CLI layer: parsing input, rendering output, help text, and command handlers.

#### `assistant_bot/cli/__init__.py`

Exports CLI package components.

#### `assistant_bot/cli/parser.py`

Parses raw user input into structured commands.

Responsibilities:

- normalize command names
- resolve aliases
- split arguments
- expose available commands and aliases
- support command completion token lists

#### `assistant_bot/cli/handlers.py`

Contains handlers for all user-facing commands.

Responsibilities:

- contact operations
- note operations
- tag operations
- help handling
- unknown command suggestions
- interactive input flows
- confirmation dialogs

#### `assistant_bot/cli/renderer.py`

Responsible for output formatting.

Responsibilities:

- colorized terminal output
- message rendering
- contact card rendering
- note card rendering
- compact previews
- suggestion formatting

#### `assistant_bot/cli/help_text.py`

Contains help menu definitions and detailed command descriptions.

Responsibilities:

- main menu rendering
- section grouping
- command help texts
- alias mapping for help lookup

### `assistant_bot/domain/`

Core domain models and exceptions.

#### `assistant_bot/domain/__init__.py`

Exports domain package members.

#### `assistant_bot/domain/contacts.py`

Contact domain model.

Responsibilities:

- represent contact data
- validate and normalize creation data
- update contact fields safely
- manage contact tags
- convert to and from serializable dictionaries
- support text search matching

#### `assistant_bot/domain/notes.py`

Note domain model.

Responsibilities:

- represent note data
- validate content and tags
- update note fields
- manage note tags
- serialize and deserialize notes
- support search and preview generation

#### `assistant_bot/domain/exceptions.py`

Custom exception hierarchy.

Responsibilities:

- define project-specific exceptions
- separate validation, storage, and not-found errors

### `assistant_bot/services/`

Business logic layer.

#### `assistant_bot/services/__init__.py`

Exports service package members.

#### `assistant_bot/services/contact_service.py`

Contact business logic.

Responsibilities:

- create, load, update, delete contacts
- search contacts
- collect birthdays
- manage contact tags
- return sorted contact views

#### `assistant_bot/services/note_service.py`

Note business logic.

Responsibilities:

- create, load, update, delete notes
- search notes
- filter notes by tags
- sort notes
- expose tag-based retrieval logic

#### `assistant_bot/services/birthday_service.py`

Birthday-focused logic built on top of contacts.

Responsibilities:

- collect upcoming birthdays
- format birthday-related output data

#### `assistant_bot/services/suggestion_service.py`

Command suggestion logic.

Responsibilities:

- provide typo correction
- provide similar command suggestions
- map aliases to canonical commands

### `assistant_bot/storage/`

Persistence layer.

#### `assistant_bot/storage/__init__.py`

Exports storage package members.

#### `assistant_bot/storage/base.py`

Abstract storage interface.

Responsibilities:

- define required storage contract for contacts and notes

#### `assistant_bot/storage/json_storage.py`

Concrete JSON-based storage backend.

Responsibilities:

- load contacts and notes from JSON
- save contacts and notes atomically
- create backups for corrupted files
- isolate persistence details from business logic

#### `assistant_bot/storage/paths.py`

Storage path utilities.

Responsibilities:

- define application data directory
- define contacts and notes JSON file paths

### `assistant_bot/utils/`

Utility modules shared across layers.

#### `assistant_bot/utils/__init__.py`

Exports utility functions.

#### `assistant_bot/utils/validators.py`

Centralized validation module.

Responsibilities:

- validate names
- validate email addresses
- validate phone numbers
- validate birthdays
- validate note content
- validate and normalize tags

#### `assistant_bot/utils/datetime_utils.py`

Date and time helpers.

Responsibilities:

- calculate days until birthday
- format birthdays for output
- build birthday display strings

#### `assistant_bot/utils/text_utils.py`

Text processing helpers.

Responsibilities:

- truncate text
- normalize whitespace
- pluralization
- match highlighting support

#### `assistant_bot/utils/fuzzy_match.py`

Fuzzy matching helpers.

Responsibilities:

- calculate similarity between strings
- find closest matching command
- collect similar commands above threshold

## Design Principles

The implementation follows these engineering principles:

- **Separation of concerns** — each layer has a clear role
- **Single responsibility** — modules focus on one task
- **Encapsulation** — validation and business rules remain inside models and services
- **Extensibility** — storage and CLI behavior can be extended with minimal coupling
- **Explicit error handling** — predictable exception flow
- **Readable CLI UX** — command help, aliases, colored feedback, structured rendering

## Error Handling

The application handles the following safely:

- invalid commands
- malformed emails
- invalid or impossible phone numbers
- invalid birthdays
- empty required fields
- missing records
- corrupted JSON storage files
- destructive actions through explicit confirmation

## Runtime Dependencies

Runtime dependencies used in the project:

```txt
email-validator==2.3.0
dnspython==2.7.0
phonenumbers==9.0.25
prompt-toolkit==3.0.52
wcwidth==0.2.13
```

### Dependency Purpose

- **email-validator** — strict email syntax and deliverability validation
- **dnspython** — DNS support required for email deliverability checks
- **phonenumbers** — real phone parsing and validation
- **prompt-toolkit** — interactive command suggestions and completion
- **wcwidth** — terminal width handling used by prompt-toolkit

## Professional Notes

This README intentionally documents:

- installation
- runtime dependencies
- architecture
- module responsibilities
- command set
- validation rules
- storage behavior

This level of documentation is provided to satisfy project delivery requirements and to make the repository understandable for mentors, reviewers, collaborators, and future maintainers.

## Project License

This project is distributed under the MIT License.
