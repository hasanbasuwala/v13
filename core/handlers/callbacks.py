from pyrogram.types import CallbackQuery

from app import app


@app.on_callback_query()
async def callback_handler(

    client,

    callback: CallbackQuery
):

    await callback.answer(

        "No actions configured."
    )