from typing import Any

__all__ = ("tuple_item_keywords",)


def tuple_item_keywords(prefix_items: Any, items: Any = None, additional_items: Any = None) -> dict[str, str]:
    """Map JSON Schema 2020-12 tuple keywords onto their Draft07 keywords.

    Draft07 has no ``prefixItems``: positional schemas become an ``items`` array
    and a trailing ``items`` schema becomes ``additionalItems``. An empty
    ``prefixItems`` constrains nothing, so it is dropped and a trailing ``items``
    schema keeps its keyword.

    Args:
        prefix_items: The positional item schemas.
        items: The trailing item schema, or ``None`` when absent.
        additional_items: An explicit ``additionalItems`` value, or ``None`` when absent.

    Returns:
        The Draft07 keyword for each supplied keyword that is emitted.

    Raises:
        ValueError: If ``items`` is a schema array, or ``items`` and
            ``additional_items`` are both supplied.
    """
    if items is not None and additional_items is not None:
        msg = "items and additionalItems cannot both accompany prefixItems"
        raise ValueError(msg)
    if prefix_items is not None and isinstance(items, list):
        msg = "items must be a single schema when prefixItems is present"
        raise ValueError(msg)
    keywords: dict[str, str] = {}
    if prefix_items:
        keywords["prefixItems"] = "items"
    if items is not None:
        keywords["items"] = "additionalItems" if prefix_items else "items"
    if additional_items is not None:
        keywords["additionalItems"] = "additionalItems"
    return keywords
