#!/usr/bin/env python3
"""
Script de instalación para AsadoApp
Instala dependencias y configura el entorno
"""

import subprocess
import sys
import os

def install_dependencies():
    """Instalar dependencias de Python"""
    dependencies = [
        "streamlit>=1.28.0",
        "pandas>=2.0.0", 
        "plotly>=5.15.0",
        "psycopg[binary]>=3.2.0",
        "pyarrow==12.0.1",
        "sqlalchemy>=2.0.0",
        "numpy>=1.24.0",
        "python-dotenv>=1.0.0"
    ]
    
    print("Instalando dependencias...")
    for dep in dependencies:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
            print(f"✓ {dep} instalado")
        except subprocess.CalledProcessError as e:
            print(f"✗ Error instalando {dep}: {e}")
            return False
    return True

def create_env_template():
    """Crear archivo .env.template con variables necesarias"""
    env_content = """# Configuración de Base de Datos PostgreSQL
DATABASE_URL=postgresql://postgres:dalerojo@localhost:5432/asadoapp
PGHOST=localhost
PGPORT=5432
PGUSER=postgres
PGPASSWORD=dalerojo
PGDATABASE=asadoapp

# Instrucciones:
# 1. Copia este archivo como .env
# 2. Modifica los valores con tu configuración de PostgreSQL
# 3. Asegúrate de que la base de datos existe
"""
    
    with open('.env.template', 'w') as f:
        f.write(env_content)
    print("✓ Archivo .env.template creado")

def create_run_script():
    """Crear script para ejecutar la aplicación"""
    run_content = """#!/bin/bash
# Script para ejecutar AsadoApp

# Verificar que existe el archivo .env
if [ ! -f .env ]; then
    echo "Error: Archivo .env no encontrado"
    echo "Copia .env.template como .env y configura tus variables"
    exit 1
fi

# Cargar variables de entorno
export $(cat .env | grep -v '^#' | xargs)

# Ejecutar la aplicación
streamlit run app.py --server.port 5000 --server.headless true --server.address 0.0.0.0
"""
    
    with open('run.sh', 'w') as f:
        f.write(run_content)
    
    # Hacer ejecutable en sistemas Unix
    if os.name != 'nt':
        os.chmod('run.sh', 0o755)
    
    print("✓ Script run.sh creado")

def main():
    """Función principal de instalación"""
    print("=== Instalador de AsadoApp ===\n")
    
    # Instalar dependencias
    if not install_dependencies():
        print("Error durante la instalación de dependencias")
        return False
    
    # Crear archivos de configuración
    create_env_template()
    create_run_script()
    
    print("\n=== Instalación Completada ===")
    print("\nPasos siguientes:")
    print("1. Configura tu base de datos PostgreSQL")
    print("2. Copia .env.template como .env y configura las variables")
    print("3. Ejecuta: python app.py o ./run.sh")
    print("\nPara más información, consulta README.md")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)