# Self-subscribe runtime lessons from the June 2026 pass

Контекст:
- правки по self-subscribe и jobs UI уже были внесены в код;
- `py_compile`, `node --check` и backend smoke проходили;
- live UI уже показывал новый блок self-subscribe;
- но API/runtime вёл себя как старый.

Что оказалось важным:
1. Если `GET /api/service-info` возвращает неожиданный mode, сначала лечить launcher/runtime, а не UI.
2. Для этого проекта нельзя полагаться на голый `python app.py`, когда нужен корректный Hermes API mode.
3. Если job detail в live response не показывает новые поля, а код их уже сериализует, вероятен stale runtime или другой storage/schema.
4. Для self-subscribe нужно отдельно проверять:
   - disabled -> запрет, а не 500;
   - enabled -> успешная подписка;
   - подтверждение отдельного `job`-чата.
5. При product-разборе обязательно фиксировать модель явно:
   - recipients задаёт создатель/админ;
   - self-subscribe — дополнительная управляемая опция, а не замена recipients.
