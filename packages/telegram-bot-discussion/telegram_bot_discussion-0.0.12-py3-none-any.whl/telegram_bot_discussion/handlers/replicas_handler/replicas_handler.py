from typing import Dict, Tuple, Type, Union


from telegram import Update
from telegram.ext import CallbackContext


from ...bot.contextual import Contextual
from ...dialogue.dialogue import Dialogue, Polemic
from ...dialogue.replicas.base import (
    NoNeedReactionReplica,
    Replica,
    StopReplica,
)
from ...functions import get_from_id
from ...logger.logger_interface import LoggerInterface
from .exceptions import ReplicaClassAccessDeny


class DiscussionInterface:
    def get_dialogues(self) -> Dict[int, Polemic]: ...
    def get_logger(self) -> LoggerInterface: ...


class ReplicasHandler:

    async def access_control_list(
        self,
        user_id: int,
        replica_class: Type[Replica],
    ) -> bool:
        _, _ = user_id, replica_class
        return True

    async def middleware(
        self,
        update: Update,
        context: CallbackContext,
    ) -> Union[Tuple[Update, CallbackContext], None]:
        return update, context

    async def when_there_are_no_any_dialog(
        self,
        update: Update,
        context: CallbackContext,
    ) -> Union[Tuple[Update, CallbackContext], None]:
        return update, context

    async def handle(
        self,
        update: Update,
        context: CallbackContext,
    ):
        if (
            await self.middleware(
                update,
                context,
            )
            is None
        ):
            return

        discussion: DiscussionInterface = Contextual[DiscussionInterface](context)()

        from_id = get_from_id(update, context)
        if not from_id:
            discussion.get_logger().warning("from_id is None")
            discussion.get_logger().warning(context.bot_data)
            return

        if from_id in discussion.get_dialogues():
            await self.get_replica_from_dialogue(
                update,
                context,
            )
        else:
            await self.when_there_are_no_any_dialog(
                update,
                context,
            )

    async def get_replica_from_dialogue(
        self,
        update: Update,
        context: CallbackContext,
    ):
        from_id = get_from_id(update, context)
        if not from_id:
            return

        discussion: DiscussionInterface = Contextual[DiscussionInterface](context)()

        while True:
            try:
                replica: Replica = discussion.get_dialogues()[from_id].send(update)
                if isinstance(replica, StopReplica):
                    self.stop_dialogue(
                        context=context,
                        with_user_id=from_id,
                    )

                if await self.access_control_list(
                    from_id,
                    replica.__class__,
                ):
                    await replica.as_reply(update, context)
                else:
                    raise ReplicaClassAccessDeny(from_id, replica.__class__)
                if isinstance(replica, StopReplica):
                    break
                if isinstance(replica, NoNeedReactionReplica):
                    continue
                break

            except KeyError as e:
                discussion.get_logger().error(e)
                raise e
            except Exception as e:
                discussion.get_logger().error(e)
                self.stop_dialogue(
                    context=context,
                    with_user_id=from_id,
                )
                raise e

    async def start_dialogue(
        self,
        update: Update,
        context: CallbackContext,
        with_user_id: int,
        dialogue: Dialogue,
    ):
        # TODO: fetcher
        # calculated_user_id = 0
        # cbq: Union[CallbackQuery, None] = update.callback_query
        # if cbq and cbq.from_user:
        #     calculated_user_id = cbq.from_user.id
        # message: Union[Message, None] = update.message
        # if message and message.from_user and message.from_user.id:
        #     calculated_user_id = message.from_user.id

        discussion: DiscussionInterface = Contextual[DiscussionInterface](context)()

        if not with_user_id:
            with_user_id = get_from_id(update, context)

        self.stop_dialogue(context, with_user_id)
        discussion.get_dialogues()[with_user_id] = dialogue.replicas_flow()
        _ = next(discussion.get_dialogues()[with_user_id])
        await self.get_replica_from_dialogue(update, context)

    def stop_dialogue(
        self,
        context: CallbackContext,
        with_user_id: int,
    ):
        discussion: DiscussionInterface = Contextual[DiscussionInterface](context)()
        if with_user_id in discussion.get_dialogues():
            del discussion.get_dialogues()[with_user_id]
