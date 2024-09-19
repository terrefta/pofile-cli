import pytest

from ..client.pofile import is_valid_po_content


@pytest.mark.parametrize(
    "content, expected",
    [
        # Valid PO file content with all required elements
        (
            """
msgid ""
msgstr ""
"Language: en\\n"
"Content-Type: text/plain; charset=UTF-8\\n"

msgid "Hello"
msgstr "Hola"
""",
            True,
        ),
        # Missing "Language: " meta
        (
            """
msgid ""
msgstr ""
"Content-Type: text/plain; charset=UTF-8\\n"

msgid "Hello"
msgstr "Hola"
""",
            False,
        ),
        # Missing msgid
        (
            """
msgstr ""
"Language: en\\n"
"Content-Type: text/plain; charset=UTF-8\\n"

msgstr "Hola"
""",
            False,
        ),
        # Missing msgstr
        (
            """
msgid ""
"Language: en\\n"
"Content-Type: text/plain; charset=UTF-8\\n"

msgid "Hello"
""",
            False,
        ),
        # Completely empty PO content
        (
            "",
            False,
        ),
        # PO content with all required parts but minimal
        (
            """
msgid ""
msgstr ""
"Language: fr\\n"

msgid ""
msgstr ""
""",
            True,
        ),
        # PO content with only "Language: " meta, no msgid or msgstr
        (
            """
"Language: de\\n"
""",
            False,
        ),
        # PO content with only msgid, no msgstr or "Language: "
        (
            """
            msgid "Hello"
            """,
            False,
        ),
        # PO content with only msgstr, no msgid or "Language: "
        (
            """
            msgstr "Hola"
            """,
            False,
        ),
    ],
)
def test_is_valid_po_content(content, expected):
    result = is_valid_po_content(content)
    assert result == expected
