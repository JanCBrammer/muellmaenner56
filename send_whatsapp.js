#!/usr/bin/env node
/**
 * Usage: node send_whatsapp.js <phone> <message>
 *
 * <phone>   recipient in international format without '+' or spaces, e.g. 491701234567
 * <message> text to send
 *
 * On first run a QR code is printed to stdout – scan it with WhatsApp once.
 * The session is then persisted in ./.wwebjs_auth/ so subsequent runs skip
 * the QR step.
 */

const { Client, LocalAuth } = require("whatsapp-web.js");
const qrcode = require("qrcode-terminal");

const [, , phone, message] = process.argv;

if (!phone || !message) {
    console.error("Usage: node send_whatsapp.js <phone> <message>");
    process.exit(1);
}

const client = new Client({
    authStrategy: new LocalAuth(),
    puppeteer: { args: ["--no-sandbox"] },
});

client.on("qr", (qr) => {
    console.log("Scan this QR code with WhatsApp:");
    qrcode.generate(qr, { small: true });
});

client.on("ready", async () => {
    const chatId = `${phone}@c.us`;
    try {
        await client.sendMessage(chatId, message);
        console.log(`Message sent to ${phone}`);
    } finally {
        await client.destroy();
    }
});

client.on("auth_failure", (msg) => {
    console.error("Authentication failed:", msg);
    process.exit(1);
});

client.initialize();
