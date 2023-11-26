import argparse
import asyncio
import logging

from bot.handlers.wish_editor.wish_editor_draft import WishEditorDraft
from wish.storage_adapters.file_storage_adapter import WishStorageFileAdapter
from wish.wish_manager import WishManager


async def generate_wishes(wish_manager: WishManager, owner_id: int, count: int):
    response = await wish_manager.get_wishlist(owner_id, owner_id)
    wish_start_idx = len(response.wishlist)
    for wish_idx in range(count):
        draft = WishEditorDraft(
            0,
            f"autogen wish {wish_start_idx + wish_idx + 1}",
            f"autogen desc",
            0.0,
            None)
        await wish_manager.create_wish(owner_id, draft)


async def generator_entry_point() -> None:
    parser = argparse.ArgumentParser("Wish Generator")
    parser.add_argument('--token', required=True)
    parser.add_argument('--storage-file', required=True)
    parser.add_argument('--wish-owner-id', required=True)
    parser.add_argument('--wish-count', required=True, type=int)
    args = parser.parse_args()

    root_logger = logging.getLogger('wish-generator')
    wish_storage = WishStorageFileAdapter(args.storage_file)
    wish_manager = WishManager(wish_storage, root_logger)

    await generate_wishes(wish_manager, args.wish_owner_id, args.wish_count)


if __name__ == '__main__':
    asyncio.run(generator_entry_point())
