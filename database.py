import os
import logging
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Base para los modelos
Base = declarative_base()

# Modelos de la base de datos
class Asado(Base):
    __tablename__ = 'asados'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    created_date = Column(DateTime, default=datetime.now)
    
    # Relaciones
    participants = relationship("Participant", back_populates="asado", cascade="all, delete-orphan")
    expenses = relationship("Expense", back_populates="asado", cascade="all, delete-orphan")

class Participant(Base):
    __tablename__ = 'participants'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    asado_id = Column(Integer, ForeignKey('asados.id'), nullable=False)
    
    # Relaciones
    asado = relationship("Asado", back_populates="participants")
    expenses = relationship("Expense", back_populates="participant")

class Expense(Base):
    __tablename__ = 'expenses'
    
    id = Column(Integer, primary_key=True)
    participant_id = Column(Integer, ForeignKey('participants.id'), nullable=False)
    asado_id = Column(Integer, ForeignKey('asados.id'), nullable=False)
    category = Column(String(50), nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(Text, default="")
    timestamp = Column(DateTime, default=datetime.now)
    
    # Relaciones
    participant = relationship("Participant", back_populates="expenses")
    asado = relationship("Asado", back_populates="expenses")

class CustomCategory(Base):
    __tablename__ = 'custom_categories'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    created_date = Column(DateTime, default=datetime.now)

# Configuración de la base de datos
class DatabaseManager:
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL')
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable not set")
        
        self.engine = create_engine(
            self.database_url,
            pool_pre_ping=True,
            pool_recycle=300,
            connect_args={"connect_timeout": 10}
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
    def create_tables(self):
        """Crear todas las tablas"""
        try:
            Base.metadata.create_all(bind=self.engine, checkfirst=True)
            logger.info("Tablas creadas exitosamente")
        except Exception as e:
            logger.error(f"Error creando tablas: {e}")
            # No relanzar la excepción si las tablas ya existen
            if "already exists" not in str(e):
                raise
    
    def get_session(self):
        """Obtener una sesión de base de datos"""
        return self.SessionLocal()
    
    def test_connection(self):
        """Probar la conexión a la base de datos"""
        try:
            with self.engine.connect() as connection:
                from sqlalchemy import text
                connection.execute(text("SELECT 1"))
            logger.info("Conexión a base de datos exitosa")
            return True
        except Exception as e:
            logger.error(f"Error de conexión: {e}")
            return False

# Funciones de utilidad para operaciones de base de datos
class AsadoService:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def create_asado(self, name: str):
        """Crear un nuevo asado"""
        session = self.db_manager.get_session()
        try:
            # Verificar si ya existe
            existing = session.query(Asado).filter(Asado.name == name).first()
            if existing:
                return None
            
            asado = Asado(name=name)
            session.add(asado)
            session.commit()
            session.refresh(asado)
            return asado
        except Exception as e:
            session.rollback()
            logger.error(f"Error creando asado: {e}")
            raise
        finally:
            session.close()
    
    def get_all_asados(self):
        """Obtener todos los asados"""
        session = self.db_manager.get_session()
        try:
            asados = session.query(Asado).all()
            return asados
        except Exception as e:
            session.rollback()
            logger.error(f"Error obteniendo asados: {e}")
            # Reintentar con nueva sesión
            try:
                session.close()
                session = self.db_manager.get_session()
                asados = session.query(Asado).all()
                return asados
            except Exception as e2:
                logger.error(f"Error en reintento: {e2}")
                return []
        finally:
            session.close()
    
    def get_asado_by_name(self, name: str):
        """Obtener asado por nombre"""
        session = self.db_manager.get_session()
        try:
            asado = session.query(Asado).filter(Asado.name == name).first()
            return asado
        finally:
            session.close()
    
    def delete_asado(self, name: str):
        """Eliminar un asado"""
        session = self.db_manager.get_session()
        try:
            asado = session.query(Asado).filter(Asado.name == name).first()
            if asado:
                session.delete(asado)
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"Error eliminando asado: {e}")
            raise
        finally:
            session.close()
    
    def add_participant(self, asado_name: str, participant_name: str):
        """Agregar participante a un asado"""
        session = self.db_manager.get_session()
        try:
            asado = session.query(Asado).filter(Asado.name == asado_name).first()
            if not asado:
                return None
            
            # Verificar si ya existe
            existing = session.query(Participant).filter(
                Participant.name == participant_name,
                Participant.asado_id == asado.id
            ).first()
            if existing:
                return None
            
            participant = Participant(name=participant_name, asado_id=asado.id)
            session.add(participant)
            session.commit()
            session.refresh(participant)
            return participant
        except Exception as e:
            session.rollback()
            logger.error(f"Error agregando participante: {e}")
            raise
        finally:
            session.close()
    
    def get_participants(self, asado_name: str):
        """Obtener participantes de un asado"""
        session = self.db_manager.get_session()
        try:
            asado = session.query(Asado).filter(Asado.name == asado_name).first()
            if not asado:
                return []
            
            participants = session.query(Participant).filter(Participant.asado_id == asado.id).all()
            return [p.name for p in participants]
        except Exception as e:
            session.rollback()
            logger.error(f"Error obteniendo participantes: {e}")
            try:
                session.close()
                session = self.db_manager.get_session()
                asado = session.query(Asado).filter(Asado.name == asado_name).first()
                if not asado:
                    return []
                participants = session.query(Participant).filter(Participant.asado_id == asado.id).all()
                return [p.name for p in participants]
            except Exception as e2:
                logger.error(f"Error en reintento obteniendo participantes: {e2}")
                return []
        finally:
            session.close()
    
    def remove_participant(self, asado_name: str, participant_name: str):
        """Eliminar participante de un asado"""
        session = self.db_manager.get_session()
        try:
            asado = session.query(Asado).filter(Asado.name == asado_name).first()
            if not asado:
                return False
            
            participant = session.query(Participant).filter(
                Participant.name == participant_name,
                Participant.asado_id == asado.id
            ).first()
            
            if participant:
                session.delete(participant)
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"Error eliminando participante: {e}")
            raise
        finally:
            session.close()
    
    def add_expense(self, asado_name: str, participant_name: str, category: str, amount: float, description: str = ""):
        """Agregar gasto"""
        session = self.db_manager.get_session()
        try:
            asado = session.query(Asado).filter(Asado.name == asado_name).first()
            if not asado:
                return None
            
            participant = session.query(Participant).filter(
                Participant.name == participant_name,
                Participant.asado_id == asado.id
            ).first()
            if not participant:
                return None
            
            expense = Expense(
                participant_id=participant.id,
                asado_id=asado.id,
                category=category,
                amount=amount,
                description=description
            )
            session.add(expense)
            session.commit()
            session.refresh(expense)
            return expense
        except Exception as e:
            session.rollback()
            logger.error(f"Error agregando gasto: {e}")
            raise
        finally:
            session.close()
    
    def get_expenses(self, asado_name: str):
        """Obtener gastos de un asado"""
        session = self.db_manager.get_session()
        try:
            asado = session.query(Asado).filter(Asado.name == asado_name).first()
            if not asado:
                return []
            
            expenses = session.query(Expense).join(Participant).filter(
                Expense.asado_id == asado.id
            ).all()
            
            expense_list = []
            for expense in expenses:
                expense_list.append({
                    'id': expense.id,
                    'participant': expense.participant.name,
                    'category': expense.category,
                    'amount': expense.amount,
                    'description': expense.description,
                    'timestamp': expense.timestamp
                })
            
            return expense_list
        except Exception as e:
            session.rollback()
            logger.error(f"Error obteniendo gastos: {e}")
            try:
                session.close()
                session = self.db_manager.get_session()
                asado = session.query(Asado).filter(Asado.name == asado_name).first()
                if not asado:
                    return []
                expenses = session.query(Expense).join(Participant).filter(
                    Expense.asado_id == asado.id
                ).all()
                expense_list = []
                for expense in expenses:
                    expense_list.append({
                        'id': expense.id,
                        'participant': expense.participant.name,
                        'category': expense.category,
                        'amount': expense.amount,
                        'description': expense.description,
                        'timestamp': expense.timestamp
                    })
                return expense_list
            except Exception as e2:
                logger.error(f"Error en reintento obteniendo gastos: {e2}")
                return []
        finally:
            session.close()
    
    def remove_expense(self, expense_id: int):
        """Eliminar un gasto"""
        session = self.db_manager.get_session()
        try:
            expense = session.query(Expense).filter(Expense.id == expense_id).first()
            if expense:
                session.delete(expense)
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"Error eliminando gasto: {e}")
            raise
        finally:
            session.close()
    
    def get_custom_categories(self):
        """Obtener categorías personalizadas"""
        session = self.db_manager.get_session()
        try:
            categories = session.query(CustomCategory).all()
            return [c.name for c in categories]
        except Exception as e:
            session.rollback()
            logger.error(f"Error obteniendo categorías: {e}")
            try:
                session.close()
                session = self.db_manager.get_session()
                categories = session.query(CustomCategory).all()
                return [c.name for c in categories]
            except Exception as e2:
                logger.error(f"Error en reintento obteniendo categorías: {e2}")
                return []
        finally:
            session.close()
    
    def add_custom_category(self, name: str):
        """Agregar categoría personalizada"""
        session = self.db_manager.get_session()
        try:
            existing = session.query(CustomCategory).filter(CustomCategory.name == name).first()
            if existing:
                return None
            
            category = CustomCategory(name=name)
            session.add(category)
            session.commit()
            session.refresh(category)
            return category
        except Exception as e:
            session.rollback()
            logger.error(f"Error agregando categoría: {e}")
            raise
        finally:
            session.close()
    
    def remove_custom_category(self, name: str):
        """Eliminar categoría personalizada"""
        session = self.db_manager.get_session()
        try:
            category = session.query(CustomCategory).filter(CustomCategory.name == name).first()
            if category:
                session.delete(category)
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"Error eliminando categoría: {e}")
            raise
        finally:
            session.close()

# Instancia global del servicio
db_manager = None
asado_service = None

def initialize_database():
    """Inicializar la base de datos"""
    global db_manager, asado_service
    try:
        db_manager = DatabaseManager()
        db_manager.test_connection()
        db_manager.create_tables()
        asado_service = AsadoService(db_manager)
        logger.info("Base de datos inicializada correctamente")
        return True
    except Exception as e:
        logger.error(f"Error inicializando base de datos: {e}")
        return False

def get_asado_service():
    """Obtener el servicio de asados"""
    return asado_service
