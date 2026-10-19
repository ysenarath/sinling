"""A stand-in for a third-party plugin package, loaded through a fake entry point."""

from sinling import Backend, Doc


class ShoutBackend(Backend):
    def __call__(self, doc: Doc) -> Doc:
        doc.edit_text([(len(doc.text), len(doc.text), '!')])
        return doc


class NotABackend:
    pass
