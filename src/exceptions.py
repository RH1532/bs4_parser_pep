class ParserFindTagException(Exception):
    """Вызывается, когда парсер не может найти тег."""
    pass


class VersionListNotFoundException(Exception):
    """Вызывается, когда парсер не может найти список версий Python."""
    pass
