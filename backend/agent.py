# """
# Nurse Triage Agent - Main Agent File
# Clean, modular, beginner-friendly code using Gemini API
# """

# import os
# from datetime import datetime
# from google import genai
# from google.genai import types
# from dotenv import load_dotenv

# # Load environment variables
# load_dotenv()

# class NurseAgent:
#     """Main Nurse Triage Agent"""
    
#     def __init__(self):
#         """Initialize the agent with Gemini API"""
#         api_key = os.getenv('GEMINI_API_KEY')
#         if not api_key:
#             raise ValueError("GEMINI_API_KEY not found in .env file")
        
#         self.client = genai.Client(api_key=api_key)
#         self.model = 'gemini-2.0-flash-exp'
#         self.patient_data = {}
        
#     def analyze_vitals(self, vitals):
#         """
#         Analyze patient vitals and determine emergency level
#         Args:
#             vitals: dict with hr, bp, temp
#         Returns:
#             dict with analysis results
#         """
#         prompt = f"""
# You are an expert nurse. Analyze these patient vitals:

# Heart Rate: {vitals['hr']} bpm
# Blood Pressure: {vitals['bp']} mmHg
# Temperature: {vitals['temp']}°F

# Provide:
# 1. Emergency Level (CRITICAL, MODERATE, STABLE)
# 2. Brief reasoning (2 sentences max)
# 3. Immediate action needed (if any)

# Respond in this exact format:
# LEVEL: [emergency level]
# REASON: [your reasoning]
# ACTION: [recommended action]
# """
        
#         response = self.client.models.generate_content(
#             model=self.model,
#             contents=prompt
#         )
        
#         return self._parse_vitals_response(response.text)
    
#     def _parse_vitals_response(self, text):
#         """Parse Gemini response into structured data"""
#         lines = text.strip().split('\n')
#         result = {
#             'level': 'UNKNOWN',
#             'reason': '',
#             'action': ''
#         }
        
#         for line in lines:
#             if line.startswith('LEVEL:'):
#                 result['level'] = line.replace('LEVEL:', '').strip()
#             elif line.startswith('REASON:'):
#                 result['reason'] = line.replace('REASON:', '').strip()
#             elif line.startswith('ACTION:'):
#                 result['action'] = line.replace('ACTION:', '').strip()
        
#         return result
    
#     def recommend_doctor(self, diagnosis, vitals):
#         """
#         Recommend appropriate doctor based on condition
#         Args:
#             diagnosis: patient diagnosis string
#             vitals: vital signs dict
#         Returns:
#             dict with doctor recommendation
#         """
#         prompt = f"""
# Patient diagnosis: {diagnosis}
# Current vitals: HR {vitals['hr']}, BP {vitals['bp']}, Temp {vitals['temp']}°F

# Recommend the most appropriate specialist doctor and explain why in 1 sentence.

# Format:
# SPECIALIST: [doctor type]
# REASON: [why this specialist]
# """
        
#         response = self.client.models.generate_content(
#             model=self.model,
#             contents=prompt
#         )
        
#         return self._parse_doctor_response(response.text)
    
#     def _parse_doctor_response(self, text):
#         """Parse doctor recommendation response"""
#         lines = text.strip().split('\n')
#         result = {
#             'specialist': 'General Physician',
#             'reason': ''
#         }
        
#         for line in lines:
#             if line.startswith('SPECIALIST:'):
#                 result['specialist'] = line.replace('SPECIALIST:', '').strip()
#             elif line.startswith('REASON:'):
#                 result['reason'] = line.replace('REASON:', '').strip()
        
#         return result
    
#     def assess_wound(self, wound_description):
#         """
#         Assess wound and provide care instructions
#         Args:
#             wound_description: description of wound
#         Returns:
#             dict with wound assessment and care steps
#         """
#         prompt = f"""
# Wound description: {wound_description}

# As a nurse, provide:
# 1. Wound severity (MINOR, MODERATE, SEVERE)
# 2. Required care (dressing/stitching)
# 3. Simple care steps (3 steps max)

# Format:
# SEVERITY: [level]
# CARE: [dressing or stitching]
# STEPS: [step 1; step 2; step 3]
# """
        
#         response = self.client.models.generate_content(
#             model=self.model,
#             contents=prompt
#         )
        
#         return self._parse_wound_response(response.text)
    
#     def _parse_wound_response(self, text):
#         """Parse wound assessment response"""
#         lines = text.strip().split('\n')
#         result = {
#             'severity': 'MODERATE',
#             'care_type': 'dressing',
#             'steps': []
#         }
        
#         for line in lines:
#             if line.startswith('SEVERITY:'):
#                 result['severity'] = line.replace('SEVERITY:', '').strip()
#             elif line.startswith('CARE:'):
#                 result['care_type'] = line.replace('CARE:', '').strip().lower()
#             elif line.startswith('STEPS:'):
#                 steps_text = line.replace('STEPS:', '').strip()
#                 result['steps'] = [s.strip() for s in steps_text.split(';')]
        
#         return result
    
#     def guide_iv_procedure(self, procedure_type):
#         """
#         Provide guidance for IV/Injection procedures
#         Args:
#             procedure_type: 'IV', 'Injection', or 'Drip'
#         Returns:
#             dict with procedure guidance
#         """
#         prompt = f"""
# Provide simple {procedure_type} procedure guidance for a nurse.

# Give 4 key steps in this format:
# STEP1: [step]
# STEP2: [step]
# STEP3: [step]
# STEP4: [step]
# """
        
#         response = self.client.models.generate_content(
#             model=self.model,
#             contents=prompt
#         )
        
#         steps = []
#         for line in response.text.strip().split('\n'):
#             if line.startswith('STEP'):
#                 step_text = line.split(':', 1)[1].strip() if ':' in line else line
#                 steps.append(step_text)
        
#         return {'procedure': procedure_type, 'steps': steps}
    
#     def track_patient(self, patient_id, vitals, medications):
#         """
#         Track patient records and generate reminders
#         Args:
#             patient_id: patient identifier
#             vitals: current vitals dict
#             medications: list of medications
#         Returns:
#             dict with tracking info and reminders
#         """
#         current_time = datetime.now().strftime("%H:%M")
        
#         prompt = f"""
# Patient {patient_id} tracking at {current_time}:
# Vitals: HR {vitals['hr']}, BP {vitals['bp']}, Temp {vitals['temp']}°F
# Medications: {', '.join(medications)}

# Generate 2 important reminders for this patient (short, clear).

# Format:
# REMINDER1: [text]
# REMINDER2: [text]
# """
        
#         response = self.client.models.generate_content(
#             model=self.model,
#             contents=prompt
#         )
        
#         reminders = []
#         for line in response.text.strip().split('\n'):
#             if line.startswith('REMINDER'):
#                 reminder_text = line.split(':', 1)[1].strip() if ':' in line else line
#                 reminders.append(reminder_text)
        
#         return {
#             'patient_id': patient_id,
#             'tracked_at': current_time,
#             'reminders': reminders
#         }
    
#     def generate_diet_plan(self, diagnosis, allergies):
#         """
#         Generate dietary recommendations
#         Args:
#             diagnosis: patient condition
#             allergies: list of allergies
#         Returns:
#             dict with diet recommendations
#         """
#         allergies_text = ', '.join(allergies) if allergies else 'None'
        
#         prompt = f"""
# Diagnosis: {diagnosis}
# Allergies: {allergies_text}

# Suggest 3 dietary recommendations for this patient (brief, clear).

# Format:
# DIET1: [recommendation]
# DIET2: [recommendation]
# DIET3: [recommendation]
# """
        
#         response = self.client.models.generate_content(
#             model=self.model,
#             contents=prompt
#         )
        
#         recommendations = []
#         for line in response.text.strip().split('\n'):
#             if line.startswith('DIET'):
#                 diet_text = line.split(':', 1)[1].strip() if ':' in line else line
#                 recommendations.append(diet_text)
        
#         return {'recommendations': recommendations}
    
#     def create_exercise_plan(self, diagnosis, age):
#         """
#         Create exercise/physiotherapy schedule
#         Args:
#             diagnosis: patient condition
#             age: patient age
#         Returns:
#             dict with exercise plan
#         """
#         prompt = f"""
# Patient: {age} years old with {diagnosis}

# Create a simple daily exercise/physiotherapy schedule (3 activities, max 2 lines each).

# Format:
# ACTIVITY1: [time] - [activity description]
# ACTIVITY2: [time] - [activity description]
# ACTIVITY3: [time] - [activity description]
# """
        
#         response = self.client.models.generate_content(
#             model=self.model,
#             contents=prompt
#         )
        
#         activities = []
#         for line in response.text.strip().split('\n'):
#             if line.startswith('ACTIVITY'):
#                 activity_text = line.split(':', 1)[1].strip() if ':' in line else line
#                 activities.append(activity_text)
        
#         return {'schedule': activities}
    
#     def full_patient_assessment(self, patient_data):
#         """
#         Complete patient assessment - combines all agent capabilities
#         Args:
#             patient_data: dict with all patient information
#         Returns:
#             dict with complete assessment
#         """
#         vitals = patient_data.get('vitals', {})
        
#         # Analyze vitals
#         vitals_analysis = self.analyze_vitals(vitals)
        
#         # Recommend doctor
#         doctor_rec = self.recommend_doctor(
#             patient_data.get('diagnosis', 'Unknown'),
#             vitals
#         )
        
#         # Track patient
#         tracking = self.track_patient(
#             patient_data.get('patient_id', 'P000'),
#             vitals,
#             patient_data.get('medications', [])
#         )
        
#         return {
#             'patient_id': patient_data.get('patient_id'),
#             'vitals_analysis': vitals_analysis,
#             'doctor_recommendation': doctor_rec,
#             'tracking': tracking,
#             'timestamp': datetime.now().isoformat()
#         }


# # Example usage
# if __name__ == '__main__':
#     # Initialize agent
#     agent = NurseAgent()
    
#     # Sample patient data
#     sample_patient = {
#         'patient_id': 'P405',
#         'diagnosis': 'Post-MI (Heart Attack)',
#         'vitals': {
#             'hr': 118,
#             'bp': '90/60',
#             'temp': 101.5
#         },
#         'medications': ['Aspirin', 'Beta-blocker']
#     }
    
#     # Run full assessment
#     print("🏥 Starting Patient Assessment...\n")
#     assessment = agent.full_patient_assessment(sample_patient)
    
#     print(f"Patient: {assessment['patient_id']}")
#     print(f"\n🚨 Emergency Level: {assessment['vitals_analysis']['level']}")
#     print(f"💭 Reasoning: {assessment['vitals_analysis']['reason']}")
#     print(f"⚡ Action: {assessment['vitals_analysis']['action']}")
#     print(f"\n👨‍⚕️ Recommended: {assessment['doctor_recommendation']['specialist']}")
#     print(f"📋 Reason: {assessment['doctor_recommendation']['reason']}")
#     print(f"\n🔔 Reminders:")
#     for reminder in assessment['tracking']['reminders']:
#         print(f"  - {reminder}")



# """
# Nurse Triage Agent - Main Agent File
# Clean, modular, beginner-friendly code using Gemini API
# """

# import os
# from datetime import datetime
# from google import genai
# from google.genai import types
# from dotenv import load_dotenv

# # Load environment variables
# load_dotenv()

# class NurseAgent:
#     """Main Nurse Triage Agent"""
    
#     def __init__(self):
#         """Initialize the agent with Gemini API"""
#         api_key = os.getenv('GEMINI_API_KEY')
#         if not api_key:
#             raise ValueError("GEMINI_API_KEY not found in .env file")
        
#         self.client = genai.Client(api_key=api_key)
#         # Using stable model with better free tier limits
#         self.model = 'gemini-1.5-flash'
#         self.patient_data = {}
        
#     def analyze_vitals(self, vitals):
#         """
#         Analyze patient vitals and determine emergency level
#         Args:
#             vitals: dict with hr, bp, temp
#         Returns:
#             dict with analysis results
#         """
#         prompt = f"""
# You are an expert nurse. Analyze these patient vitals:

# Heart Rate: {vitals['hr']} bpm
# Blood Pressure: {vitals['bp']} mmHg
# Temperature: {vitals['temp']}°F

# Provide:
# 1. Emergency Level (CRITICAL, MODERATE, STABLE)
# 2. Brief reasoning (2 sentences max)
# 3. Immediate action needed (if any)

# Respond in this exact format:
# LEVEL: [emergency level]
# REASON: [your reasoning]
# ACTION: [recommended action]
# """
        
#         response = self.client.models.generate_content(
#             model=self.model,
#             contents=prompt
#         )
        
#         return self._parse_vitals_response(response.text)
    
#     def _parse_vitals_response(self, text):
#         """Parse Gemini response into structured data"""
#         lines = text.strip().split('\n')
#         result = {
#             'level': 'UNKNOWN',
#             'reason': '',
#             'action': ''
#         }
        
#         for line in lines:
#             if line.startswith('LEVEL:'):
#                 result['level'] = line.replace('LEVEL:', '').strip()
#             elif line.startswith('REASON:'):
#                 result['reason'] = line.replace('REASON:', '').strip()
#             elif line.startswith('ACTION:'):
#                 result['action'] = line.replace('ACTION:', '').strip()
        
#         return result
    
#     def recommend_doctor(self, diagnosis, vitals):
#         """
#         Recommend appropriate doctor based on condition
#         Args:
#             diagnosis: patient diagnosis string
#             vitals: vital signs dict
#         Returns:
#             dict with doctor recommendation
#         """
#         prompt = f"""
# Patient diagnosis: {diagnosis}
# Current vitals: HR {vitals['hr']}, BP {vitals['bp']}, Temp {vitals['temp']}°F

# Recommend the most appropriate specialist doctor and explain why in 1 sentence.

# Format:
# SPECIALIST: [doctor type]
# REASON: [why this specialist]
# """
        
#         response = self.client.models.generate_content(
#             model=self.model,
#             contents=prompt
#         )
        
#         return self._parse_doctor_response(response.text)
    
#     def _parse_doctor_response(self, text):
#         """Parse doctor recommendation response"""
#         lines = text.strip().split('\n')
#         result = {
#             'specialist': 'General Physician',
#             'reason': ''
#         }
        
#         for line in lines:
#             if line.startswith('SPECIALIST:'):
#                 result['specialist'] = line.replace('SPECIALIST:', '').strip()
#             elif line.startswith('REASON:'):
#                 result['reason'] = line.replace('REASON:', '').strip()
        
#         return result
    
#     def assess_wound(self, wound_description):
#         """
#         Assess wound and provide care instructions
#         Args:
#             wound_description: description of wound
#         Returns:
#             dict with wound assessment and care steps
#         """
#         prompt = f"""
# Wound description: {wound_description}

# As a nurse, provide:
# 1. Wound severity (MINOR, MODERATE, SEVERE)
# 2. Required care (dressing/stitching)
# 3. Simple care steps (3 steps max)

# Format:
# SEVERITY: [level]
# CARE: [dressing or stitching]
# STEPS: [step 1; step 2; step 3]
# """
        
#         response = self.client.models.generate_content(
#             model=self.model,
#             contents=prompt
#         )
        
#         return self._parse_wound_response(response.text)
    
#     def _parse_wound_response(self, text):
#         """Parse wound assessment response"""
#         lines = text.strip().split('\n')
#         result = {
#             'severity': 'MODERATE',
#             'care_type': 'dressing',
#             'steps': []
#         }
        
#         for line in lines:
#             if line.startswith('SEVERITY:'):
#                 result['severity'] = line.replace('SEVERITY:', '').strip()
#             elif line.startswith('CARE:'):
#                 result['care_type'] = line.replace('CARE:', '').strip().lower()
#             elif line.startswith('STEPS:'):
#                 steps_text = line.replace('STEPS:', '').strip()
#                 result['steps'] = [s.strip() for s in steps_text.split(';')]
        
#         return result
    
#     def guide_iv_procedure(self, procedure_type):
#         """
#         Provide guidance for IV/Injection procedures
#         Args:
#             procedure_type: 'IV', 'Injection', or 'Drip'
#         Returns:
#             dict with procedure guidance
#         """
#         prompt = f"""
# Provide simple {procedure_type} procedure guidance for a nurse.

# Give 4 key steps in this format:
# STEP1: [step]
# STEP2: [step]
# STEP3: [step]
# STEP4: [step]
# """
        
#         response = self.client.models.generate_content(
#             model=self.model,
#             contents=prompt
#         )
        
#         steps = []
#         for line in response.text.strip().split('\n'):
#             if line.startswith('STEP'):
#                 step_text = line.split(':', 1)[1].strip() if ':' in line else line
#                 steps.append(step_text)
        
#         return {'procedure': procedure_type, 'steps': steps}
    
#     def track_patient(self, patient_id, vitals, medications):
#         """
#         Track patient records and generate reminders
#         Args:
#             patient_id: patient identifier
#             vitals: current vitals dict
#             medications: list of medications
#         Returns:
#             dict with tracking info and reminders
#         """
#         current_time = datetime.now().strftime("%H:%M")
        
#         prompt = f"""
# Patient {patient_id} tracking at {current_time}:
# Vitals: HR {vitals['hr']}, BP {vitals['bp']}, Temp {vitals['temp']}°F
# Medications: {', '.join(medications)}

# Generate 2 important reminders for this patient (short, clear).

# Format:
# REMINDER1: [text]
# REMINDER2: [text]
# """
        
#         response = self.client.models.generate_content(
#             model=self.model,
#             contents=prompt
#         )
        
#         reminders = []
#         for line in response.text.strip().split('\n'):
#             if line.startswith('REMINDER'):
#                 reminder_text = line.split(':', 1)[1].strip() if ':' in line else line
#                 reminders.append(reminder_text)
        
#         return {
#             'patient_id': patient_id,
#             'tracked_at': current_time,
#             'reminders': reminders
#         }
    
#     def generate_diet_plan(self, diagnosis, allergies):
#         """
#         Generate dietary recommendations
#         Args:
#             diagnosis: patient condition
#             allergies: list of allergies
#         Returns:
#             dict with diet recommendations
#         """
#         allergies_text = ', '.join(allergies) if allergies else 'None'
        
#         prompt = f"""
# Diagnosis: {diagnosis}
# Allergies: {allergies_text}

# Suggest 3 dietary recommendations for this patient (brief, clear).

# Format:
# DIET1: [recommendation]
# DIET2: [recommendation]
# DIET3: [recommendation]
# """
        
#         response = self.client.models.generate_content(
#             model=self.model,
#             contents=prompt
#         )
        
#         recommendations = []
#         for line in response.text.strip().split('\n'):
#             if line.startswith('DIET'):
#                 diet_text = line.split(':', 1)[1].strip() if ':' in line else line
#                 recommendations.append(diet_text)
        
#         return {'recommendations': recommendations}
    
#     def create_exercise_plan(self, diagnosis, age):
#         """
#         Create exercise/physiotherapy schedule
#         Args:
#             diagnosis: patient condition
#             age: patient age
#         Returns:
#             dict with exercise plan
#         """
#         prompt = f"""
# Patient: {age} years old with {diagnosis}

# Create a simple daily exercise/physiotherapy schedule (3 activities, max 2 lines each).

# Format:
# ACTIVITY1: [time] - [activity description]
# ACTIVITY2: [time] - [activity description]
# ACTIVITY3: [time] - [activity description]
# """
        
#         response = self.client.models.generate_content(
#             model=self.model,
#             contents=prompt
#         )
        
#         activities = []
#         for line in response.text.strip().split('\n'):
#             if line.startswith('ACTIVITY'):
#                 activity_text = line.split(':', 1)[1].strip() if ':' in line else line
#                 activities.append(activity_text)
        
#         return {'schedule': activities}
    
#     def full_patient_assessment(self, patient_data):
#         """
#         Complete patient assessment - combines all agent capabilities
#         Args:
#             patient_data: dict with all patient information
#         Returns:
#             dict with complete assessment
#         """
#         vitals = patient_data.get('vitals', {})
        
#         # Analyze vitals
#         vitals_analysis = self.analyze_vitals(vitals)
        
#         # Recommend doctor
#         doctor_rec = self.recommend_doctor(
#             patient_data.get('diagnosis', 'Unknown'),
#             vitals
#         )
        
#         # Track patient
#         tracking = self.track_patient(
#             patient_data.get('patient_id', 'P000'),
#             vitals,
#             patient_data.get('medications', [])
#         )
        
#         return {
#             'patient_id': patient_data.get('patient_id'),
#             'vitals_analysis': vitals_analysis,
#             'doctor_recommendation': doctor_rec,
#             'tracking': tracking,
#             'timestamp': datetime.now().isoformat()
#         }


# # Example usage
# if __name__ == '__main__':
#     # Initialize agent
#     agent = NurseAgent()
    
#     # Sample patient data
#     sample_patient = {
#         'patient_id': 'P405',
#         'diagnosis': 'Post-MI (Heart Attack)',
#         'vitals': {
#             'hr': 118,
#             'bp': '90/60',
#             'temp': 101.5
#         },
#         'medications': ['Aspirin', 'Beta-blocker']
#     }
    
#     # Run full assessment
#     print("🏥 Starting Patient Assessment...\n")
#     assessment = agent.full_patient_assessment(sample_patient)
    
#     print(f"Patient: {assessment['patient_id']}")
#     print(f"\n🚨 Emergency Level: {assessment['vitals_analysis']['level']}")
#     print(f"💭 Reasoning: {assessment['vitals_analysis']['reason']}")
#     print(f"⚡ Action: {assessment['vitals_analysis']['action']}")
#     print(f"\n👨‍⚕️ Recommended: {assessment['doctor_recommendation']['specialist']}")
#     print(f"📋 Reason: {assessment['doctor_recommendation']['reason']}")
#     print(f"\n🔔 Reminders:")
#     for reminder in assessment['tracking']['reminders']:
#         print(f"  - {reminder}")


"""
Nurse Triage Agent - Main Agent File
Clean, modular, beginner-friendly code using Gemini API
WITH RATE LIMIT HANDLING
"""

import os
import time
from datetime import datetime
from google import genai
from google.genai import types
from google.genai.errors import ClientError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class NurseAgent:
    """Main Nurse Triage Agent with Rate Limit Handling"""
    
    def __init__(self):
        """Initialize the agent with Gemini API"""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in .env file")
        
        self.client = genai.Client(api_key=api_key)
        # Using most stable free model
        self.model = 'gemini-1.5-flash'
        self.patient_data = {}
        self.request_count = 0
        self.last_request_time = 0
    
    def _safe_api_call(self, prompt, max_retries=3):
        """
        Make API call with retry logic for rate limits
        """
        for attempt in range(max_retries):
            try:
                # Add delay between requests (minimum 5 seconds)
                current_time = time.time()
                time_since_last = current_time - self.last_request_time
                if time_since_last < 5:
                    wait_time = 5 - time_since_last
                    print(f"⏳ Waiting {wait_time:.1f}s to avoid rate limit...")
                    time.sleep(wait_time)
                
                # Make API call
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt
                )
                
                self.last_request_time = time.time()
                self.request_count += 1
                return response.text
                
            except ClientError as e:
                if '429' in str(e):  # Rate limit error
                    if attempt < max_retries - 1:
                        wait_time = 60 * (attempt + 1)  # 60s, 120s, 180s
                        print(f"⚠️ Rate limit hit. Waiting {wait_time}s... (Attempt {attempt + 1}/{max_retries})")
                        time.sleep(wait_time)
                    else:
                        print("❌ Rate limit exceeded. Solutions:")
                        print("   1. Wait 1 hour and try again")
                        print("   2. Generate new API key: https://aistudio.google.com/app/apikey")
                        print("   3. Use different Google account")
                        raise
                else:
                    raise
            except Exception as e:
                print(f"❌ Error: {str(e)}")
                raise
        
        return None
    
    def analyze_vitals(self, vitals):
        """
        Analyze patient vitals and determine emergency level
        Args:
            vitals: dict with hr, bp, temp
        Returns:
            dict with analysis results
        """
        prompt = f"""
You are an expert nurse. Analyze these patient vitals:

Heart Rate: {vitals['hr']} bpm
Blood Pressure: {vitals['bp']} mmHg
Temperature: {vitals['temp']}°F

Provide:
1. Emergency Level (CRITICAL, MODERATE, STABLE)
2. Brief reasoning (2 sentences max)
3. Immediate action needed (if any)

Respond in this exact format:
LEVEL: [emergency level]
REASON: [your reasoning]
ACTION: [recommended action]
"""
        
        response_text = self._safe_api_call(prompt)
        if response_text:
            return self._parse_vitals_response(response_text)
        return {'level': 'UNKNOWN', 'reason': 'API call failed', 'action': 'Manual assessment required'}
    
    def _parse_vitals_response(self, text):
        """Parse Gemini response into structured data"""
        lines = text.strip().split('\n')
        result = {
            'level': 'UNKNOWN',
            'reason': '',
            'action': ''
        }
        
        for line in lines:
            if line.startswith('LEVEL:'):
                result['level'] = line.replace('LEVEL:', '').strip()
            elif line.startswith('REASON:'):
                result['reason'] = line.replace('REASON:', '').strip()
            elif line.startswith('ACTION:'):
                result['action'] = line.replace('ACTION:', '').strip()
        
        return result
    
    def recommend_doctor(self, diagnosis, vitals):
        """
        Recommend appropriate doctor based on condition
        Args:
            diagnosis: patient diagnosis string
            vitals: vital signs dict
        Returns:
            dict with doctor recommendation
        """
        prompt = f"""
Patient diagnosis: {diagnosis}
Current vitals: HR {vitals['hr']}, BP {vitals['bp']}, Temp {vitals['temp']}°F

Recommend the most appropriate specialist doctor and explain why in 1 sentence.

Format:
SPECIALIST: [doctor type]
REASON: [why this specialist]
"""
        
        response_text = self._safe_api_call(prompt)
        if response_text:
            return self._parse_doctor_response(response_text)
        return {'specialist': 'General Physician', 'reason': 'Default recommendation'}
    
    def _parse_doctor_response(self, text):
        """Parse doctor recommendation response"""
        lines = text.strip().split('\n')
        result = {
            'specialist': 'General Physician',
            'reason': ''
        }
        
        for line in lines:
            if line.startswith('SPECIALIST:'):
                result['specialist'] = line.replace('SPECIALIST:', '').strip()
            elif line.startswith('REASON:'):
                result['reason'] = line.replace('REASON:', '').strip()
        
        return result
    
    def assess_wound(self, wound_description):
        """
        Assess wound and provide care instructions
        Args:
            wound_description: description of wound
        Returns:
            dict with wound assessment and care steps
        """
        prompt = f"""
Wound description: {wound_description}

As a nurse, provide:
1. Wound severity (MINOR, MODERATE, SEVERE)
2. Required care (dressing/stitching)
3. Simple care steps (3 steps max)

Format:
SEVERITY: [level]
CARE: [dressing or stitching]
STEPS: [step 1; step 2; step 3]
"""
        
        response_text = self._safe_api_call(prompt)
        if response_text:
            return self._parse_wound_response(response_text)
        return {'severity': 'MODERATE', 'care_type': 'dressing', 'steps': ['Clean wound', 'Apply sterile dressing', 'Monitor for infection']}
    
    def _parse_wound_response(self, text):
        """Parse wound assessment response"""
        lines = text.strip().split('\n')
        result = {
            'severity': 'MODERATE',
            'care_type': 'dressing',
            'steps': []
        }
        
        for line in lines:
            if line.startswith('SEVERITY:'):
                result['severity'] = line.replace('SEVERITY:', '').strip()
            elif line.startswith('CARE:'):
                result['care_type'] = line.replace('CARE:', '').strip().lower()
            elif line.startswith('STEPS:'):
                steps_text = line.replace('STEPS:', '').strip()
                result['steps'] = [s.strip() for s in steps_text.split(';')]
        
        return result
    
    def guide_iv_procedure(self, procedure_type):
        """
        Provide guidance for IV/Injection procedures
        Args:
            procedure_type: 'IV', 'Injection', or 'Drip'
        Returns:
            dict with procedure guidance
        """
        prompt = f"""
Provide simple {procedure_type} procedure guidance for a nurse.

Give 4 key steps in this format:
STEP1: [step]
STEP2: [step]
STEP3: [step]
STEP4: [step]
"""
        
        response_text = self._safe_api_call(prompt)
        if not response_text:
            return {'procedure': procedure_type, 'steps': ['Prepare equipment', 'Follow sterile technique', 'Administer as prescribed', 'Monitor patient']}
        
        steps = []
        for line in response_text.strip().split('\n'):
            if line.startswith('STEP'):
                step_text = line.split(':', 1)[1].strip() if ':' in line else line
                steps.append(step_text)
        
        return {'procedure': procedure_type, 'steps': steps}
    
    def track_patient(self, patient_id, vitals, medications):
        """
        Track patient records and generate reminders
        Args:
            patient_id: patient identifier
            vitals: current vitals dict
            medications: list of medications
        Returns:
            dict with tracking info and reminders
        """
        current_time = datetime.now().strftime("%H:%M")
        
        prompt = f"""
Patient {patient_id} tracking at {current_time}:
Vitals: HR {vitals['hr']}, BP {vitals['bp']}, Temp {vitals['temp']}°F
Medications: {', '.join(medications)}

Generate 2 important reminders for this patient (short, clear).

Format:
REMINDER1: [text]
REMINDER2: [text]
"""
        
        response_text = self._safe_api_call(prompt)
        reminders = []
        
        if response_text:
            for line in response_text.strip().split('\n'):
                if line.startswith('REMINDER'):
                    reminder_text = line.split(':', 1)[1].strip() if ':' in line else line
                    reminders.append(reminder_text)
        else:
            reminders = ['Monitor vitals regularly', 'Administer medications on schedule']
        
        return {
            'patient_id': patient_id,
            'tracked_at': current_time,
            'reminders': reminders
        }
    
    def generate_diet_plan(self, diagnosis, allergies):
        """
        Generate dietary recommendations
        Args:
            diagnosis: patient condition
            allergies: list of allergies
        Returns:
            dict with diet recommendations
        """
        allergies_text = ', '.join(allergies) if allergies else 'None'
        
        prompt = f"""
Diagnosis: {diagnosis}
Allergies: {allergies_text}

Suggest 3 dietary recommendations for this patient (brief, clear).

Format:
DIET1: [recommendation]
DIET2: [recommendation]
DIET3: [recommendation]
"""
        
        response_text = self._safe_api_call(prompt)
        recommendations = []
        
        if response_text:
            for line in response_text.strip().split('\n'):
                if line.startswith('DIET'):
                    diet_text = line.split(':', 1)[1].strip() if ':' in line else line
                    recommendations.append(diet_text)
        else:
            recommendations = ['Balanced nutrition', 'Adequate hydration', 'Follow doctor\'s dietary advice']
        
        return {'recommendations': recommendations}
    
    def create_exercise_plan(self, diagnosis, age):
        """
        Create exercise/physiotherapy schedule
        Args:
            diagnosis: patient condition
            age: patient age
        Returns:
            dict with exercise plan
        """
        prompt = f"""
Patient: {age} years old with {diagnosis}

Create a simple daily exercise/physiotherapy schedule (3 activities, max 2 lines each).

Format:
ACTIVITY1: [time] - [activity description]
ACTIVITY2: [time] - [activity description]
ACTIVITY3: [time] - [activity description]
"""
        
        response_text = self._safe_api_call(prompt)
        activities = []
        
        if response_text:
            for line in response_text.strip().split('\n'):
                if line.startswith('ACTIVITY'):
                    activity_text = line.split(':', 1)[1].strip() if ':' in line else line
                    activities.append(activity_text)
        else:
            activities = ['Morning: Gentle breathing exercises', 'Afternoon: Short walk with assistance', 'Evening: Range of motion exercises']
        
        return {'schedule': activities}
    
    def full_patient_assessment(self, patient_data):
        """
        Complete patient assessment - combines all agent capabilities
        Args:
            patient_data: dict with all patient information
        Returns:
            dict with complete assessment
        """
        vitals = patient_data.get('vitals', {})
        
        print(f"📊 Analyzing patient {patient_data.get('patient_id')}...")
        
        # Analyze vitals
        print("   → Analyzing vitals...")
        vitals_analysis = self.analyze_vitals(vitals)
        
        # Recommend doctor
        print("   → Recommending specialist...")
        doctor_rec = self.recommend_doctor(
            patient_data.get('diagnosis', 'Unknown'),
            vitals
        )
        
        # Track patient
        print("   → Generating reminders...")
        tracking = self.track_patient(
            patient_data.get('patient_id', 'P000'),
            vitals,
            patient_data.get('medications', [])
        )
        
        print("✅ Assessment complete!")
        
        return {
            'patient_id': patient_data.get('patient_id'),
            'vitals_analysis': vitals_analysis,
            'doctor_recommendation': doctor_rec,
            'tracking': tracking,
            'timestamp': datetime.now().isoformat()
        }


# Example usage
if __name__ == '__main__':
    try:
        # Initialize agent
        agent = NurseAgent()
        
        # Sample patient data
        sample_patient = {
            'patient_id': 'P405',
            'diagnosis': 'Post-MI (Heart Attack)',
            'vitals': {
                'hr': 118,
                'bp': '90/60',
                'temp': 101.5
            },
            'medications': ['Aspirin', 'Beta-blocker']
        }
        
        # Run full assessment
        print("🏥 Starting Patient Assessment...\n")
        assessment = agent.full_patient_assessment(sample_patient)
        
        print(f"\n{'='*50}")
        print(f"Patient: {assessment['patient_id']}")
        print(f"{'='*50}")
        print(f"\n🚨 Emergency Level: {assessment['vitals_analysis']['level']}")
        print(f"💭 Reasoning: {assessment['vitals_analysis']['reason']}")
        print(f"⚡ Action: {assessment['vitals_analysis']['action']}")
        print(f"\n👨‍⚕️ Recommended: {assessment['doctor_recommendation']['specialist']}")
        print(f"📋 Reason: {assessment['doctor_recommendation']['reason']}")
        print(f"\n🔔 Reminders:")
        for reminder in assessment['tracking']['reminders']:
            print(f"  - {reminder}")
        
        print(f"\n✅ Total API calls made: {agent.request_count}")
        
    except Exception as e:
        print(f"\n❌ Error occurred: {str(e)}")
        print("\n🔧 Troubleshooting steps:")
        print("1. Generate NEW API key: https://aistudio.google.com/app/apikey")
        print("2. Update .env file with new key")
        print("3. Try again after 1 hour (daily quota reset)")
        print("4. Or use different Google account")