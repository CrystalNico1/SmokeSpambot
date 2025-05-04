import asyncio
from telethon import TelegramClient, events
from datetime import datetime

# === CONFIGURAZIONE ===
api_id = 23403476
api_hash = 'cab944bc9651a1e415398b6241c09d3e'
phone_number = '+393515455771'

chat_sorgente = 'https://t.me/Smokerescrow'
id_messaggio = 10
canali_target = [
[1002646183500],
]

# === CLIENT ===
client = TelegramClient('sessione_spambot', api_id, api_hash)

# === FUNZIONE INVIO PERIODICO ===
async def invia_messaggio_ogni_30min():
    while True:
        try:
            msg = await client.get_messages(chat_sorgente, ids=id_messaggio)
            for target in canali_target:
                await client.send_message(target, msg)
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Inviato in {target}")
        except Exception as e:
            print(f"[ERRORE] Invio fallito: {e}")
        await asyncio.sleep(1800)

# === COMANDI ===
@client.on(events.NewMessage(pattern=r'\.rimandamessaggio'))
async def rimanda(event):
    try:
        msg = await client.get_messages(chat_sorgente, ids=id_messaggio)
        for target in canali_target:
            await client.send_message(target, msg)
        await event.respond("✅ Messaggio reinviato!")
    except Exception as e:
        await event.respond(f"❌ Errore: {e}")

@client.on(events.NewMessage(pattern=r'\.setcanali (.+)'))
async def set_canali(event):
    global canali_target
    nuovi = [x.strip() for x in event.pattern_match.group(1).replace(',', ' ').split()]
    canali_target = list(dict.fromkeys(nuovi))
    await event.respond("✅ Lista aggiornata:\n" + '\n'.join(canali_target))

@client.on(events.NewMessage(pattern=r'\.aggiungicanale (.+)'))
async def aggiungi_canale(event):
    global canali_target
    nuovi = [x.strip() for x in event.pattern_match.group(1).replace(',', ' ').split()]
    canali_target += nuovi
    canali_target = list(dict.fromkeys(canali_target))
    await event.respond("✅ Canali aggiunti:\n" + '\n'.join(canali_target))

@client.on(events.NewMessage(pattern=r'\.mostracanali'))
async def mostra_canali(event):
    if not canali_target:
        await event.respond("⚠️ Nessun canale impostato.")
    else:
        await event.respond("📋 Canali attuali:\n" + '\n'.join(canali_target))

@client.on(events.NewMessage(pattern=r'\.rimuovicancanale (.+)'))
async def rimuovi_canale(event):
    global canali_target
    canale_rimuovere = event.pattern_match.group(1).strip()
    if canale_rimuovere in canali_target:
        canali_target.remove(canale_rimuovere)
        await event.respond(f"✅ Canale `{canale_rimuovere}` rimosso.")
    else:
        await event.respond(f"⚠️ Il canale `{canale_rimuovere}` non è presente.")

@client.on(events.NewMessage(pattern=r'\.id'))
async def mostra_id(event):
    await event.respond(f"🆔 ID di questa chat: `{event.chat_id}`")
@client.on(events.NewMessage(pattern=r'\.aggiungiid (\-?\d+)'))
async def aggiungi_id(event):
    global canali_target
    nuovo_id = int(event.pattern_match.group(1))
    if nuovo_id not in canali_target:
        canali_target.append(nuovo_id)
        await event.respond(f"✅ ID `{nuovo_id}` aggiunto alla lista.")
    else:
        await event.respond(f"⚠️ ID `{nuovo_id}` è già presente nella lista.")
        
@client.on(events.NewMessage(pattern=r'\.broadcast (.+)'))
async def broadcast(event):
    testo = event.pattern_match.group(1)
    sent_count = 0
    failed = 0

    await event.respond("🚀 Inizio invio messaggio a tutte le chat...")

    async for dialog in client.iter_dialogs():
        entity = dialog.entity

        # Filtra solo le chat dove puoi inviare
        if hasattr(entity, 'id') and (dialog.is_user or dialog.is_group or dialog.is_channel):
            try:
                await client.send_message(entity.id, testo)
                sent_count += 1
                await asyncio.sleep(1)  # Piccola pausa per evitare limiti
            except Exception as e:
                print(f"Errore in {entity.id}: {e}")
                failed += 1

    await event.respond(f"✅ Inviato a {sent_count} chat.\n❌ Falliti: {failed}")
    
# === AVVIO BOT ===
async def main():
    await client.start(phone_number)
    print("✅ Bot attivo.")
    await asyncio.gather(invia_messaggio_ogni_30min())

client.loop.run_until_complete(main())
