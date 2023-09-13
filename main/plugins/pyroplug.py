# Github.com/Vasusen-code

from .. import bot as Drone, BOT_UN
import asyncio, time, os, shutil, datetime 

from main.plugins.progress import progress_for_pyrogram
from main.plugins.helpers import screenshot, findVideoResolution
from main.plugins.helpers import duration as dr

from pyrogram import Client, filters
from pyrogram.errors import ChannelBanned, ChannelInvalid, ChannelPrivate, ChatIdInvalid, ChatInvalid
from pyrogram.enums import MessageMediaType, ChatType
from ethon.pyfunc import video_metadata
from ethon.telefunc import fast_upload
from telethon.tl.types import DocumentAttributeVideo
from telethon import events

from main.Database.database import db

def thumbnail(sender):
    if os.path.exists(f'{sender}.jpg'):
        return f'{sender}.jpg'
    else:
         return None
      
async def get_msg(userbot, client, bot, sender, to, edit_id, msg_link, i):
    edit = ""
    chat = ""
    round_message = False
    if "?single" in msg_link:
        msg_link = msg_link.split("?single")[0]
    msg_id = int(msg_link.split("/")[-1]) + int(i)
    height, width, duration, thumb_path = 90, 90, 0, None
    if 't.me/c/' in msg_link or 't.me/b/' in msg_link:
        if 't.me/b/' in msg_link:
            chat = str(msg_link.split("/")[-2])
        else:
            chat = int('-100' + str(msg_link.split("/")[-2]))
        file = ""
        try:
            msg = await userbot.get_messages(chat, msg_id)
            if msg.media:
                if msg.media==MessageMediaType.WEB_PAGE:
                    edit = await client.edit_message_text(sender, edit_id, "Cloning.")
                    await client.send_message(to, msg.text.markdown)
                    await edit.delete()
                    return
            if not msg.media:
                if msg.text:
                    edit = await client.edit_message_text(sender, edit_id, "Cloning.")
                    await client.send_message(to, msg.text.markdown)
                    await edit.delete()
                    return
            edit = await client.edit_message_text(sender, edit_id, "Trying to Download.")
            try:
                file = await userbot.download_media(
                    msg,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        client,
                        "**🔻 DOWNLOADING:**\n",
                        edit,
                        time.time()
                    )
                )
            except FileNotFoundError:
                new_name = file.split("downloads/")[1].replace("/", "-")
                file = await userbot.download_media(
                    msg,
                    file_name=new_name,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        client,
                        "**🔻 DOWNLOADING:**\n",
                        edit,
                        time.time()
                    )
                )
            print(file)
            await edit.edit('Preparing to Upload!')
            caption = None
            if msg.caption is not None:
                caption = msg.caption
                if (await db.get_data(sender))["plan"] == "pro":
                    new_caption = ""
                    caption_data = await db.get_caption(sender)
                    action = caption_data["action"]
                    string = caption_data["string "]
                    if action is not None:
                        if action == "delete":
                            for text in caption.split():
                                if not string.lower() == text.lower():
                                    new_caption += text
                        if action == "add":
                            new_caption = caption + f"\n\n{string}"
                        if action == "replace":
                            if string["d"].lower() == text.lower():
                                new_caption += string["d"]
                            else:
                                new_caption += text
                    caption = new_caption
                    
            if msg.media==MessageMediaType.VIDEO_NOTE:
                round_message = True
                print("Trying to get metadata")
                data = video_metadata(file)
                height, width, duration = data["height"], data["width"], data["duration"]
                print(f'd: {duration}, w: {width}, h:{height}')
                try:
                    thumb_path = await screenshot(file, duration, sender)
                except Exception:
                    thumb_path = None
                await client.send_video_note(
                    chat_id=to,
                    video_note=file,
                    length=height, duration=duration, 
                    thumb=thumb_path,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        client,
                        '**🔺 UPLOADING:**\n',
                        edit,
                        time.time()
                    )
                )
            elif msg.media==MessageMediaType.VIDEO and msg.video.mime_type in ["video/mp4", "video/x-matroska"]:
                print("Trying to get metadata")
                data = video_metadata(file)
                height, width, duration = data["height"], data["width"], data["duration"]
                print(f'd: {duration}, w: {width}, h:{height}')
                try:
                    thumb_path = await screenshot(file, duration, sender)
                except Exception:
                    thumb_path = None
                await client.send_video(
                    chat_id=to,
                    video=file,
                    caption=caption,
                    supports_streaming=True,
                    height=height, width=width, duration=duration, 
                    thumb=thumb_path,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        client,
                        '**🔺 UPLOADING:**\n',
                        edit,
                        time.time()
                    )
                )
            elif msg.media==MessageMediaType.VOICE:
                await client.send_voice(to, file, caption=caption)
                
            elif msg.media==MessageMediaType.PHOTO:
                await edit.edit("🔺 Uploading photo...")
                await bot.send_file(to, file, caption=caption)
            else:
                thumb_path=thumbnail(sender)
                await client.send_document(
                    to,
                    file, 
                    caption=caption,
                    thumb=thumb_path,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        client,
                        '**🔺 UPLOADING:**\n',
                        edit,
                        time.time()
                    )
                )
            try:
                os.remove(file)
                if os.path.isfile(file) == True:
                    os.remove(file)
            except Exception as e:
                print(e)
            await edit.delete()
        except (ChannelBanned, ChannelInvalid, ChannelPrivate, ChatIdInvalid, ChatInvalid):
            await client.edit_message_text(sender, edit_id, "⚠️ Have you joined the channel?")
            return
        except Exception as e:
            print(e)
            if "messages.SendMedia" in str(e) \
            or "2000" in str(e) \
            or "SaveBigFilePartRequest" in str(e) \
            or "SendMediaRequest" in str(e):
                try: 
                    if "2000" in str(e):
                        if not (await db.get_data(sender))["plan"] == "pro":
                            try:
                                os.remove(file)
                            except Exception:
                                pass 
                            return await client.edit_message_text(sender, edit_id, f'❌ Failed to save: `{msg_link}`\n\nError: {str(e)}')
                        if msg.media==MessageMediaType.VIDEO and msg.video.mime_type in ["video/mp4", "video/x-matroska"]:
                            print("Trying to get metadata")
                            data = video_metadata(file)
                            height, width, duration = data["height"], data["width"], data["duration"]
                            print(f'd: {duration}, w: {width}, h:{height}')
                            try:
                                thumb_path = await screenshot(file, duration, sender)
                            except Exception:
                                thumb_path = None
                            await userbot.send_video(chat_id=to, video=file, caption=caption, 
                                                    supports_streaming=True, 
                                                    height=height, width=width, duration=duration, 
                                                    thumb=thumb_path,
                                                    progress=progress_for_pyrogram,
                                                    progress_args=(
                                                        client,
                                                        '**🔺 UPLOADING:**\n',
                                                        edit,
                                                        time.time()))
                        else:
                            thumb_path=thumbnail(sender)
                            await userbot.send_document(
                                to,
                                file, 
                                caption=caption,
                                thumb=thumb_path,
                                progress=progress_for_pyrogram,
                                progress_args=(
                                    client,
                                    '**🔺 UPLOADING:**\n',
                                    edit,
                                    time.time()
                                )
                            )
                    if msg.media==MessageMediaType.VIDEO and msg.video.mime_type in ["video/mp4", "video/x-matroska"]:
                        UT = time.time()
                        uploader = await fast_upload(f'{file}', f'{file}', UT, bot, edit, '**🔺 UPLOADING:**')
                        attributes = [DocumentAttributeVideo(duration=duration, w=width, h=height, round_message=round_message, supports_streaming=True)] 
                        await bot.send_file(to, uploader, caption=caption, thumb=thumb_path, attributes=attributes, force_document=False)
                    elif msg.media==MessageMediaType.VIDEO_NOTE:
                        uploader = await fast_upload(f'{file}', f'{file}', UT, bot, edit, '**🔺 UPLOADING:**')
                        attributes = [DocumentAttributeVideo(duration=duration, w=width, h=height, round_message=round_message, supports_streaming=True)] 
                        await bot.send_file(to, uploader, caption=caption, thumb=thumb_path, attributes=attributes, force_document=False)
                    else:
                        UT = time.time()
                        uploader = await fast_upload(f'{file}', f'{file}', UT, bot, edit, '**🔺 UPLOADING:**')
                        await bot.send_file(to, uploader, caption=caption, thumb=thumb_path, force_document=True)
                    if os.path.isfile(file) == True:
                        os.remove(file)
                except Exception as e:
                    if "SendMediaRequest" in str(e):
                        try:
                            if msg.media==MessageMediaType.VIDEO and msg.video.mime_type in ["video/mp4", "video/x-matroska"]:
                                await client.send_video(
                                    chat_id=BOT_UN,
                                    video=file,
                                    caption=caption,
                                    supports_streaming=True,
                                    height=height, width=width, duration=duration, 
                                    thumb=thumb_path,
                                    progress=progress_for_pyrogram,
                                    progress_args=(
                                        client,
                                        '**🔺 UPLOADING:**\n',
                                        edit,
                                        time.time()
                                    )
                                )
                            else:
                                await userbot.send_document(
                                    BOT_UN,
                                    file, 
                                    caption=caption,
                                    thumb=thumb_path,
                                    progress=progress_for_pyrogram,
                                    progress_args=(
                                        client,
                                        '**🔺 UPLOADING:**\n',
                                        edit,
                                        time.time()
                                    )
                                )
                        except Exception as e:
                            print(e)
                            await client.edit_message_text(sender, edit_id, f'❌ Failed to save: `{msg_link}`\n\nError: {str(e)}')
                            try:
                                os.remove(file)
                            except Exception:
                                return
                            return 
                    else:
                        print("Tried telethon but failed because ", e)
                        await client.edit_message_text(sender, edit_id, f'❌ Failed to save: `{msg_link}`\n\nError: {str(e)}')
                        try:
                            os.remove(file)
                        except Exception:
                            return
                        return 
            else:
                await client.edit_message_text(sender, edit_id, f'❌ Failed to save: `{msg_link}`\n\nError: {str(e)}')
                try:
                    os.remove(file)
                except Exception:
                    return
                return
        try:
            os.remove(file)
            if os.path.isfile(file) == True:
                os.remove(file)
        except Exception as e:
            print(e)
        await edit.delete()
    else:
        edit = await client.edit_message_text(sender, edit_id, "Cloning.")
        chat =  msg_link.split("/")[-2]
        try:
            msg = await client.get_messages(chat, msg_id)
            if msg.empty:
                i, h, s = await db.get_credentials(sender)
                if i and h and s is not None:
                    try:
                        userbot = Client("saverestricted", session_string=s, api_hash=h, api_id=int(i))     
                        await userbot.start()
                    except Exception as e:
                        print(e)
                        return await edit.edit(str(e))
                    group_link = f't.me/b/{chat}/{int(msg_id)}'
                    await edit.delete()
                    edit = await bot.send_message(sender, "processing.")
                    await get_msg(userbot, client, bot, sender, to, edit.id, group_link, i)
                    await userbot.stop()
                    return await edit.delete()
            await client.copy_message(to, chat, msg_id)
        except Exception as e:
            print(e)
            return await client.edit_message_text(sender, edit_id, f'❌ Failed to save: `{msg_link}`\n\nError: {str(e)}')
        await edit.delete()
        
async def get_bulk_msg(userbot, client, sender, chat, msg_link, i):
    x = await client.send_message(sender, "Processing!")
    await get_msg(userbot, client, Drone, sender, chat, x.id, msg_link, i)
