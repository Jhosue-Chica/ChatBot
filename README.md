# 🤖 Chatbot de Telegram con GPT-3.5

Un bot de Telegram que utiliza la API de OpenAI (GPT-3.5) para mantener conversaciones inteligentes con los usuarios.

## 📋 Características

- Interacción conversacional con GPT-3.5
- Manejo de conversaciones persistentes por usuario
- Comandos integrados (/start, /help, /reset, /status)
- Sistema de logging detallado para monitoreo
- Manejo de errores robusto
- Estadísticas de uso en tiempo real

## 🛠️ Requisitos previos

- Python 3.7+
- Una cuenta en [Telegram](https://telegram.org/)
- Un bot de Telegram (creado a través de [@BotFather](https://t.me/botfather))
- Una cuenta en [OpenAI](https://openai.com/) con acceso a API key

## ⚙️ Instalación

1. Clona este repositorio o descarga el código:

```bash
git clone https://github.com/tuusuario/telegram-chatbot-gpt.git
cd telegram-chatbot-gpt
```

2. Crea un entorno virtual (recomendado):

```bash
python -m venv venv
```

3. Activa el entorno virtual:

- En Windows:
```bash
venv\Scripts\activate
```

- En macOS/Linux:
```bash
source venv/bin/activate
```

4. Instala las dependencias:

```bash
pip install -r requirements.txt
```

5. Crea un archivo `.env` basado en el ejemplo `.env.example`:

```bash
cp .env.example .env
```

6. Edita el archivo `.env` y añade tus tokens:
- `TELEGRAM_TOKEN`: El token que te proporcionó @BotFather
- `OPENAI_API_KEY`: Tu clave API de OpenAI

## 🚀 Uso

1. Inicia el bot:

```bash
python bot.py
```

2. Abre Telegram y busca tu bot por el nombre de usuario que configuraste con @BotFather.

3. ¡Comienza a chatear!

## 📟 Comandos disponibles

- `/start` - Inicia la conversación con el bot
- `/help` - Muestra la ayuda disponible
- `/reset` - Reinicia la conversación actual (borra el historial)
- `/status` - Muestra estadísticas del bot (tiempo activo, usuarios, mensajes, etc.)

## 🔍 Monitoreo

El bot incluye un sistema de logging que muestra información detallada en la consola sobre:

- Mensajes recibidos
- Respuestas generadas
- Tiempo de procesamiento
- Errores y excepciones
- Estadísticas de uso

## ⚠️ Solución de problemas

### El bot no responde:
- Verifica que los tokens en el archivo `.env` sean correctos
- Asegúrate de que tu API key de OpenAI esté activa y tenga saldo
- Revisa los logs en la consola para ver si hay errores específicos

### Error "Rate limit exceeded":
- OpenAI tiene límites de tasa para las solicitudes API
- Espera unos minutos e intenta de nuevo

## 📝 Personalización

Puedes personalizar el comportamiento del bot modificando:

- El mensaje de bienvenida en la función `start_command`
- La temperatura de generación (actualmente 0.7) para respuestas más/menos creativas
- El número máximo de tokens (actualmente 1000) para respuestas más largas/cortas

## 📜 Licencia

Este proyecto está licenciado bajo la Licencia MIT - consulta el archivo LICENSE para más detalles.

## 👋 Contribuir

Las contribuciones son bienvenidas. Si encuentras un bug o tienes una sugerencia, por favor crea un issue o un pull request.
