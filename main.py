from inventoryapp import InventoryApp
import asyncio

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(InventoryApp().async_run())
    loop.close()