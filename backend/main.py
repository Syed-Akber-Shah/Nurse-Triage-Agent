# FastAPI server (REST APIs)
"""
FastAPI Backend Server
Complete REST API for Nurse Triage System
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from contextlib import asynccontextmanager

from database import get_db, init_db
from models import Patient, VitalSigns, Assessment, AuditLog
from agent import NurseAgent
from config import settings

from notifications import notification_service
from scheduler import reminder_scheduler

# Initialize database on startup (Modern lifespan method)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    print("🚀 Server started successfully!")

    # Start reminder scheduler
    reminder_scheduler.start_all_schedules()

    yield

    # Shutdown
    reminder_scheduler.stop()
    print("👋 Server shutting down...")

# Initialize FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description=settings.API_DESCRIPTION,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AI Agent
agent = NurseAgent()

# Update FastAPI app initialization
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description=settings.API_DESCRIPTION,
    lifespan=lifespan  # Add this line
)
# ============================================
# Pydantic Models (Request/Response schemas)
# ============================================

class PatientCreate(BaseModel):
    patient_id: str
    first_name: str
    last_name: str
    date_of_birth: str
    gender: str
    blood_group: Optional[str] = None
    room_number: str
    bed_number: Optional[str] = None
    admission_date: str
    diagnosis: str
    allergies: Optional[str] = None
    emergency_contact: Optional[dict] = None

class VitalsCreate(BaseModel):
    patient_id: str
    heart_rate: int
    blood_pressure: str
    temperature: float
    recorded_by: Optional[str] = "System"

class VitalsAnalyzeRequest(BaseModel):
    hr: int
    bp: str
    temp: float

# ============================================
# API Endpoints
# ============================================

@app.get("/")
async def root():
    """Root endpoint - API info"""
    return {
        "message": "Nurse Triage API",
        "version": settings.API_VERSION,
        "status": "running",
        "endpoints": {
            "patients": "/api/patients",
            "vitals": "/api/vitals",
            "assessments": "/api/assessments",
            "docs": "/docs"
        }
    }

# ============================================
# Patient Endpoints
# ============================================

@app.post("/api/patients/register")
async def register_patient(patient_data: PatientCreate, db: Session = Depends(get_db)):
    """Register new patient"""
    try:
        # Check if patient already exists
        existing = db.query(Patient).filter(Patient.patient_id == patient_data.patient_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Patient ID already exists")
        
        # Create new patient
        new_patient = Patient(**patient_data.dict())
        db.add(new_patient)
        db.commit()
        db.refresh(new_patient)
        
        # Log action
        log = AuditLog(
            patient_id=patient_data.patient_id,
            action="PATIENT_REGISTERED",
            description=f"New patient registered: {patient_data.first_name} {patient_data.last_name}",
            user="Admin"
        )
        db.add(log)
        db.commit()
        
        return {
            "status": "success",
            "message": "Patient registered successfully",
            "patient": new_patient.to_dict()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/api/patients/{patient_id}")
async def get_patient(patient_id: str, db: Session = Depends(get_db)):
    """Get patient by ID"""
    patient = db.query(Patient).filter(Patient.patient_id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient.to_dict()

@app.get("/api/patients")
async def get_all_patients(db: Session = Depends(get_db)):
    """Get all patients"""
    patients = db.query(Patient).all()
    return [p.to_dict() for p in patients]

# ============================================
# Vitals Endpoints
# ============================================

@app.post("/api/vitals/record")
async def record_vitals(vitals_data: VitalsCreate, db: Session = Depends(get_db)):
    """Record patient vitals"""
    try:
        # Check if patient exists
        patient = db.query(Patient).filter(Patient.patient_id == vitals_data.patient_id).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        # Save vitals
        new_vitals = VitalSigns(**vitals_data.dict())
        db.add(new_vitals)
        db.commit()
        db.refresh(new_vitals)
        
        # Analyze with AI
        analysis = agent.analyze_vitals({
            'hr': vitals_data.heart_rate,
            'bp': vitals_data.blood_pressure,
            'temp': vitals_data.temperature
        })
        
        # Get doctor recommendation
        doctor_rec = agent.recommend_doctor(
            patient.diagnosis,
            {
                'hr': vitals_data.heart_rate,
                'bp': vitals_data.blood_pressure,
                'temp': vitals_data.temperature
            }
        )
        
        # Save assessment
        assessment = Assessment(
            patient_id=vitals_data.patient_id,
            emergency_level=analysis['level'],
            reasoning=analysis['reason'],
            recommended_action=analysis['action'],
            recommended_specialist=doctor_rec['specialist'],
            specialist_reason=doctor_rec['reason'],
            assessment_data={
                'vitals': vitals_data.dict(),
                'analysis': analysis,
                'doctor_recommendation': doctor_rec
            }
        )
        db.add(assessment)
        db.commit()
        
        # Log action
        log = AuditLog(
            patient_id=vitals_data.patient_id,
            action="VITALS_RECORDED",
            description=f"Vitals recorded - Level: {analysis['level']}",
            user=vitals_data.recorded_by
        )
        db.add(log)
        db.commit()
        
        return {
            "status": "success",
            "vitals": new_vitals.to_dict(),
            "analysis": analysis,
            "doctor_recommendation": doctor_rec
        }
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post("/api/vitals/analyze")
async def analyze_vitals(vitals: VitalsAnalyzeRequest):
    """Analyze vitals without saving to database"""
    try:
        result = agent.analyze_vitals({
            'hr': vitals.hr,
            'bp': vitals.bp,
            'temp': vitals.temp
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/api/vitals/{patient_id}/latest")
async def get_latest_vitals(patient_id: str, db: Session = Depends(get_db)):
    """Get latest vitals for a patient"""
    vitals = db.query(VitalSigns).filter(
        VitalSigns.patient_id == patient_id
    ).order_by(VitalSigns.recorded_at.desc()).first()
    
    if not vitals:
        raise HTTPException(status_code=404, detail="No vitals found for this patient")
    
    return vitals.to_dict()

@app.get("/api/vitals/{patient_id}/history")
async def get_vitals_history(patient_id: str, db: Session = Depends(get_db)):
    """Get vitals history for a patient"""
    vitals = db.query(VitalSigns).filter(
        VitalSigns.patient_id == patient_id
    ).order_by(VitalSigns.recorded_at.desc()).all()
    
    return [v.to_dict() for v in vitals]

# ============================================
# Assessment Endpoints
# ============================================

@app.get("/api/assessments/{patient_id}")
async def get_assessments(patient_id: str, db: Session = Depends(get_db)):
    """Get all assessments for a patient"""
    assessments = db.query(Assessment).filter(
        Assessment.patient_id == patient_id
    ).order_by(Assessment.created_at.desc()).all()
    
    return [a.to_dict() for a in assessments]

@app.get("/api/assessments/{patient_id}/latest")
async def get_latest_assessment(patient_id: str, db: Session = Depends(get_db)):
    """Get latest assessment for a patient"""
    assessment = db.query(Assessment).filter(
        Assessment.patient_id == patient_id
    ).order_by(Assessment.created_at.desc()).first()
    
    if not assessment:
        raise HTTPException(status_code=404, detail="No assessment found")
    
    return assessment.to_dict()

# ============================================
# Agent Capabilities Endpoints
# ============================================

@app.post("/api/agent/assess-wound")
async def assess_wound(wound_description: str):
    """Assess wound and provide care instructions"""
    try:
        result = agent.assess_wound(wound_description)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post("/api/agent/iv-guidance")
async def iv_guidance(procedure_type: str):
    """Get IV/Injection procedure guidance"""
    try:
        result = agent.guide_iv_procedure(procedure_type)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post("/api/agent/diet-plan")
async def generate_diet_plan(diagnosis: str, allergies: List[str] = []):
    """Generate diet plan"""
    try:
        result = agent.generate_diet_plan(diagnosis, allergies)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post("/api/agent/exercise-plan")
async def generate_exercise_plan(diagnosis: str, age: int):
    """Generate exercise plan"""
    try:
        result = agent.create_exercise_plan(diagnosis, age)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# ============================================
# Audit Log Endpoints
# ============================================

@app.get("/api/audit-logs")
async def get_audit_logs(limit: int = 50, db: Session = Depends(get_db)):
    """Get recent audit logs"""
    logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(limit).all()
    return [log.to_dict() for log in logs]

@app.get("/api/audit-logs/{patient_id}")
async def get_patient_audit_logs(patient_id: str, db: Session = Depends(get_db)):
    """Get audit logs for specific patient"""
    logs = db.query(AuditLog).filter(
        AuditLog.patient_id == patient_id
    ).order_by(AuditLog.timestamp.desc()).all()
    return [log.to_dict() for log in logs]

# ============================================
# Health Check
# ============================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "database": "connected",
        "ai_agent": "active"
    }

# ============================================
# Notification Endpoints
# ============================================

class NotificationRequest(BaseModel):
    patient_id: str
    type: str  # medication, vitals, diet, exercise
    phone: Optional[str] = None
    email: Optional[str] = None
    message: Optional[str] = None

@app.post("/api/notifications/send")
async def send_notification(notification: NotificationRequest, db: Session = Depends(get_db)):
    """Send manual notification to patient"""
    try:
        # Get patient
        patient = db.query(Patient).filter(Patient.patient_id == notification.patient_id).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        patient_name = f"{patient.first_name} {patient.last_name}"
        
        # Get contact info
        contact = patient.emergency_contact or {}
        phone = notification.phone or contact.get('phone')
        email = notification.email or contact.get('email')
        
        result = {}
        
        # Send based on type
        if notification.type == "medication":
            message = notification.message or "Take your prescribed medication"
            result = notification_service.send_medication_reminder(
                patient_name=patient_name,
                medication=message,
                phone=phone,
                email=email
            )
        
        elif notification.type == "vitals":
            result = notification_service.send_vitals_check_reminder(
                patient_name=patient_name,
                phone=phone,
                email=email
            )
        
        elif notification.type == "diet":
            message = notification.message or "Follow your diet plan"
            result = notification_service.send_diet_reminder(
                patient_name=patient_name,
                diet_item=message,
                phone=phone,
                email=email
            )
        
        elif notification.type == "exercise":
            message = notification.message or "Complete your exercise routine"
            result = notification_service.send_exercise_reminder(
                patient_name=patient_name,
                exercise=message,
                phone=phone,
                email=email
            )
        
        else:
            raise HTTPException(status_code=400, detail="Invalid notification type")
        
        # Log notification
        log = AuditLog(
            patient_id=notification.patient_id,
            action=f"NOTIFICATION_SENT_{notification.type.upper()}",
            description=f"Notification sent: {notification.type}",
            user="System"
        )
        db.add(log)
        db.commit()
        
        return {
            "status": "success",
            "notification_type": notification.type,
            "results": result
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post("/api/notifications/critical-alert")
async def send_critical_alert(patient_id: str, doctor_phone: Optional[str] = None, 
                              doctor_email: Optional[str] = None, 
                              db: Session = Depends(get_db)):
    """Send critical alert to doctor"""
    try:
        # Get patient and latest assessment
        patient = db.query(Patient).filter(Patient.patient_id == patient_id).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        assessment = db.query(Assessment).filter(
            Assessment.patient_id == patient_id
        ).order_by(Assessment.created_at.desc()).first()
        
        if not assessment or assessment.emergency_level != "CRITICAL":
            raise HTTPException(status_code=400, detail="No critical assessment found")
        
        patient_name = f"{patient.first_name} {patient.last_name}"
        
        result = notification_service.send_critical_alert(
            patient_id=patient_id,
            patient_name=patient_name,
            emergency_level=assessment.emergency_level,
            reasoning=assessment.reasoning,
            doctor_phone=doctor_phone,
            doctor_email=doctor_email
        )
        
        # Log alert
        log = AuditLog(
            patient_id=patient_id,
            action="CRITICAL_ALERT_SENT",
            description=f"Critical alert sent to doctor",
            user="System"
        )
        db.add(log)
        db.commit()
        
        return {
            "status": "success",
            "alert_type": "critical",
            "results": result
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/api/notifications/status")
async def notification_status():
    """Check notification service status"""
    return {
        "sms_enabled": notification_service.twilio_enabled,
        "email_enabled": notification_service.email_enabled,
        "scheduler_active": reminder_scheduler.scheduler.running,
        "scheduled_jobs": len(reminder_scheduler.scheduler.get_jobs())
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)