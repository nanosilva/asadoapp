#!/bin/bash
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
