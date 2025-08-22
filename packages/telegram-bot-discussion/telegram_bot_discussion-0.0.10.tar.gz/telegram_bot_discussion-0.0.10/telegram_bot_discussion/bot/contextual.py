from typing import Generic, TypeVar, Type


from telegram.ext import CallbackContext


from ..constants.constants import _DISCUSSION


T = TypeVar("T")


class Contextual(Generic[T]):

    _superclass: Type

    context: CallbackContext

    def __init__(self, context: CallbackContext) -> None:
        if not getattr(Contextual, "_superclass", None):
            from .bot import (
                Discussion,
            )  # TODO: This once import solves circular import

            Contextual._superclass = Discussion
        self.context = context

    def instance(self) -> T:
        stored = getattr(
            self.context.application,
            _DISCUSSION,
        )

        if not issubclass(stored.__class__, Contextual._superclass):
            raise ContextObjectIsNotDiscussion()
        return stored

    def __call__(self) -> T:
        return self.instance()


class ContextObjectIsNotDiscussion(Exception):
    def __str__(self):
        return "Context object is not Discussion"
