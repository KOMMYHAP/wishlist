import datetime
import json
from logging import Logger

from telebot.asyncio_storage import StateStorageBase

from bot.handlers.wish_editor.wish_editor_draft import WishEditorDraft
from bot.handlers.wish_viewer.wish_viewer_draft import WishViewerDraft
from wish.state_adapters.state_base_adapter import StateBaseAdapter


class StateStorageAdapter(StateBaseAdapter):
    def __init__(self, state_storage: StateStorageBase, logger: Logger):
        self._state_storage = state_storage
        self._logger = logger.getChild('user_state_storage_adapter')

    UserValueType = str | int | dict | list

    async def _get_user_data(self, user_id: int, key: str | int) -> UserValueType | None:
        user_data: dict = await self._state_storage.get_data(user_id, user_id)
        if user_data:
            user_value = user_data.get(key)
            if user_value is None:
                self._logger.debug('Key was found but its value is None: user id = %d, key = %s', user_id, str(key))
            return user_value

        self._logger.warning('Cannot find data of user %d', user_id)
        return None

    async def _set_user_data(self, user_id: int, key: str | int, value: UserValueType | None) -> bool:
        if value is None:
            self._logger.debug('Removing user data: user id %d, key %s', user_id, str(key))

        user_data: dict = await self._state_storage.get_data(user_id, user_id)
        if user_data is None:
            self._logger.debug('Creating new user data: user id %d', user_id)
            await self._state_storage.set_state(user_id, user_id, None)
            await self._state_storage.set_data(user_id, user_id, '__creation_time', datetime.datetime.now(datetime.UTC))

        result = await self._state_storage.set_data(user_id, user_id, key, value)
        if not result:
            self._logger.warning(
                'Failed to set user data: user id = %d, key = %s, value = %s',
                user_id, str(key), json.dumps(value))
        return result

    async def get_wish_editor_draft(self, user_id: int) -> WishEditorDraft | None:
        self._logger.debug('get_wish_editor_draft(%d)', user_id)
        data = await self._get_user_data(user_id, 'wish_editor_draft')
        if data is None:
            return None
        try:
            return WishEditorDraft(
                data['editor_id'],
                data['title'],
                data['hint'],
                data['cost'],
                data['wish_id'],
            )
        except KeyError as e:
            self._logger.exception(
                'Failed to parse wish editor draft from user data! user id = %d, data = %s',
                user_id, json.dumps(data), exc_info=e)
            return None

    async def update_wish_editor_draft(self, user_id: int, draft: WishEditorDraft) -> bool:
        self._logger.debug('update_wish_editor_draft(%d, %s)', user_id, str(draft))
        return await self._set_user_data(user_id, 'wish_editor_draft', {
            'editor_id': draft.editor_id,
            'title': draft.title,
            'hint': draft.hint,
            'cost': draft.cost,
            'wish_id': draft.wish_id,
        })

    async def delete_wish_editor_draft(self, user_id: int) -> bool:
        self._logger.debug('delete_wish_editor_draft(%d)', user_id)
        return await self._set_user_data(user_id, 'wish_editor_draft', None)

    async def get_wish_viewer_draft(self, user_id: int) -> WishViewerDraft | None:
        self._logger.debug('get_wish_viewer_draft(%d)', user_id)
        data = await self._get_user_data(user_id, 'wish_viewer_draft')
        if data is None:
            return None
        try:
            return WishViewerDraft(
                data['editor_id'],
                data['viewer_id'],
                data['wish_id'],
                data['reserved'],
            )
        except KeyError as e:
            self._logger.exception(
                'Failed to parse wish viewer draft from user data! user id = %d, data = %s',
                user_id, json.dumps(data), exc_info=e)
            return None

    async def update_wish_viewer_draft(self, user_id: int, draft: WishViewerDraft) -> bool:
        self._logger.debug('update_wish_editor_draft(%d, %s)', user_id, str(draft))
        return await self._set_user_data(user_id, 'wish_viewer_draft', {
            'editor_id': draft.editor_id,
            'viewer_id': draft.viewer_id,
            'reserved': draft.reserved,
            'wish_id': draft.wish_id,
        })

    async def delete_wish_viewer_draft(self, user_id: int) -> bool:
        self._logger.debug('delete_wish_viewer_draft(%d)', user_id)
        return await self._set_user_data(user_id, 'wish_viewer_draft', None)
