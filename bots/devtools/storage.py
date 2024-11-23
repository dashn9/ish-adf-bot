import asyncio

from nodriver import Tab
from nodriver.cdp import dom_storage as dms


class DOMStorageManager:
    """
    Manages DOM Storage events.

    Attributes:
        inchoate_local_storage (list): Temporary storage for DOM storage items.
        tab (Tab): The browser tab associated with this manager.
    """

    inchoate_local_storage = []

    def __init__(self, tab, local_storage_only=True):
        """
        Initialize the DOMStorageManager.

        Args:
            tab (Tab): The browser tab this manager is attached to.
        """
        self.tab = tab
        self.local_storage_only = local_storage_only

    async def _validate_nature(self, item):
        """
        Validates the nature of a given storage object

        Args:
            item: DOMStorage Item

        Returns:
            bool: True if the storage object matches expected condition, False otherwise.
        """
        return self.local_storage_only and item.storage_id.is_local_storage

    async def parse_item_to_json(self, item):
        """
        Parses a DOM storage item into JSON format.

        Args:
            item: The DOM storage item to parse.

        Returns:
            dict: Parsed JSON representation of the storage item.
        """
        try:
            return {
                "storage_id": {
                    "is_local_storage": item.storage_id.is_local_storage,
                    "security_origin": item.storage_id.security_origin,
                    "storage_key": str(item.storage_id.storage_key),
                },
                "key": item.key,
                "value": item.new_value,
            }
        except AttributeError as e:
            print(f"Error parsing item: {e}")
            return None

    async def storage_item_added_listener(self, item_added: dms.DomStorageItemAdded):
        """
        Listener for when a storage item is added.

        Args:
            item_added (dms.DomStorageItemAdded): Event containing details of the added item.
        """
        if await self._validate_nature(item_added):
            parsed_item = await self.parse_item_to_json(item_added)
            if parsed_item:
                self.inchoate_local_storage.append(parsed_item)

    async def storage_item_removed_listener(
        self, item_removed: dms.DomStorageItemRemoved
    ):
        """
        Listener for when a storage item is removed.

        Args:
            item_removed (dms.DomStorageItemRemoved): Event containing details of the removed item.
        """
        if await self._validate_nature(item_removed):
            self.inchoate_local_storage = [
                ils
                for ils in self.inchoate_local_storage
                if not (
                    ils["storage_id"]["storage_key"]
                    == item_removed.storage_id.storage_key.to_json()
                    and ils["key"] == item_removed.key
                )
            ]

    async def storage_items_cleared_listener(
        self, items_cleared: dms.DomStorageItemsCleared
    ):
        """
        Listener for when all storage items with a specific storage key are cleared.

        Args:
            items_cleared (dms.DomStorageItemsCleared): Event containing details of the cleared items.
        """
        if await self._validate_nature(items_cleared):
            storage_key_to_clear = items_cleared.storage_id.storage_key.to_json()
            self.inchoate_local_storage = [
                ils
                for ils in self.inchoate_local_storage
                if ils["storage_id"]["storage_key"] != storage_key_to_clear
            ]

    async def storage_item_updated_listener(
        self, item_updated: dms.DomStorageItemUpdated
    ):
        """
        Listener for when a storage item is updated.

        Args:
            item_updated (dms.DomStorageItemUpdated): Event containing details of the updated item.
        """
        if await self._validate_nature(item_updated):
            for ils in self.inchoate_local_storage:
                if (
                    ils["storage_id"]["storage_key"]
                    == item_updated.storage_id.storage_key.to_json()
                    and ils["key"] == item_updated.key
                ):
                    ils["value"] = item_updated.new_value

    async def activate_listeners(self, tab=None):
        """
        Activates DOM storage event listeners for the associated tab.

        Args:
            tab (Tab, optional): The tab to attach listeners to. Defaults to the initialized tab.
        """
        tab = tab or self.tab
        await tab.send(dms.enable())
        tab.add_handler(dms.DomStorageItemAdded, self.storage_item_added_listener)
        tab.add_handler(dms.DomStorageItemRemoved, self.storage_item_removed_listener)
        tab.add_handler(dms.DomStorageItemsCleared, self.storage_items_cleared_listener)
        tab.add_handler(dms.DomStorageItemUpdated, self.storage_item_updated_listener)

    async def set_local_storage(self, local_storage: list):
        for ls in local_storage:
            ls_sid = ls["storage_id"]
            self.tab.send(
                dms.set_dom_storage_item(
                    dms.StorageId(
                        ls_sid["is_local_storage"],
                        ls_sid["security_origin"],
                        dms.SerializedStorageKey(ls_sid["storage_key"]),
                    ),
                    ls["key"],
                    ls["value"],
                )
            )
            await asyncio.sleep(0.2)
