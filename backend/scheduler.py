"""
Scheduler Service - Automated Reminders
Background task scheduler for patient reminders
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Patient
from notifications import notification_service
import logging

logger = logging.getLogger(__name__)

class ReminderScheduler:
    """Automated reminder scheduler"""
    
    def __init__(self):
        """Initialize scheduler"""
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        print("✅ Reminder scheduler started")
    
    def schedule_medication_reminders(self):
        """Schedule medication reminders"""
        medication_times = ["08:00", "14:00", "20:00"]
        
        for time_str in medication_times:
            hour, minute = map(int, time_str.split(':'))
            self.scheduler.add_job(
                self.send_medication_reminders,
                CronTrigger(hour=hour, minute=minute),
                id=f'medication_{time_str}',
                replace_existing=True
            )
        
        print(f"📅 Medication reminders scheduled: {', '.join(medication_times)}")
    
    def send_medication_reminders(self):
        """Send medication reminders to all patients"""
        db = SessionLocal()
        try:
            patients = db.query(Patient).all()
            
            for patient in patients:
                contact = patient.emergency_contact or {}
                phone = contact.get('phone')
                
                if phone:
                    notification_service.send_medication_reminder(
                        patient_name=f"{patient.first_name} {patient.last_name}",
                        medication="Your prescribed medication",
                        phone=phone
                    )
            
            logger.info(f"Sent medication reminders to {len(patients)} patients")
        
        except Exception as e:
            logger.error(f"Error: {e}")
        
        finally:
            db.close()
    
    def start_all_schedules(self):
        """Start all scheduled reminders"""
        self.schedule_medication_reminders()
        print("✅ All reminder schedules activated")
    
    def stop(self):
        """Stop scheduler"""
        self.scheduler.shutdown()
        print("👋 Scheduler stopped")


# Global instance
reminder_scheduler = ReminderScheduler()