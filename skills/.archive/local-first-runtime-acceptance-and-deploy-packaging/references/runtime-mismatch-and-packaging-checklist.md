# Runtime mismatch and deploy packaging checklist

## Что зафиксировано как полезный паттерн

### 1. Сначала проверь, что frontend и backend вообще из одного project root

Минимальные признаки:
- порт слушает ожидаемый процесс;
- `cwd` процесса совпадает с нужным проектом;
- user-systemd `ExecStart` указывает на тот же проект;
- ручной dev-сервер не маскирует сервисный runtime.

### 2. Для policy/settings нужен именно round-trip

Надёжная схема:
1. `GET` текущее состояние;
2. `PATCH`/`POST` изменения;
3. повторный `GET`;
4. если меняется inventory или classification — проверка изменения в runtime payload;
5. restore исходного состояния.

### 3. User-layer и admin-layer нельзя смешивать

Если задача про source policy:
- user layer должен видеть только режимы вроде `local_only / local_first / global_only`;
- inventory, connector groups и internal/external classification — это admin layer.

### 4. Документация после приёмки должна быть четырёхслойной

Минимальный комплект:
- README как входная точка;
- SYSTEM_OVERVIEW с полной моделью системы;
- DEPLOYMENT_GUIDE для нового сервера;
- TESTING_SCENARIO для первого user-теста.

### 5. Deploy package лучше оформлять как явный каталог

Полезный состав:
- `env/*.example`
- `systemd/*.service`
- install script
- verify script
- README

Даже если архив ещё не собран, такой каталог уже можно передавать и проверять.
