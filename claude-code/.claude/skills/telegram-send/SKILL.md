---
name: telegram-send
description: Envía un mensaje de texto a Telegram (Bot API sendMessage) usando TELEGRAM_BOT_TOKEN y TELEGRAM_CHAT_ID de .claude/settings.local.json.
disable-model-invocation: true
argument-hint: <mensaje>
allowed-tools: Bash(node *)
---

# /telegram-send

Mensaje: `$ARGUMENTS`

1. Si el mensaje está vacío, pide el texto al usuario y para.
2. Envíalo por stdin (evita problemas de comillas), sustituyendo el texto literal:

```bash
node "$CLAUDE_PROJECT_DIR/.claude/skills/telegram-send/send.mjs" <<'EOF'
<mensaje>
EOF
```

3. Reporta solo el resultado (`message_id`) o el error. Si falta variable de entorno, indica definir `TELEGRAM_BOT_TOKEN` y `TELEGRAM_CHAT_ID` en `.claude/settings.local.json` → `env` y reiniciar Claude Code. Nunca muestres el token.
