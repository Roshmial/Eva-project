# Fixed-IP temporary pilot contour

Когда применять:
- есть отдельный сервер с фиксированным публичным IP;
- тестировщикам нужен обычный browser URL;
- домен и SSH-доступ исключены;
- пилот короткий, на 1–2 недели.

Рабочий паттерн:
1. Оставить backend и runtime на loopback (`127.0.0.1`).
2. Открыть наружу только frontend entrypoint.
3. Для dev-server режима временно перевести frontend bind host на `0.0.0.0` через systemd override/env override.
4. Если frontend проксирует `/api`, добавить внешний IP origin в backend CORS allowlist.
5. После рестарта проверить три слоя:
   - `systemctl --user is-active ...`
   - `ss -ltnp` на нужных портах
   - `curl -I http://<public-ip>:<frontend-port>/`
6. Пользователям давать один фиксированный URL по IP; внутренние backend/runtime порты не светить.

Зачем это важно:
- quick tunnels могут жить меньше, чем срок пилота;
- прямой IP убирает внешний point of failure;
- при этом same-origin proxy позволяет не открывать backend наружу.

Ограничения:
- без домена это обычно HTTP или self-signed HTTPS;
- подходит для тестового контура, но не как финальная production-схема.
