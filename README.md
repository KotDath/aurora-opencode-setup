# Aurora OpenCode setup

Репозиторий содержит актуальный минимальный project-local конфиг OpenCode для
интерактивной разработки приложений ОС Аврора.

- [`interactive-kit/`](interactive-kit/) — конфигурация, роли, навыки, шаблоны
  контрактов и единственная команда инициализации;
- [`tests/test_interactive_kit.py`](tests/test_interactive_kit.py) — структурные
  и детерминированные проверки поставки.

## Проверка

```bash
python3 tests/test_interactive_kit.py -v
```
