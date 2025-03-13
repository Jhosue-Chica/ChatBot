import json
import pymongo
from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()
MONGODB_URI = os.getenv('MONGODB_URI')
MONGODB_DB = os.getenv('MONGODB_DB', 'TechStore')

def migrate_data_to_mongodb(json_file='products.json'):
    """
    Migra los datos del archivo JSON a MongoDB
    """
    # Verificar que la URI de MongoDB está disponible
    if not MONGODB_URI:
        print("⚠️ MONGODB_URI no encontrado en el archivo .env")
        return False
    
    # Cargar datos desde el archivo JSON
    try:
        with open(json_file, 'r', encoding='utf-8') as file:
            data = json.load(file)
            print(f"✅ Datos cargados correctamente desde {json_file}")
    except FileNotFoundError:
        print(f"❌ Archivo no encontrado: {json_file}")
        return False
    except json.JSONDecodeError:
        print(f"❌ Error al decodificar el archivo JSON: {json_file}")
        return False
    
    # Conectar a MongoDB
    try:
        client = MongoClient(MONGODB_URI)
        db = client[MONGODB_DB]
        print(f"✅ Conexión exitosa a MongoDB: {MONGODB_DB}")
    except Exception as e:
        print(f"❌ Error al conectar a MongoDB: {str(e)}")
        return False
    
    # Migrar información de la tienda
    try:
        # Eliminar datos existentes
        db.storeInfo.delete_many({})
        # Insertar nueva información
        db.storeInfo.insert_one(data.get('store_info', {}))
        print(f"✅ Información de tienda migrada con éxito")
    except Exception as e:
        print(f"❌ Error al migrar información de tienda: {str(e)}")
    
    # Migrar categorías
    try:
        # Eliminar datos existentes
        db.categories.delete_many({})
        # Insertar nuevas categorías
        categories = [{"name": category} for category in data.get('categories', [])]
        if categories:
            db.categories.insert_many(categories)
            print(f"✅ {len(categories)} categorías migradas con éxito")
        else:
            print("⚠️ No se encontraron categorías para migrar")
    except Exception as e:
        print(f"❌ Error al migrar categorías: {str(e)}")
    
    # Migrar productos
    try:
        # Eliminar datos existentes
        db.products.delete_many({})
        # Insertar nuevos productos
        products = data.get('products', [])
        if products:
            db.products.insert_many(products)
            print(f"✅ {len(products)} productos migrados con éxito")
        else:
            print("⚠️ No se encontraron productos para migrar")
    except Exception as e:
        print(f"❌ Error al migrar productos: {str(e)}")
    
    # Crear índices para mejorar el rendimiento de las consultas
    try:
        # Índice para búsqueda rápida por ID
        db.products.create_index("id", unique=True)
        # Índice para búsqueda por categoría
        db.products.create_index("category")
        # Índice para búsqueda de ofertas
        db.products.create_index("ofertas.activa")
        print("✅ Índices creados correctamente")
    except Exception as e:
        print(f"❌ Error al crear índices: {str(e)}")
    
    print(f"✅ Migración completada con éxito a la base de datos {MONGODB_DB}")
    return True

if __name__ == "__main__":
    print("=" * 50)
    print(f"🚀 INICIANDO MIGRACIÓN DE DATOS A MONGODB")
    print("=" * 50)
    
    success = migrate_data_to_mongodb('products.json')
    
    if success:
        print("\n" + "=" * 50)
        print("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
        print("=" * 50)
    else:
        print("\n" + "=" * 50)
        print("❌ LA MIGRACIÓN NO SE COMPLETÓ CORRECTAMENTE")
        print("=" * 50)