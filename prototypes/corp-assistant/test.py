from bs4 import BeautifulSoup, Comment, NavigableString


def html_to_telegram(html_text: str, max_length: int = 4096) -> str:
    """
    Конвертирует HTML в Telegram-совместимую разметку.

    Поддерживает:
    ✅ Жирный текст: <b>, <strong> → **
    ✅ Курсив: <i>, <em> → *
    ✅ Подчеркивание: <u>, <ins> → __
    ✅ Зачеркивание: <s>, <strike>, <del> → ~
    ✅ Моноширинный: <code> → `
    ✅ Блок кода: <pre> → ```
    ✅ Ссылки: <a href="..."> → [текст](url)
    ✅ Заголовки: <h1>-<h6> → **ЖИРНЫЙ ТЕКСТ** + переносы

    Удаляет:
    ❌ Неподдерживаемые теги: <div>, <span>, <table>, <img> и др.
    ❌ Атрибуты стилей: style, class, id

    Args:
        html_text: Входной HTML текст
        max_length: Максимальная длина результата (ограничение Telegram)

    Returns:
        Telegram-совместимая разметка
    """
    if not html_text or not html_text.strip():
        return ""

    # Создаем парсер и обрабатываем HTML
    soup = BeautifulSoup(html_text, "html.parser")

    def process_element(element):
        """Рекурсивно обрабатывает элемент и его детей."""

        # Если это строка текста - возвращаем как есть
        if isinstance(element, NavigableString):
            return str(element)

        # Если это комментарий - пропускаем
        if isinstance(element, Comment):
            return ""

        tag_name = element.name.lower()

        # Обрабатываем детей текущего элемента
        children_text = "".join(process_element(child) for child in element.children)

        # Telegram-совместимые теги (оставляем как есть или преобразуем)
        if tag_name in ["b", "strong"]:
            return f"**{children_text}**"

        elif tag_name in ["i", "em"]:
            return f"*{children_text}*"

        elif tag_name in ["u", "ins"]:
            return f"__{children_text}__"

        elif tag_name in ["s", "strike", "del"]:
            return f"~{children_text}~"

        elif tag_name == "code":
            # Для inline кода
            return f"`{children_text}`"

        elif tag_name == "pre":
            # Для блоков кода
            return f"\n```\n{children_text}\n```\n"

        elif tag_name == "a":
            # Обрабатываем ссылки
            href = element.get("href", "")
            if href and children_text:
                return f"[{children_text}]({href})"
            return children_text

        elif tag_name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
            # Заголовки преобразуем в жирный текст с отступами
            level = int(tag_name[1])
            prefix = "\n" + "🔸" * min(level, 3) + " "  # Добавляем маркеры для наглядности
            return f"{prefix}**{children_text.upper()}**\n\n"

        elif tag_name in ["p", "br"]:
            # Абзацы и переносы - добавляем \n
            suffix = "\n" if tag_name == "p" else "\n"
            return f"{children_text}{suffix}"

        elif tag_name in ["ul", "ol"]:
            # Списки - сохраняем структуру
            return f"\n{children_text}\n"

        elif tag_name == "li":
            # Элементы списка
            parent = element.find_parent(["ul", "ol"])
            if parent and parent.name == "ol":
                # Для нумерованных списков определяем индекс
                index = list(parent.find_all("li", recursive=False)).index(element) + 1
                prefix = f"{index}. "
            else:
                # Для маркированных списков
                prefix = "• "
            return f"{prefix}{children_text}\n"

        elif tag_name == "hr":
            # Горизонтальная линия
            return "\n" + "─" * 20 + "\n"

        elif tag_name == "blockquote":
            # Цитаты
            lines = children_text.strip().split("\n")
            quoted = "\n".join(f"▎ {line}" for line in lines if line.strip())
            return f"\n{quoted}\n"

        # Теги, которые нужно сохранить, но без содержимого
        elif tag_name in ["html", "body", "head", "title", "meta"]:
            return ""

        # Неподдерживаемые теги - извлекаем только текст детей
        else:
            # Для div, span и других - только содержимое
            return children_text

    # Обрабатываем весь документ
    result = process_element(soup.html if soup.html else soup)

    # Очищаем лишние пробелы и переносы
    lines = [line.strip() for line in result.split("\n")]
    result = "\n".join(line for line in lines if line)

    # Обрезаем по максимальной длине Telegram
    if len(result) > max_length:
        result = result[: max_length - 3] + "..."

    return result


# Пример использования функции
def test_conversion():
    """Тестирование функции на примере HTML."""

    from pathlib import Path

    import markdown

    md_content = Path("Протокол совещания.md").read_text(encoding="utf-8")
    text = html_to_telegram(markdown.markdown(md_content))
    print(text)


if __name__ == "__main__":
    test_conversion()
