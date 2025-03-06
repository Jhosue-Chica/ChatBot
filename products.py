import os
import json
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

class StoreBot:
    def __init__(self, products_file='products.json'):
        self.conversations = {}
        self.start_time = datetime.now()
        self.products_data = self.load_products(products_file)
        self.store_info = self.products_data.get('store_info', {})
        
        # Crear un contexto del sistema para enviar a GPT
        self.system_context = self.create_system_context()
        
        logger.info(f"📝 Inicializando StoreBot a las {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"🏪 Información de tienda cargada: {self.store_info.get('name', 'Desconocido')}")
        logger.info(f"📦 Productos cargados: {len(self.products_data.get('products', []))}")
    
    def load_products(self, file_path):
        """Cargar datos de productos desde un archivo JSON"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                logger.info(f"✅ Datos de productos cargados correctamente desde {file_path}")
                return data
        except FileNotFoundError:
            logger.error(f"❌ Archivo de productos no encontrado: {file_path}")
            return {"store_info": {"name": "Tienda Demo"}, "products": []}
        except json.JSONDecodeError:
            logger.error(f"❌ Error al decodificar el archivo JSON: {file_path}")
            return {"store_info": {"name": "Tienda Demo"}, "products": []}
    
    def create_system_context(self):
        """Crear un contexto del sistema para entrenar al modelo GPT"""
        store_name = self.store_info.get('name', 'Nuestra Tienda')
        store_desc = self.store_info.get('description', '')
        
        # Crear una representación de los productos para el contexto
        products_info = []
        for product in self.products_data.get('products', []):
            product_info = (
                f"ID: {product.get('id', 'N/A')}, "
                f"Nombre: {product.get('name', 'N/A')}, "
                f"Categoría: {product.get('category', 'N/A')}, "
                f"Precio: ${product.get('price', 0):.2f}, "
                f"Descripción: {product.get('description', 'N/A')}, "
                f"Stock: {product.get('stock', 0)} unidades, "
                f"Disponible: {'Sí' if product.get('disponible', False) else 'No'}"
            )
            
            # Añadir información de ofertas si existe
            ofertas = product.get('ofertas', {})
            if ofertas.get('activa', False):
                product_info += (
                    f", OFERTA: {ofertas.get('descuento', '')} de descuento, "
                    f"Precio de oferta: ${ofertas.get('precio_oferta', 0):.2f}, "
                    f"Válido hasta: {ofertas.get('fecha_fin', 'N/A')}"
                )
            
            products_info.append(product_info)
        
        # Crear el mensaje del sistema
        system_message = f"""
Eres un asistente virtual para la tienda {store_name}. 
{store_desc}

INFORMACIÓN DE LA TIENDA:
- Nombre: {self.store_info.get('name', 'N/A')}
- Horario: {self.store_info.get('horario', 'N/A')}
- Dirección: {self.store_info.get('direccion', 'N/A')}
- Teléfono: {self.store_info.get('telefono', 'N/A')}
- Email: {self.store_info.get('email', 'N/A')}
- Política de envíos: {self.store_info.get('politica_envios', 'N/A')}
- Política de devoluciones: {self.store_info.get('politica_devoluciones', 'N/A')}

CATÁLOGO DE PRODUCTOS:
{chr(10).join(products_info)}

INSTRUCCIONES:
1. Debes actuar siempre como un representante amable y profesional de {store_name}.
2. Proporciona información precisa sobre los productos, precios y disponibilidad.
3. Si un producto está en oferta, asegúrate de mencionarlo y destacar el descuento.
4. Si un cliente pregunta por un producto que no está en el catálogo, indícale amablemente que no está disponible pero sugiere alternativas similares.
5. Para compras, indica al cliente que puede realizar el pedido en nuestra tienda física, a través de nuestra web o en este mismo chat.
6. Cuando el cliente pregunte por el proceso de compra, explícale que puede pagar con tarjeta de crédito, PayPal o transferencia bancaria.
7. Mantén un tono conversacional, amable y cercano en todo momento.
8. Si te preguntan sobre un tema que no está relacionado con la tienda o los productos, redirígelos amablemente de vuelta a temas relacionados con nuestra tienda.
"""
        logger.info("✅ Contexto del sistema creado para GPT")
        return system_message
        
    async def start_command(self, update: Update, context: CallbackContext):
        """Manejador del comando /start"""
        user = update.message.from_user
        logger.info(f"📣 Usuario {user.first_name} (ID: {user.id}) ha iniciado el bot")
        
        store_name = self.store_info.get('name', 'nuestra tienda')
        
        welcome_message = (
            f"👋 ¡Hola {user.first_name}! Bienvenido/a a {store_name}.\n\n"
            f"Soy tu asistente virtual y estoy aquí para ayudarte con cualquier duda sobre nuestros productos, "
            f"precios, disponibilidad o realizar un pedido.\n\n"
            f"¿En qué puedo ayudarte hoy?\n\n"
            f"Usa /productos para ver un listado de nuestros productos o /ayuda para más información."
        )
        await update.message.reply_text(welcome_message)

    async def help_command(self, update: Update, context: CallbackContext):
        """Manejador del comando /help o /ayuda"""
        user = update.message.from_user
        logger.info(f"ℹ️ Usuario {user.first_name} (ID: {user.id}) solicitó ayuda")
        
        help_message = (
            "📚 Comandos disponibles:\n"
            "/start - Iniciar el asistente\n"
            "/ayuda - Mostrar esta ayuda\n"
            "/productos - Ver listado de productos\n"
            "/ofertas - Ver productos en oferta\n"
            "/info - Información de la tienda\n"
            "/reset - Reiniciar la conversación\n\n"
            "También puedes preguntarme directamente sobre productos específicos, precios o cualquier duda que tengas 😊"
        )
        await update.message.reply_text(help_message)

    async def products_command(self, update: Update, context: CallbackContext):
        """Manejador del comando /productos"""
        user = update.message.from_user
        logger.info(f"📦 Usuario {user.first_name} (ID: {user.id}) solicitó listado de productos")
        
        products = self.products_data.get('products', [])
        
        if not products:
            await update.message.reply_text("Lo siento, no hay productos disponibles en este momento.")
            return
        
        categories = {}
        for product in products:
            category = product.get('category', 'Sin categoría')
            if category not in categories:
                categories[category] = []
            
            price = product.get('price', 0)
            name = product.get('name', 'Producto sin nombre')
            
            # Verificar si hay oferta
            ofertas = product.get('ofertas', {})
            if ofertas.get('activa', False):
                price_text = f"${price:.2f} 🔥 OFERTA: ${ofertas.get('precio_oferta', 0):.2f}"
            else:
                price_text = f"${price:.2f}"
            
            categories[category].append(f"• {name}: {price_text}")
        
        # Construir mensaje por categorías
        message_parts = ["📋 Nuestro catálogo de productos:\n"]
        
        for category, items in categories.items():
            message_parts.append(f"\n📁 {category}:")
            message_parts.extend(items)
        
        message_parts.append("\n\nPara más detalles sobre un producto específico, pregúntame por su nombre.")
        
        await update.message.reply_text("\n".join(message_parts))

    async def offers_command(self, update: Update, context: CallbackContext):
        """Manejador del comando /ofertas"""
        user = update.message.from_user
        logger.info(f"🔥 Usuario {user.first_name} (ID: {user.id}) solicitó ofertas")
        
        products = self.products_data.get('products', [])
        offers = []
        
        for product in products:
            ofertas = product.get('ofertas', {})
            if ofertas.get('activa', False):
                name = product.get('name', 'Producto sin nombre')
                original_price = product.get('price', 0)
                offer_price = ofertas.get('precio_oferta', 0)
                discount = ofertas.get('descuento', '')
                end_date = ofertas.get('fecha_fin', 'Tiempo limitado')
                
                offers.append(
                    f"• {name}\n"
                    f"  Precio original: ${original_price:.2f}\n"
                    f"  Precio oferta: ${offer_price:.2f} ({discount} descuento)\n"
                    f"  Válido hasta: {end_date}"
                )
        
        if offers:
            message = "🔥 OFERTAS ESPECIALES 🔥\n\n" + "\n\n".join(offers)
            message += "\n\nPara más detalles o realizar una compra, solo pregúntame."
        else:
            message = "Lo siento, actualmente no hay ofertas especiales disponibles. ¡Revisa más tarde!"
        
        await update.message.reply_text(message)

    async def store_info_command(self, update: Update, context: CallbackContext):
        """Manejador del comando /info"""
        user = update.message.from_user
        logger.info(f"ℹ️ Usuario {user.first_name} (ID: {user.id}) solicitó información de la tienda")
        
        info_message = (
            f"ℹ️ Información de {self.store_info.get('name', 'nuestra tienda')}:\n\n"
            f"{self.store_info.get('description', '')}\n\n"
            f"🕒 Horario: {self.store_info.get('horario', 'No disponible')}\n"
            f"📍 Dirección: {self.store_info.get('direccion', 'No disponible')}\n"
            f"📞 Teléfono: {self.store_info.get('telefono', 'No disponible')}\n"
            f"📧 Email: {self.store_info.get('email', 'No disponible')}\n\n"
            f"🚚 Envíos: {self.store_info.get('politica_envios', 'No disponible')}\n"
            f"🔄 Devoluciones: {self.store_info.get('politica_devoluciones', 'No disponible')}"
        )
        
        await update.message.reply_text(info_message)

    async def reset_command(self, update: Update, context: CallbackContext):
        """Manejador del comando /reset"""
        user = update.message.from_user
        user_id = user.id
        
        if user_id in self.conversations:
            msg_count = len(self.conversations[user_id])
            del self.conversations[user_id]
            logger.info(f"🔄 Usuario {user.first_name} (ID: {user_id}) reinició su conversación ({msg_count} mensajes borrados)")
            await update.message.reply_text("🔄 Conversación reiniciada correctamente. ¿En qué puedo ayudarte ahora?")
        else:
            logger.info(f"🔄 Usuario {user.first_name} (ID: {user_id}) intentó reiniciar, pero no tiene una conversación activa")
            await update.message.reply_text("🔄 No hay una conversación activa para reiniciar. ¿En qué puedo ayudarte?")

    async def handle_message(self, update: Update, context: CallbackContext):
        """Manejador principal de mensajes"""
        user = update.message.from_user
        user_id = user.id
        user_message = update.message.text
        
        # Log del mensaje recibido
        logger.info(f"💬 Mensaje recibido de {user.first_name} (ID: {user_id}): '{user_message[:30]}...' si es largo")

        # Inicializar o recuperar el historial de conversación
        if user_id not in self.conversations:
            # Si es una nueva conversación, añadir el contexto del sistema
            self.conversations[user_id] = [
                {"role": "system", "content": self.system_context}
            ]
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
        logger.info("🤖 Iniciando el bot de tienda con Telegram...")
        
        # Crear la aplicación
        app = Application.builder().token(TELEGRAM_TOKEN).build()

        # Añadir handlers
        app.add_handler(CommandHandler("start", self.start_command))
        app.add_handler(CommandHandler("ayuda", self.help_command))
        app.add_handler(CommandHandler("help", self.help_command))
        app.add_handler(CommandHandler("productos", self.products_command))
        app.add_handler(CommandHandler("ofertas", self.offers_command))
        app.add_handler(CommandHandler("info", self.store_info_command))
        app.add_handler(CommandHandler("reset", self.reset_command))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        # Añadir manejador de errores
        app.add_error_handler(self.error_handler)

        # Iniciar el bot
        logger.info(f"✅ Bot de tienda {self.store_info.get('name', '')} configurado y listo para funcionar")
        logger.info("🚀 Iniciando polling...")
        app.run_polling()
        logger.info("👋 Bot detenido")

if __name__ == "__main__":
    print("=" * 50)
    print(f"🤖 INICIANDO BOT DE TIENDA CON GPT-3.5")
    print("=" * 50)
    bot = StoreBot('products.json')
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