# AsadoApp - Organizador de Gastos para Asados

AsadoApp es una aplicación web desarrollada con Streamlit que permite organizar y dividir gastos de asados entre múltiples participantes.

## Características

- ✅ Gestión de múltiples asados independientes
- ✅ Registro de participantes por evento
- ✅ Seguimiento de gastos por categoría
- ✅ División automática de costos
- ✅ Cálculo de transferencias necesarias
- ✅ Categorías predefinidas para asados argentinos
- ✅ Categorías personalizadas
- ✅ Exportación de datos a CSV
- ✅ Base de datos PostgreSQL para persistencia
- ✅ Interfaz web responsive

## Instalación

### Requisitos
- Python 3.11+
- PostgreSQL

### Dependencias
```bash
pip install streamlit pandas plotly psycopg2-binary sqlalchemy numpy
```

### Variables de Entorno
Configura las siguientes variables de entorno para la conexión a PostgreSQL:
```bash
DATABASE_URL=postgresql://usuario:password@host:puerto/database
PGHOST=host
PGPORT=puerto
PGUSER=usuario
PGPASSWORD=password
PGDATABASE=database
```

## Uso

1. Ejecutar la aplicación:
```bash
streamlit run app.py --server.port 5000
```

2. Acceder a la aplicación en: `http://localhost:5000`

3. Crear un nuevo asado desde la barra lateral

4. Agregar participantes en la página "Participantes"

5. Registrar gastos en la página "Gastos"

6. Ver el resumen y división de costos en la página "Resumen"

## Estructura del Proyecto

- `app.py` - Aplicación principal de Streamlit
- `database.py` - Configuración y operaciones de base de datos
- `.streamlit/config.toml` - Configuración del servidor Streamlit

## Categorías Predefinidas

La aplicación incluye categorías típicas para asados argentinos:
- Carnes (Carne, Achuras, Chorizo, Morcilla, Pollo)
- Bebidas (Vino, Cerveza, Gaseosas, Agua)
- Combustible (Carbón, Leña, Encendedor)
- Verduras y acompañamientos
- Condimentos y salsas
- Pan y postres
- Varios (Hielo, Servilletas, Platos, Vasos)

## Funcionalidades Principales

### Gestión de Asados
- Crear múltiples eventos independientes
- Seleccionar asado activo
- Eliminar asados completos

### Participantes
- Agregar/eliminar participantes por asado
- Cada asado mantiene su propia lista

### Gastos
- Registrar gastos por participante
- Categorización automática
- Descripción opcional
- Timestamp automático

### Resumen y División
- Total general del asado
- Gasto por persona (división equitativa)
- Balance individual (quién pagó de más/menos)
- Instrucciones específicas de transferencia
- Gráficos de distribución por categoría y participante

### Exportación
- Descarga de datos en formato CSV
- Exportación por asado individual

## Base de Datos

La aplicación utiliza SQLAlchemy con PostgreSQL:

### Tablas:
- `asados` - Eventos principales
- `participants` - Participantes por asado
- `expenses` - Gastos registrados
- `custom_categories` - Categorías personalizadas

### Características:
- Relaciones con eliminación en cascada
- Conexión con pooling y reconexión automática
- Manejo de errores SSL

## Contribución

Para contribuir al proyecto:
1. Fork el repositorio
2. Crear una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Crear un Pull Request

## Licencia

Este proyecto está bajo licencia MIT.