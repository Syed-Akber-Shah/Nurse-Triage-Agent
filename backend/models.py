# Database tables
"""
Database Models for Nurse Triage System
SQLAlchemy ORM models
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Patient(Base):
    """Patient information table"""
    __tablename__ = 'patients'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(String(50), unique=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(String(20), nullable=False)
    gender = Column(String(20), nullable=False)
    blood_group = Column(String(10))
    room_number = Column(String(50), nullable=False)
    bed_number = Column(String(20))
    admission_date = Column(String(50), nullable=False)
    diagnosis = Column(Text, nullable=False)
    allergies = Column(String(500))
    emergency_contact = Column(JSON)  # Store as JSON
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    vitals = relationship("VitalSigns", back_populates="patient", cascade="all, delete-orphan")
    assessments = relationship("Assessment", back_populates="patient", cascade="all, delete-orphan")
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'date_of_birth': self.date_of_birth,
            'gender': self.gender,
            'blood_group': self.blood_group,
            'room_number': self.room_number,
            'bed_number': self.bed_number,
            'admission_date': self.admission_date,
            'diagnosis': self.diagnosis,
            'allergies': self.allergies,
            'emergency_contact': self.emergency_contact,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class VitalSigns(Base):
    """Patient vital signs table"""
    __tablename__ = 'vital_signs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(String(50), ForeignKey('patients.patient_id'), nullable=False)
    heart_rate = Column(Integer, nullable=False)
    blood_pressure = Column(String(20), nullable=False)
    temperature = Column(Float, nullable=False)
    recorded_by = Column(String(100))
    recorded_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    patient = relationship("Patient", back_populates="vitals")
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'heart_rate': self.heart_rate,
            'blood_pressure': self.blood_pressure,
            'temperature': self.temperature,
            'recorded_by': self.recorded_by,
            'recorded_at': self.recorded_at.isoformat() if self.recorded_at else None
        }


class Assessment(Base):
    """AI Assessment results table"""
    __tablename__ = 'assessments'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(String(50), ForeignKey('patients.patient_id'), nullable=False)
    emergency_level = Column(String(20))  # CRITICAL, MODERATE, STABLE
    reasoning = Column(Text)
    recommended_action = Column(Text)
    recommended_specialist = Column(String(100))
    specialist_reason = Column(Text)
    assessment_data = Column(JSON)  # Store complete AI response
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    patient = relationship("Patient", back_populates="assessments")
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'emergency_level': self.emergency_level,
            'reasoning': self.reasoning,
            'recommended_action': self.recommended_action,
            'recommended_specialist': self.recommended_specialist,
            'specialist_reason': self.specialist_reason,
            'assessment_data': self.assessment_data,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class AuditLog(Base):
    """System audit log table"""
    __tablename__ = 'audit_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(String(50))
    action = Column(String(100), nullable=False)
    description = Column(Text)
    user = Column(String(100))
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'action': self.action,
            'description': self.description,
            'user': self.user,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }