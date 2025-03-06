# 🤖 Chatbot de Tienda para Telegram con GPT-3.5

Un bot de Telegram que utiliza la API de OpenAI (GPT-3.5) para funcionar como asistente virtual de una tienda, manejando consultas sobre productos, precios, disponibilidad y ofertas.

## 📋 Características

- Interacción conversacional con GPT-3.5
- Manejo de conversaciones persistentes por usuario
- Catálogo de productos desde archivo JSON
- Comandos integrados para explorar productos, ofertas e información de la tienda
- Sistema de logging detallado para monitoreo
- Manejo de errores robusto
- Estadísticas de uso en tiempo real

## 🏪 Características de la Tienda Virtual

- **Catálogo de productos dinámico**: Gestiona productos, precios y existencias a través de un archivo JSON
- **Información detallada de productos**: Descripción, especificaciones, precios y disponibilidad
- **Gestión de ofertas**: Destacado automático de productos en promoción
- **Categorías de productos**: Organización jerárquica del catálogo
- **Información de la tienda**: Horarios, políticas de envío y devolución, contacto
- **Asistente de ventas inteligente**: Responde preguntas sobre productos y recomienda alternativas

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

7. Personaliza el archivo `products.json` con tu catálogo de productos:
```json
{
  "store_info": {
    "name": "Tu Tienda",
    "description": "Descripción de tu tienda",
    ...
  },
  "categories": ["Categoría1", "Categoría2", ...],
  "products": [
    {
      "id": "001",
      "name": "Nombre del Producto",
      "price": 99.99,
      ...
    },
    ...
  ]
}
```

## 🚀 Uso

1. Inicia el bot:

```bash
python main.py
```

2. Abre Telegram y busca tu bot por el nombre de usuario que configuraste con @BotFather.

3. ¡Comienza a chatear y vender productos!

## 📟 Comandos disponibles

### Comandos Generales
- `/start` - Inicia la conversación con el bot
- `/help` o `/ayuda` - Muestra la ayuda disponible
- `/reset` - Reinicia la conversación actual (borra el historial)

### Comandos de Tienda
- `/productos` - Muestra el catálogo completo de productos
- `/ofertas` - Muestra productos con descuentos activos
- `/info` - Muestra información detallada de la tienda

## 🛍️ Ejemplos de interacción

El bot puede responder a preguntas como:
- "¿Cuánto cuesta el iPhone 15 Pro?"
- "¿Tienen laptops en oferta?"
- "¿Cuál es la diferencia entre el Smartphone Galaxy X10 y el iPhone 15 Pro?"
- "¿Cuáles son sus métodos de pago?"
- "¿Cuándo está disponible el envío gratuito?"
- "¿Cuál es la política de devoluciones?"

## 📂 Estructura del archivo products.json

```json
{
  "store_info": {
    "name": "Nombre de la tienda",
    "description": "Descripción",
    "horario": "Horario de atención",
    "direccion": "Dirección física",
    "telefono": "Número de contacto",
    "email": "Email de contacto",
    "politica_envios": "Información sobre envíos",
    "politica_devoluciones": "Información sobre devoluciones"
  },
  "categories": ["Categoría1", "Categoría2"],
  "products": [
    {
      "id": "ID-PRODUCTO",
      "name": "Nombre del producto",
      "category": "Categoría",
      "price": 99.99,
      "description": "Descripción detallada",
      "specs": {
        "caracteristica1": "valor1",
        "caracteristica2": "valor2"
      },
      "stock": 10,
      "disponible": true,
      "ofertas": {
        "activa": true,
        "descuento": "20%",
        "precio_oferta": 79.99,
        "fecha_fin": "2023-12-31"
      }
    }
  ]
}
```

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

### Problemas con el catálogo de productos:
- Verifica que el archivo `products.json` tenga formato JSON válido
- Asegúrate de que el archivo esté en la misma ubicación que el script principal

## 📝 Personalización

Puedes personalizar el comportamiento del bot modificando:

- El archivo `products.json` para actualizar tu catálogo
- El sistema de contexto en la función `create_system_context()` para cambiar cómo responde el asistente
- La temperatura de generación (actualmente 0.7) para respuestas más/menos creativas
- El número máximo de tokens (actualmente 1000) para respuestas más largas/cortas

## 📜 Licencia

Este proyecto está licenciado bajo la Licencia MIT - consulta el archivo LICENSE para más detalles.

## 👋 Contribuir

Las contribuciones son bienvenidas. Si encuentras un bug o tienes una sugerencia, por favor crea un issue o un pull request.
