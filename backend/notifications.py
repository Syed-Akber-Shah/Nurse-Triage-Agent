"""
Notification Service - SMS & Email
Handles all patient reminders and alerts
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from datetime import datetime
from config import settings

class NotificationService:
    """Handle SMS and Email notifications"""
    
    def __init__(self):
        """Initialize notification service"""
        self.twilio_enabled = bool(settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN)
        self.email_enabled = bool(settings.SMTP_USERNAME and settings.SMTP_PASSWORD)
        
        # Initialize Twilio client if credentials available
        if self.twilio_enabled:
            try:
                from twilio.rest import Client
                self.twilio_client = Client(
                    settings.TWILIO_ACCOUNT_SID,
                    settings.TWILIO_AUTH_TOKEN
                )
                print("✅ Twilio SMS service initialized")
            except ImportError:
                print("⚠️ Twilio not installed. Run: pip install twilio")
                self.twilio_enabled = False
            except Exception as e:
                print(f"⚠️ Twilio initialization failed: {e}")
                self.twilio_enabled = False
        else:
            print("ℹ️ Twilio SMS not configured (optional)")
    
    def send_sms(self, phone_number: str, message: str) -> dict:
        """
        Send SMS notification
        Args:
            phone_number: Recipient phone (+923001234567 format)
            message: SMS text
        Returns:
            dict with status and message_id
        """
        if not self.twilio_enabled:
            print("⚠️ SMS not sent: Twilio not configured")
            return {"status": "skipped", "reason": "Twilio not configured"}
        
        try:
            message = self.twilio_client.messages.create(
                body=message,
                from_=settings.TWILIO_PHONE_NUMBER,
                to=phone_number
            )
            
            print(f"✅ SMS sent to {phone_number}: {message.sid}")
            return {
                "status": "success",
                "message_id": message.sid,
                "phone": phone_number
            }
        
        except Exception as e:
            print(f"❌ SMS failed: {str(e)}")
            return {
                "status": "failed",
                "error": str(e)
            }
    
    def send_email(self, to_email: str, subject: str, body: str, html_body: Optional[str] = None) -> dict:
        """
        Send email notification
        Args:
            to_email: Recipient email
            subject: Email subject
            body: Plain text body
            html_body: HTML formatted body (optional)
        Returns:
            dict with status
        """
        if not self.email_enabled:
            print("⚠️ Email not sent: SMTP not configured")
            return {"status": "skipped", "reason": "SMTP not configured"}
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = settings.SMTP_USERNAME
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add plain text
            msg.attach(MIMEText(body, 'plain'))
            
            # Add HTML if provided
            if html_body:
                msg.attach(MIMEText(html_body, 'html'))
            
            # Send email
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
                server.send_message(msg)
            
            print(f"✅ Email sent to {to_email}")
            return {
                "status": "success",
                "to": to_email,
                "subject": subject
            }
        
        except Exception as e:
            print(f"❌ Email failed: {str(e)}")
            return {
                "status": "failed",
                "error": str(e)
            }
    
    def send_medication_reminder(self, patient_name: str, medication: str, 
                                  phone: Optional[str] = None, 
                                  email: Optional[str] = None) -> dict:
        """Send medication reminder via SMS and/or Email"""
        
        current_time = datetime.now().strftime("%I:%M %p")
        
        # SMS message
        sms_text = f"🏥 Reminder: {patient_name}, it's time for your medication: {medication}. Time: {current_time}"
        
        # Email content
        email_subject = f"Medication Reminder - {medication}"
        email_body = f"""
Dear {patient_name},

This is a reminder to take your medication:

Medication: {medication}
Time: {current_time}

Please take your medication as prescribed by your doctor.

Best regards,
Nurse Triage System
"""
        
        email_html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; }}
        .container {{ max-width: 600px; margin: 20px auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px; }}
        .header {{ background-color: #0d6efd; color: white; padding: 15px; border-radius: 5px; }}
        .content {{ padding: 20px; }}
        .medication {{ background-color: #f8f9fa; padding: 15px; margin: 15px 0; border-left: 4px solid #28a745; }}
        .footer {{ color: #666; font-size: 12px; margin-top: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>🏥 Medication Reminder</h2>
        </div>
        <div class="content">
            <p>Dear {patient_name},</p>
            <p>This is a reminder to take your medication:</p>
            <div class="medication">
                <strong>Medication:</strong> {medication}<br>
                <strong>Time:</strong> {current_time}
            </div>
            <p>Please take your medication as prescribed by your doctor.</p>
        </div>
        <div class="footer">
            <p>Best regards,<br>Nurse Triage System</p>
        </div>
    </div>
</body>
</html>
"""
        
        results = {}
        
        # Send SMS
        if phone:
            results['sms'] = self.send_sms(phone, sms_text)
        
        # Send Email
        if email:
            results['email'] = self.send_email(email, email_subject, email_body, email_html)
        
        return results
    
    def send_vitals_check_reminder(self, patient_name: str, 
                                    phone: Optional[str] = None, 
                                    email: Optional[str] = None) -> dict:
        """Send vitals check reminder"""
        
        sms_text = f"🏥 Reminder: {patient_name}, please check your vitals (BP, HR, Temperature). Report to nurse station."
        
        email_subject = "Vitals Check Reminder"
        email_body = f"""
Dear {patient_name},

This is a reminder to check your vital signs:

• Blood Pressure
• Heart Rate
• Temperature

Please report to the nurse station for vitals monitoring.

Best regards,
Nurse Triage System
"""
        
        results = {}
        
        if phone:
            results['sms'] = self.send_sms(phone, sms_text)
        
        if email:
            results['email'] = self.send_email(email, email_subject, email_body)
        
        return results
    
    def send_critical_alert(self, patient_id: str, patient_name: str, 
                           emergency_level: str, reasoning: str,
                           doctor_phone: Optional[str] = None,
                           doctor_email: Optional[str] = None) -> dict:
        """Send critical patient alert to doctor"""
        
        sms_text = f"🚨 CRITICAL ALERT: Patient {patient_id} ({patient_name}) - {emergency_level}. {reasoning[:100]}... Check dashboard immediately."
        
        email_subject = f"🚨 CRITICAL ALERT - Patient {patient_id}"
        email_body = f"""
CRITICAL PATIENT ALERT

Patient ID: {patient_id}
Patient Name: {patient_name}
Emergency Level: {emergency_level}

Reasoning: {reasoning}

ACTION REQUIRED: Please check the patient immediately and review the triage dashboard.

Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

Best regards,
Nurse Triage System
"""
        
        email_html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; }}
        .container {{ max-width: 600px; margin: 20px auto; padding: 20px; border: 3px solid #d9534f; border-radius: 8px; }}
        .header {{ background-color: #d9534f; color: white; padding: 15px; border-radius: 5px; }}
        .alert {{ background-color: #f2dede; padding: 15px; margin: 15px 0; border-left: 4px solid #d9534f; }}
        .info {{ padding: 10px; background-color: #f8f9fa; margin: 10px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>🚨 CRITICAL PATIENT ALERT</h2>
        </div>
        <div class="alert">
            <p><strong>Patient ID:</strong> {patient_id}</p>
            <p><strong>Patient Name:</strong> {patient_name}</p>
            <p><strong>Emergency Level:</strong> {emergency_level}</p>
        </div>
        <div class="info">
            <p><strong>Reasoning:</strong></p>
            <p>{reasoning}</p>
        </div>
        <p style="color: #d9534f;"><strong>ACTION REQUIRED:</strong> Please check the patient immediately.</p>
        <p style="color: #666; font-size: 12px;">Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
    </div>
</body>
</html>
"""
        
        results = {}
        
        if doctor_phone:
            results['sms'] = self.send_sms(doctor_phone, sms_text)
        
        if doctor_email:
            results['email'] = self.send_email(doctor_email, email_subject, email_body, email_html)
        
        return results
    
    def send_diet_reminder(self, patient_name: str, diet_item: str,
                          phone: Optional[str] = None,
                          email: Optional[str] = None) -> dict:
        """Send diet/meal reminder"""
        
        sms_text = f"🍽️ Diet Reminder: {patient_name}, time for your meal: {diet_item}. Follow your prescribed diet plan."
        
        email_subject = "Diet Reminder"
        email_body = f"""
Dear {patient_name},

Diet Reminder: {diet_item}

Please follow your prescribed diet plan as recommended by your doctor.

Best regards,
Nurse Triage System
"""
        
        results = {}
        
        if phone:
            results['sms'] = self.send_sms(phone, sms_text)
        
        if email:
            results['email'] = self.send_email(email, email_subject, email_body)
        
        return results
    
    def send_exercise_reminder(self, patient_name: str, exercise: str,
                              phone: Optional[str] = None,
                              email: Optional[str] = None) -> dict:
        """Send exercise/physiotherapy reminder"""
        
        sms_text = f"🏃 Exercise Reminder: {patient_name}, it's time for: {exercise}. Follow your physiotherapy schedule."
        
        email_subject = "Exercise/Physiotherapy Reminder"
        email_body = f"""
Dear {patient_name},

Exercise Reminder: {exercise}

Please follow your prescribed physiotherapy schedule.

Best regards,
Nurse Triage System
"""
        
        results = {}
        
        if phone:
            results['sms'] = self.send_sms(phone, sms_text)
        
        if email:
            results['email'] = self.send_email(email, email_subject, email_body)
        
        return results


# Initialize global notification service
notification_service = NotificationService()