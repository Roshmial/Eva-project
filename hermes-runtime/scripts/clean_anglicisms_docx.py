#!/usr/bin/env python3
"""Clean common unnecessary anglicisms in Russian DOCX documents."""
from __future__ import annotations

import argparse
import re
from pathlib import Path
from docx import Document

# Case-sensitive phrase replacements first. Product/company names are intentionally not translated.
REPLACEMENTS = [
    (r"market-entry", "стратегия выхода на рынок"),
    (r"Market-entry", "Стратегия выхода на рынок"),
    (r"go-to-market", "выход на рынок"),
    (r"enterprise-клиент", "корпоративный клиент"),
    (r"enterprise-клиенты", "корпоративные клиенты"),
    (r"enterprise-контур", "корпоративный контур"),
    (r"enterprise-сегмент", "корпоративный сегмент"),
    (r"enterprise deployment", "корпоративное внедрение"),
    (r"enterprise", "корпоративный"),
    (r"Enterprise", "Корпоративный"),
    (r"security pack", "пакет материалов по безопасности"),
    (r"Security pack", "Пакет материалов по безопасности"),
    (r"demo/security pack", "демонстрация и пакет материалов по безопасности"),
    (r"due diligence", "комплексная проверка"),
    (r"Due diligence", "Комплексная проверка"),
    (r"contract review", "проверка договоров"),
    (r"Contract review", "Проверка договоров"),
    (r"contract intelligence", "договорная аналитика"),
    (r"Contract intelligence", "Договорная аналитика"),
    (r"contract management", "управление договорами"),
    (r"Contract management", "Управление договорами"),
    (r"agreement management", "управление соглашениями"),
    (r"Agreement management", "Управление соглашениями"),
    (r"contracting operations", "договорные операции"),
    (r"managed services", "управляемые услуги"),
    (r"private markets", "частные рынки"),
    (r"legal assistant", "юридический помощник"),
    (r"Legal assistant", "Юридический помощник"),
    (r"legal research", "правовое исследование"),
    (r"Legal research", "Правовое исследование"),
    (r"legal reasoning", "юридическая аргументация"),
    (r"Legal reasoning", "Юридическая аргументация"),
    (r"legal review", "юридическая проверка"),
    (r"Legal review", "Юридическая проверка"),
    (r"review", "проверка"),
    (r"Review", "Проверка"),
    (r"drafting", "подготовка документов"),
    (r"Drafting", "Подготовка документов"),
    (r"redlining", "внесение правок"),
    (r"Redlining", "Внесение правок"),
    (r"playbooks", "методики проверки"),
    (r"playbook", "методика проверки"),
    (r"workflow", "рабочий процесс"),
    (r"workflows", "рабочие процессы"),
    (r"Workflow", "Рабочий процесс"),
    (r"intake", "приём запроса"),
    (r"outputs", "результаты"),
    (r"output", "результат"),
    (r"logs", "журналы"),
    (r"audit trail", "журнал аудита"),
    (r"audit", "аудит"),
    (r"access controls", "контроль доступа"),
    (r"access control", "контроль доступа"),
    (r"access", "доступ"),
    (r"knowledge layer", "слой управления знаниями"),
    (r"document governance", "управление документами"),
    (r"governance", "управление"),
    (r"data residency", "размещение данных"),
    (r"data", "данные"),
    (r"privacy", "конфиденциальность и защита данных"),
    (r"deployment", "развёртывание"),
    (r"pricing", "ценообразование"),
    (r"privilege review", "проверка адвокатской тайны и привилегии"),
    (r"privilege", "адвокатская тайна и привилегия"),
    (r"litigation", "судебные споры"),
    (r"investigations", "расследования"),
    (r"summaries", "краткие выводы"),
    (r"document", "документ"),
    (r"contract", "договор"),
    (r"contracts", "договоры"),
    (r"clauses", "положения договора"),
    (r"clause", "положение договора"),
    (r"processor", "обработчик данных"),
    (r"transfer", "передача данных"),
    (r"breach notification", "уведомление об инциденте"),
    (r"breach", "инцидент"),
    (r"incident", "инцидент"),
    (r"confidentiality", "конфиденциальность"),
    (r"professional secrecy", "профессиональная тайна"),
    (r"regulated", "регулируемый"),
    (r"cloud", "облако"),
    (r"terms", "условия"),
    (r"region", "регион"),
    (r"assessment", "оценка"),
    (r"process", "процесс"),
    (r"controls", "контроли"),
    (r"suggested redlines", "предложенные правки"),
    (r"sensitivity", "чувствительность данных"),
    (r"media-only", "только медиа"),
    (r"Raw export", "Исходная выгрузка"),
    (r"raw export", "исходная выгрузка"),
    (r"export", "выгрузка"),
    (r"full", "полная"),
    (r"self-service", "самообслуживание"),
    (r"business", "бизнес"),
]

# Restore/keep known product names and standard abbreviations after broad replacements.
RESTORES = [
    ("Lexis+ ИИ", "Lexis+ AI"),
    ("CoCounsel ИИ", "CoCounsel AI"),
    ("Vincent ИИ", "Vincent AI"),
    ("Harvey ИИ", "Harvey AI"),
    ("Relativity aiR", "Relativity aiR"),
]


def clean_text(text: str) -> str:
    if not text:
        return text
    out = text
    for old, new in REPLACEMENTS:
        out = re.sub(old, new, out)
    # Replace standalone AI/AI- where not in obvious vendor names.
    out = re.sub(r"(?<![+A-Za-z])AI-", "ИИ-", out)
    out = re.sub(r"(?<![+A-Za-z])AI(?![A-Za-z])", "ИИ", out)
    out = out.replace("LegalAI-", "LegalAI-")  # category name retained
    for old, new in RESTORES:
        out = out.replace(old, new)
    # Cosmetic cleanup.
    out = out.replace("RFI/security pack", "RFI и пакет материалов по безопасности")
    out = out.replace("demo", "демонстрация")
    out = out.replace("Demo", "Демонстрация")
    return out


def set_paragraph_text(paragraph, new_text: str) -> None:
    if paragraph.text == new_text:
        return
    # Preserve paragraph style, but simplify runs. This is acceptable for cleanup pass.
    for run in paragraph.runs:
        run.text = ""
    if paragraph.runs:
        paragraph.runs[0].text = new_text
    else:
        paragraph.add_run(new_text)


def clean_docx(input_path: Path, output_path: Path) -> None:
    doc = Document(input_path)
    for p in doc.paragraphs:
        set_paragraph_text(p, clean_text(p.text))
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    set_paragraph_text(p, clean_text(p.text))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(output_path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("output", nargs="?")
    args = parser.parse_args()
    inp = Path(args.input).expanduser().resolve()
    out = Path(args.output).expanduser().resolve() if args.output else inp.with_name(inp.stem + "_ru_clean.docx")
    clean_docx(inp, out)
    print(out)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
