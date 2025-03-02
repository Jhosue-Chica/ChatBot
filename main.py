import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from telegram import Update
import openai
import time

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Verificar que las claves están disponibles
if not TELEGRAM_TOKEN:
    logger.error("⚠️ TELEGRAM_TOKEN no encontrado en el archivo .env")
    exit(1)
    
if not OPENAI_API_KEY:
    logger.error("⚠️ OPENAI_API_KEY no encontrado en el archivo .env")
    exit(1)

# Configurar OpenAI
openai.api_key = OPENAI_API_KEY

class ChatBot:
    def __init__(self):
        self.conversations = {}
        self.start_time = datetime.now()
        logger.info(f"📝 Inicializando ChatBot a las {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
    async def start_command(self, update: Update, context: CallbackContext):
        """Manejador del comando /start"""
        user = update.message.from_user
        logger.info(f"📣 Usuario {user.first_name} (ID: {user.id}) ha iniciado el bot")
        
        welcome_message = (
            f"👋 ¡Hola {user.first_name}! Soy un chatbot potenciado por GPT-3.5.\n"
            "Puedes preguntarme lo que quieras y trataré de ayudarte.\n\n"
            "Usa /help para ver los comandos disponibles."
        )
        await update.message.reply_text(welcome_message)

    async def help_command(self, update: Update, context: CallbackContext):
        """Manejador del comando /help"""
        user = update.message.from_user
        logger.info(f"ℹ️ Usuario {user.first_name} (ID: {user.id}) solicitó ayuda")
        
        help_message = (
            "📚 Comandos disponibles:\n"
            "/start - Iniciar el bot\n"
            "/help - Mostrar esta ayuda\n"
            "/reset - Reiniciar la conversación\n"
            "/status - Ver estado del bot\n\n"
            "Simplemente envía un mensaje y te responderé 😊"
        )
        await update.message.reply_text(help_message)

    async def reset_command(self, update: Update, context: CallbackContext):
        """Manejador del comando /reset"""
        user = update.message.from_user
        user_id = user.id
        
        if user_id in self.conversations:
            msg_count = len(self.conversations[user_id])
            del self.conversations[user_id]
            logger.info(f"🔄 Usuario {user.first_name} (ID: {user_id}) reinició su conversación ({msg_count} mensajes borrados)")
            await update.message.reply_text("🔄 Conversación reiniciada correctamente")
        else:
            logger.info(f"🔄 Usuario {user.first_name} (ID: {user_id}) intentó reiniciar, pero no tiene una conversación activa")
            await update.message.reply_text("🔄 No hay una conversación activa para reiniciar")

    async def status_command(self, update: Update, context: CallbackContext):
        """Manejador del comando /status para mostrar estadísticas del bot"""
        user = update.message.from_user
        logger.info(f"📊 Usuario {user.first_name} (ID: {user.id}) solicitó estado del bot")
        
        uptime = datetime.now() - self.start_time
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        active_users = len(self.conversations)
        total_messages = sum(len(conv) for conv in self.conversations.values())
        
        status_message = (
            "📊 Estado del Bot:\n"
            f"⏱️ Tiempo activo: {uptime.days} días, {hours} horas, {minutes} minutos\n"
            f"👥 Usuarios activos: {active_users}\n"
            f"💬 Total mensajes procesados: {total_messages}\n"
            f"🖥️ Versión: 1.1.0"
        )
        await update.message.reply_text(status_message)

    async def handle_message(self, update: Update, context: CallbackContext):
        """Manejador principal de mensajes"""
        user = update.message.from_user
        user_id = user.id
        user_message = update.message.text
        
        # Log del mensaje recibido
        logger.info(f"💬 Mensaje recibido de {user.first_name} (ID: {user_id}): '{user_message[:30]}...' si es largo")

        # Inicializar o recuperar el historial de conversación
        if user_id not in self.conversations:
            self.conversations[user_id] = []
            logger.info(f"👤 Nueva conversación iniciada con usuario {user.first_name} (ID: {user_id})")

        # Añadir el mensaje del usuario al historial
        self.conversations[user_id].append({
            "role": "user",
            "content": user_message
        })

        try:
            # Indicar que el bot está escribiendo
            await context.bot.send_chat_action(
                chat_id=update.effective_chat.id, 
                action="typing"
            )
            
            start_time = time.time()
            logger.info(f"🤖 Solicitando respuesta a GPT-3.5 para usuario {user.first_name} (ID: {user_id})")

            # Obtener respuesta de GPT-3.5
            response = await self.get_gpt_response(self.conversations[user_id])
            
            end_time = time.time()
            response_time = end_time - start_time
            
            # Log de estadísticas de la respuesta
            logger.info(f"✅ Respuesta generada en {response_time:.2f} segundos para usuario {user.first_name} (ID: {user_id})")
            logger.info(f"📏 Longitud de la respuesta: {len(response)} caracteres")

            # Añadir la respuesta al historial
            self.conversations[user_id].append({
                "role": "assistant",
                "content": response
            })

            # Enviar la respuesta
            await update.message.reply_text(response)

        except Exception as e:
            logger.error(f"❌ Error procesando mensaje del usuario {user.first_name} (ID: {user_id}): {str(e)}")
            error_message = (
                "❌ Lo siento, ocurrió un error al procesar tu mensaje.\n"
                "Por favor, intenta nuevamente o usa /reset para reiniciar la conversación."
            )
            await update.message.reply_text(error_message)

    async def get_gpt_response(self, conversation_history):
        """Obtener respuesta de GPT-3.5"""
        try:
            logger.info(f"🔄 Enviando solicitud a OpenAI con {len(conversation_history)} mensajes en el historial")
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=conversation_history,
                max_tokens=1000,
                temperature=0.7
            )
            
            logger.info(f"✅ Respuesta recibida de OpenAI exitosamente")
            return response.choices[0].message.content
        except openai.error.RateLimitError:
            logger.error("⚠️ Error de límite de tasa (Rate Limit) en OpenAI API")
            raise Exception("Se ha alcanzado el límite de solicitudes a OpenAI. Por favor, intenta más tarde.")
        except openai.error.AuthenticationError:
            logger.error("🔑 Error de autenticación en OpenAI API")
            raise Exception("Error de autenticación con OpenAI. Verifica tu API key.")
        except Exception as e:
            logger.error(f"❌ Error general al comunicarse con OpenAI: {str(e)}")
            raise Exception(f"Error al comunicarse con GPT-3.5: {str(e)}")

    def error_handler(self, update, context):
        """Manejador global de errores"""
        logger.error(f"⚠️ Error en la actualización {update}: {context.error}")

    def run(self):
        """Iniciar el bot"""
        logger.info("🤖 Iniciando el bot de Telegram...")
        
        # Crear la aplicación
        app = Application.builder().token(TELEGRAM_TOKEN).build()

        # Añadir handlers
        app.add_handler(CommandHandler("start", self.start_command))
        app.add_handler(CommandHandler("help", self.help_command))
        app.add_handler(CommandHandler("reset", self.reset_command))
        app.add_handler(CommandHandler("status", self.status_command))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        # Añadir manejador de errores
        app.add_error_handler(self.error_handler)

        # Iniciar el bot
        logger.info("✅ Bot configurado y listo para funcionar")
        logger.info("🚀 Iniciando polling...")
        app.run_polling()
        logger.info("👋 Bot detenido")

if __name__ == "__main__":
    print("=" * 50)
    print("🤖 INICIANDO CHATBOT DE TELEGRAM CON GPT-3.5")
    print("=" * 50)
    bot = ChatBot()
    try:
        bot.run()
    except KeyboardInterrupt:
        print("\n" + "=" * 50)
        print("⛔ Bot detenido por el usuario")
        print("=" * 50)
    except Exception as e:
        print("\n" + "=" * 50)
        print(f"❌ Error crítico: {str(e)}")
        print("=" * 50)