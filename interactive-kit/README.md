# Aurora OpenCode interactive kit

Project-local конфигурация OpenCode для интерактивной разработки нативных приложений ОС Аврора. Пользователь описывает приложение обычным текстом, утверждает план и контракт, а агенты исследуют, реализуют, собирают и проверяют функциональность небольшими вертикальными срезами.

## Состав

- `orchestrator` ведёт диалог, план и контракты;
- `integration-researcher`, `aurora-researcher` и `ui-researcher` проверяют интеграцию, платформу и интерфейс;
- `architect` проектирует решение;
- `implementer` изменяет исходники;
- `reviewer` независимо проверяет результат;
- `/aurora-init` создаёт CMake-проект из закреплённого Application Template.

## Установка в проект

Скопируйте файлы kit в корень проекта:

```bash
cp -R /path/to/interactive-kit/.opencode /path/to/app/
cp -R /path/to/interactive-kit/templates /path/to/app/
cp /path/to/interactive-kit/AGENTS.md /path/to/app/
cp /path/to/interactive-kit/opencode.json /path/to/app/
cp /path/to/interactive-kit/aurora.local.json /path/to/app/
```

Для уже существующего проекта вручную перенесите подходящие строки из `.gitignore.fragment` в его `.gitignore`. Для нового проекта это сделает `/aurora-init`.

Затем:

```bash
cd /path/to/app
opencode --agent orchestrator
```

Убедитесь, что команда `audb` установлена и доступна в `PATH`. Если путь к SDK, target или имя эмулятора отличаются, измените `aurora.local.json`. Этот файл содержит локальные параметры окружения и не должен попадать в Git.

Если исходников ещё нет, выполните:

```text
/aurora-init ru.example.demo "Demo" "Демо"
```

Инициализатор создаст Git-репозиторий с веткой `main`, если его ещё нет. После этого опишите приложение и доступное время обычным текстом. Оркестратор соберёт необходимое исследование, предложит план и контракт для подтверждения, а затем проведёт реализацию и проверку. Для демонстрации сначала выбирается один законченный пользовательский сценарий; остальной scope сохраняется в backlog.

Контрольные коммиты создаются после проверенного каркаса, утверждённого контракта и принятого среза. Push выполняется только по отдельной просьбе пользователя. Снимки и ввод через `audb` помогают агентам проверить эмулятор, но финальное поведение принимает пользователь.

## Окружение

- ОС Аврора 5.2.1 и SDK 5.2.1.200;
- Qt 5.6.3, CMake, C++ и QML/Silica;
- настроенный Aurora SDK target;
- запущенный эмулятор для проверки через `audb`.

## Источники baseline

- [Application Template](https://developer.auroraos.ru/demos/application-template)
- [Документация ОС Аврора 5.2.1](https://developer.auroraos.ru/doc/platform)
- [Начало работы с Аврора IDE/SDK](https://developer.auroraos.ru/doc/sdk/app_development/start)
- [Qt Test example](https://developer.auroraos.ru/demos/qt-test)
