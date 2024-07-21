from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from datetime import datetime
import aiohttp # type: ignore
import re

# Inisialisasi
print("Bot Jalan...")
token = "7122138934:AAFxfRizWE5rcwntaPFbHbNJmxhIGVuk5EA"
apiUrl = "http://192.168.0.107:7557"
adminChatId = ["6534680339", "1216230336"]

# log pesan
async def log_pesan(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{waktu} 📥 dari {update.message.from_user.username}: {update.message.text}")

# start
async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Terima kasih {update.effective_user.first_name}, Telah menggunakan bot ini')

# list
async def listDevice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    async with aiohttp.ClientSession() as session:
        async with session.get(f'{apiUrl}/devices') as response:
            if response.status == 200:
                data = await response.json()
                devices = []
                for index, device in enumerate(data):
                    device_id = device.get('_id', 'Unknown ID')
                    device_info = device.get('_deviceId', {})
                    
                    manufacturer_full = device_info.get('_Manufacturer', 'Unknown Manufacturer')
                    manufacturer = manufacturer_full.split()[0] if manufacturer_full != 'Unknown Manufacturer' else manufacturer_full
                    serial_number = device_info.get('_SerialNumber', 'Unknown Serial Number')
                    
                    devices.append(f"{index+1}. {manufacturer} SN: {serial_number}")

                devices_text = "\n".join(devices)
                await update.message.reply_text(
                    f'Perangkat Yang Terhubung:\n\n{devices_text}', 
                    parse_mode='Markdown'
                )
            else:
                await update.message.reply_text(f'Gagal mengambil data dari API. Status: {response.status}')

# ubahpw
async def ubahpw(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text.strip()
    match = re.match(r'^/ubahpw (\S+)\.(\S+)$', text)
    
    if not match:
        await update.message.reply_text('Format pesan salah. Gunakan format: /ubahpw <device_id>.<wifi_name>')
        return
    
    device_id = match.group(1)
    pw_name = match.group(2)
    
    async with aiohttp.ClientSession() as session:
        payload = {
            "name": "setParameterValues",
            "parameterValues": [
                ["InternetGatewayDevice.LANDevice.1.WLANConfiguration.1.PreSharedKey.1.PreSharedKey", pw_name, "xsd:string"]
            ]
        }
        
        url = f'{apiUrl}/devices/{device_id}/tasks?connection_request'
        async with session.post(url, json=payload) as response:
            print(response)
            if response.status == 200 or response.status == 202:
                await update.message.reply_text(f'Password WiFi berhasil diubah dengan {pw_name}')
            else:
                await update.message.reply_text(f'Gagal mengirim perubahan password WiFi. Status: {response.status}')

# ubahssid
async def ubahssid(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text.strip()
    match = re.match(r'^/ubahssid (\S+)\.(\S+)$', text)
    
    if not match:
        await update.message.reply_text('Format pesan salah. Gunakan format: /ubahssid <device_id>.<wifi_name>')
        return
    
    device_id = match.group(1)
    wifi_name = match.group(2)
    
    async with aiohttp.ClientSession() as session:
        payload = {
            "name": "setParameterValues",
            "parameterValues": [
                ["Device.WiFi.SSID.1.SSID", wifi_name, "xsd:string"]
            ]
        }
        
        url = f'{apiUrl}/devices/{device_id}/tasks?connection_request'
        async with session.post(url, json=payload) as response:
            print(response)
            if response.status == 200 or response.status == 202:
                await update.message.reply_text(f'Nama WiFi berhasil diubah dengan: {wifi_name}')
            else:
                await update.message.reply_text(f'Gagal mengirim perubahan SSID WiFi. Status: {response}')

# ubahsspw
async def ubahsspw(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text.strip()
    match = re.match(r'^/ubahsspw (\S+)\.(\S+)\.(\S+)$', text)
    
    if not match:
        await update.message.reply_text('Format pesan salah. Gunakan format: /ubahsspw <device_id>.<wifi_name>.<password>')
        return
    
    device_id = match.group(1)
    wifi_name = match.group(2)
    password = match.group(3)
    
    async with aiohttp.ClientSession() as session:
        payload = {
            "name": "setParameterValues",
            "parameterValues": [
                ["InternetGatewayDevice.LANDevice.1.WLANConfiguration.1.SSID", wifi_name, "xsd:string"],
                ["InternetGatewayDevice.LANDevice.1.WLANConfiguration.1.PreSharedKey.1.PreSharedKey", password, "xsd:string"]
            ]
        }
        
        url = f'{apiUrl}/devices/{device_id}/tasks?connection_request'
        async with session.post(url, json=payload) as response:
            print(response)
            if response.status == 200 or response.status == 202:
                await update.message.reply_text(f'SSID dan Password berhasil diubah dengan SSID {wifi_name} dan Password: {password}')
            elif response.status == 404:
                await update.message.reply_text(f'Gagal mengirim perubahan SSID dan password WiFi. Status: {response.status}\n*ID Perangkat Tidak ditemukan*')
            else:
                await update.message.reply_text(f'Gagal mengirim perubahan SSID dan password WiFi, coba lagi lain kali')

# help
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = (
        "Beberapa Perintah yang dapat digunakan:\n"
        "1. /start - Memulai interaksi dengan bot.\n"
        "2. /list - Menampilkan daftar perangkat yang terhubung.\n"
        "3. /ubahssid <device_id>.<wifi_name> - Mengubah SSID WiFi perangkat.\n"
        "4. /ubahpw <device_id>.<password> - Mengubah password WiFi perangkat.\n"
        "5. /ubahsspw <device_id>.<wifi_name>.<password> - Mengubah SSID dan password WiFi perangkat."
    )
    await update.message.reply_text(f'{help_text}')
      
# infokan
async def infokan(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    username = update.message.from_user.username
    chat_id = update.message.chat_id
    await update.message.reply_text(f'Info Akun Anda:\nUsername: {username}\nChatID: {chat_id}', parse_mode='Markdown')

# AI
async def ai_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) == 0:
        await update.message.reply_text("Please provide a query. Usage: /ai <your_query>")
        return
    
    message_text = " ".join(context.args)
    api_url = f'https://api-zenn.vercel.app/api/ai/groq?q={message_text}'

    async with aiohttp.ClientSession() as session:
        async with session.get(api_url) as response:
            if response.status == 200:
                data = await response.json()
                await update.message.reply_text(data['data'], parse_mode='Markdown')
            else:
                await update.message.reply_text('Failed to fetch AI response.', parse_mode='Markdown')

#-----
app = ApplicationBuilder().token(token).build()

# Perintah log pesan
app.add_handler(MessageHandler(filters.ALL, log_pesan), group=0)
# Perintah bot
app.add_handler(CommandHandler("start", welcome), group=1)
app.add_handler(CommandHandler("list", listDevice), group=1)
app.add_handler(CommandHandler("ubahssid", ubahssid), group=1)
app.add_handler(CommandHandler("ubahpw", ubahpw), group=1)
app.add_handler(CommandHandler("ubahsspw", ubahsspw), group=1)
app.add_handler(CommandHandler("help", help), group=1)
app.add_handler(CommandHandler("info", infokan), group=1)
app.add_handler(CommandHandler("ai", ai_handler), group=1)

app.run_polling()
