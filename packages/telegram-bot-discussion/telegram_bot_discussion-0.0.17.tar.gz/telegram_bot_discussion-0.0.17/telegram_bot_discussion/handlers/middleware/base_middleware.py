from typing import Tuple, Union


from telegram import Update
from telegram.ext import CallbackContext


class BaseMiddleware:

    async def middleware(
        self,
        update: Update,
        context: CallbackContext,
    ) -> Union[Tuple[Update, CallbackContext], None]:
        return update, context
