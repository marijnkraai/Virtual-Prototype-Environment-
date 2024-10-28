from sqlalchemy import create_engine, String, Column, Integer, DateTime, MetaData, ForeignKey, CheckConstraint, desc, text
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from db_connect import Base

# Table: Physical Objects
class PhysicalObject(Base):
    __tablename__ = 'physical_objects'

    physical_object_id = Column(Integer, primary_key=True, autoincrement=True)
    object_name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    marker_id = Column(Integer)

    # Relationship to the physical object configurations
    configurations = relationship("PhysicalObjectConfiguration", back_populates="physical_object")
    virtual_objects = relationship("VirtualObject", back_populates="physical_object")

# Table: Virtual Objects
class VirtualObject(Base):
    __tablename__ = 'virtual_objects'

    virtual_object_id = Column(Integer, primary_key=True, autoincrement=True)
    physical_object_id = Column(Integer, ForeignKey('physical_objects.physical_object_id'), nullable=False)
    object_name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    #Relationship to physical objects
    physical_object = relationship("PhysicalObject", back_populates="virtual_objects")
    configurations = relationship("VirtualObjectConfiguration", back_populates="virtual_object")

# Table: Configurations
class Configuration(Base):
    __tablename__ = 'configurations'

    config_id = Column(Integer, primary_key=True, autoincrement=True)
    config_type = Column(String(50), CheckConstraint("config_type IN ('physical', 'virtual')"), nullable=False)
    config_name = Column(String(255))
    created_at = Column(DateTime, default=datetime.now)

    # Relationships
    physical_configs = relationship("PhysicalObjectConfiguration", back_populates="configuration")
    virtual_configs = relationship("VirtualObjectConfiguration", back_populates="configuration")
    products = relationship("Product", back_populates="configuration")

# Table: Physical Object Configurations
class PhysicalObjectConfiguration(Base):
    __tablename__ = 'physical_object_configurations'

    physical_object_config_id = Column(Integer, primary_key=True, autoincrement=True)
    physical_object_id = Column(Integer, ForeignKey('physical_objects.physical_object_id'), nullable=False)
    config_id = Column(Integer, ForeignKey('configurations.config_id'), nullable=False)
    x_coordinate = Column(Integer, nullable=False)
    y_coordinate = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    last_updated = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    physical_object = relationship("PhysicalObject", back_populates="configurations")
    configuration = relationship("Configuration", back_populates="physical_configs")
    

# Table: Virtual Object Configurations
class VirtualObjectConfiguration(Base):
    __tablename__ = 'virtual_object_configurations'

    virtual_object_config_id = Column(Integer, primary_key=True, autoincrement=True)
    virtual_object_id = Column(Integer, ForeignKey('virtual_objects.virtual_object_id'), nullable=False)
    config_id = Column(Integer, ForeignKey('configurations.config_id'), nullable=False)
    x_coordinate = Column(Integer, nullable=False)
    y_coordinate = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    last_updated = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    virtual_object = relationship("VirtualObject", back_populates="configurations")
    configuration = relationship("Configuration", back_populates="virtual_configs")

# Table: Mimic Sync Log
class MimicSyncLog(Base):
    __tablename__ = 'mimic_sync_log'

    sync_id = Column(Integer, primary_key=True, autoincrement=True)
    physical_object_id = Column(Integer, ForeignKey('physical_objects.physical_object_id'), nullable=True)
    virtual_object_id = Column(Integer, ForeignKey('virtual_objects.virtual_object_id'), nullable=True)
    config_id = Column(Integer, ForeignKey('configurations.config_id'), nullable=True)
    sync_direction = Column(String(20), CheckConstraint("sync_direction IN ('physical_to_virtual', 'virtual_to_physical')"), nullable=False)
    sync_timestamp = Column(DateTime, default=datetime.now)

class Product(Base):
    __tablename__ = 'products'

    product_id = Column(Integer, primary_key=True, autoincrement=True)
    product_name = Column(String(255))
    current_config = Column(Integer, ForeignKey('configurations.config_id'), nullable=False)

    #relationships
    configuration = relationship("Configuration", back_populates="products")