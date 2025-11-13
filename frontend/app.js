/**
 * ============================================
 * NURSE TRIAGE DASHBOARD - APPLICATION LOGIC
 * ============================================
 */

// ============================================
// CONFIGURATION & CONSTANTS
// ============================================

const CONFIG = {
    API_BASE_URL: 'http://localhost:8000',
    CURRENT_PATIENT_ID: 'P405',
    VITALS_REFRESH_INTERVAL: 30000,
    LOG_MAX_ENTRIES: 10,
    ADMIN_PASSWORD: 'admin123'  // Change this in production
};

// const CONFIG = {
//     API_BASE_URL: 'http://localhost:8000',  // Change for production
//     CURRENT_PATIENT_ID: 'P405',
//     VITALS_REFRESH_INTERVAL: 30000,  // 30 seconds
//     LOG_MAX_ENTRIES: 10
// };

// ============================================
// STATE MANAGEMENT
// ============================================

const AppState = {
    currentVitals: {
        temp: 0,
        hr: 0,
        bp: "0/0",
        time: ""
    },
    auditLog: [],
    criticalAlertActive: false,
    monitoringInterval: null,
    currentPatient: null  // Will store current patient data
};

// const AppState = {
//     currentVitals: {
//         temp: 0,
//         hr: 0,
//         bp: "0/0",
//         time: ""
//     },
//     auditLog: [],
//     criticalAlertActive: false,
//     monitoringInterval: null
// };

// ============================================
// UTILITY FUNCTIONS
// ============================================

/**
 * Determines the color code for a vital sign based on its value
 * @param {string} key - The vital sign key (hr, bp, temp)
 * @param {number|string} value - The vital sign value
 * @returns {string} - Color code (RED, ORANGE, GREEN)
 */
function getVitalColor(key, value) {
    switch (key) {
        case 'hr':
            if (value > 110 || value < 50) return 'RED';
            if (value > 100 || value < 60) return 'ORANGE';
            return 'GREEN';
            
        case 'bp':
            const systolic = parseInt(value.split('/')[0]);
            if (systolic < 90 || systolic > 180) return 'RED';
            if (systolic < 100 || systolic > 140) return 'ORANGE';
            return 'GREEN';
            
        case 'temp':
            if (value > 103 || value < 95) return 'RED';
            if (value > 101 || value < 97) return 'ORANGE';
            return 'GREEN';
            
        default:
            return 'GREEN';
    }
}

/**
 * Checks if patient is in critical condition
 * @param {Object} vitals - Patient vitals object
 * @returns {boolean} - True if critical
 */
function isCriticalCondition(vitals) {
    const hrCritical = vitals.hr > 110 || vitals.hr < 50;
    const bpCritical = vitals.bp.startsWith('90') || vitals.bp.startsWith('80') || vitals.bp.startsWith('70');
    const tempCritical = vitals.temp > 103 || vitals.temp < 95;
    
    return hrCritical || bpCritical || tempCritical;
}

/**
 * Formats current time for display
 * @returns {string} - Formatted time string
 */
function getCurrentTimeString() {
    const now = new Date();
    return now.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false
    });
}

/**
 * Gets element by ID with error handling
 * @param {string} id - Element ID
 * @returns {HTMLElement|null}
 */
function getElement(id) {
    const element = document.getElementById(id);
    if (!element) {
        console.error(`Element with ID '${id}' not found`);
    }
    return element;
}

// ============================================
// UI UPDATE FUNCTIONS
// ============================================

/**
 * Updates the vitals display on the UI
 * @param {Object} vitals - Vitals object with temp, hr, bp, time
 */
function updateVitalsUI(vitals) {
    // Update vital values
    const hrValue = getElement('hr-value');
    const bpValue = getElement('bp-value');
    const tempValue = getElement('temp-value');
    const vitalsTime = getElement('vitals-time');
    
    if (hrValue) hrValue.textContent = vitals.hr;
    if (bpValue) bpValue.textContent = vitals.bp;
    if (tempValue) tempValue.textContent = vitals.temp;
    if (vitalsTime) vitalsTime.textContent = `Last Update: ${vitals.time}`;
    
    // Update tile colors
    const hrTile = getElement('hr-tile');
    const bpTile = getElement('bp-tile');
    const tempTile = getElement('temp-tile');
    
    if (hrTile) {
        hrTile.className = `vital-tile ${getVitalColor('hr', vitals.hr)}`;
    }
    if (bpTile) {
        bpTile.className = `vital-tile ${getVitalColor('bp', vitals.bp)}`;
    }
    if (tempTile) {
        tempTile.className = `vital-tile ${getVitalColor('temp', vitals.temp)}`;
    }
    
    // Update risk indicator
    const critical = isCriticalCondition(vitals);
    updateRiskIndicator(critical);
}

/**
 * Updates the risk indicator and header alert status
 * @param {boolean} isCritical - Whether patient is in critical condition
 */
function updateRiskIndicator(isCritical) {
    const riskStatus = getElement('risk-status');
    const header = getElement('main-header');
    
    if (!riskStatus || !header) return;
    
    if (isCritical) {
        riskStatus.className = 'risk-indicator RED critical-alert';
        riskStatus.textContent = '🚨 CRITICAL RISK';
        header.classList.add('critical-alert');
        AppState.criticalAlertActive = true;
    } else {
        riskStatus.className = 'risk-indicator GREEN';
        riskStatus.textContent = '✓ STABLE';
        header.classList.remove('critical-alert');
        AppState.criticalAlertActive = false;
    }
}

/**
 * Adds an entry to the audit log
 * @param {string} message - Log message to add
 */
function addToLog(message) {
    const timeStr = getCurrentTimeString();
    const logMessage = `${timeStr}: ${message}`;
    
    // Add to state
    AppState.auditLog.unshift(logMessage);
    
    // Update UI
    const logContainer = getElement('log-container');
    if (!logContainer) return;
    
    const newLog = document.createElement('p');
    newLog.textContent = logMessage;
    newLog.style.animation = 'fadeIn 0.3s ease-in';
    logContainer.prepend(newLog);
    
    // Keep only last N logs
    if (logContainer.children.length > CONFIG.LOG_MAX_ENTRIES) {
        logContainer.removeChild(logContainer.lastChild);
    }
}

/**
 * Updates the AI monologue/reasoning section
 * @param {string} reasoning - Reasoning text
 * @param {string} recommendation - Recommendation text
 * @param {string|null} action - Action taken (optional)
 */
function updateAIMonologue(reasoning, recommendation, action = null) {
    const reasoningText = getElement('reasoning-text');
    const recommendationText = getElement('recommendation-text');
    const actionStatus = getElement('ai-action-status');
    const actionDetail = getElement('ai-action-detail');
    
    if (reasoningText) {
        reasoningText.innerHTML = `<strong>[STEP 2: REASONING]</strong> ${reasoning}`;
    }
    
    if (recommendationText) {
        recommendationText.innerHTML = `<strong>Recommendation:</strong> ${recommendation}`;
    }
    
    if (action && actionStatus && actionDetail) {
        actionStatus.style.display = 'block';
        actionDetail.textContent = action;
    } else if (actionStatus) {
        actionStatus.style.display = 'none';
    }
}

// ============================================
// API COMMUNICATION
// ============================================

/**
 * Fetches patient vitals from the backend
 * Currently using mock data - will connect to real API
 */
async function fetchPatientData() {
    try {
        addToLog('Fetching patient vitals from EHR system...');
        
        // TODO: Replace with actual API call when backend is ready
        // const response = await fetch(`${CONFIG.API_BASE_URL}/api/patient/${CONFIG.CURRENT_PATIENT_ID}/vitals`);
        // const data = await response.json();
        
        // MOCK DATA - Simulating API response
        // await simulateAPIDelay(1000);
        
        // const mockVitals = {
        //     temp: 100,
        //     hr: 90,
        //     bp: "100/160",
        //     time: getCurrentTimeString()
        // };
        
        // Update state and UI
        AppState.currentVitals = mockVitals;
        updateVitalsUI(mockVitals);
        
        // Trigger AI analysis
        analyzePatientCondition(mockVitals);
        
    } catch (error) {
        console.error('Error fetching patient data:', error);
        addToLog('❌ ERROR: Failed to fetch patient data');
        
        // Show error to user
        updateAIMonologue(
            'System error: Unable to retrieve patient vitals.',
            'Please check system connection and try manual assessment.',
            null
        );
    }
}

/**
 * Analyzes patient condition and triggers appropriate protocols
 * @param {Object} vitals - Patient vitals
 */
function analyzePatientCondition(vitals) {
    const critical = isCriticalCondition(vitals);
    
    if (critical) {
        // Critical condition detected
        updateAIMonologue(
            `Vitals show high HR (${vitals.hr} bpm), low BP (${vitals.bp}), and fever (${vitals.temp}°F). Situation strongly matches Protocol A (Cardiogenic Shock Risk).`,
            'Immediate physical assessment required. Prepare for fluid resuscitation as per P-SHOCK-A protocol.',
            'Physician (Dr. Khan) alerted via Paging System'
        );
        
        addToLog('⚠️ CRITICAL: Protocol P-SHOCK-A triggered');
        addToLog('AI alerted physician automatically');
        
        // TODO: Send actual alert to backend
        // sendPhysicianAlert(CONFIG.CURRENT_PATIENT_ID, 'P-SHOCK-A');
        
    } else {
        // Normal condition
        updateAIMonologue(
            'Vitals within acceptable ranges. No critical protocols triggered.',
            'Continue routine monitoring. Document current status.',
            null
        );
        
        addToLog('✓ Routine check completed - Patient stable');
    }
}

/**
 * Simulates API delay for mock data
 * @param {number} ms - Delay in milliseconds
 */
function simulateAPIDelay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// ============================================
// USER ACTION HANDLERS
// ============================================

/**
 * Handles confirmation button click
 */
function handleConfirmation() {
    const confirmation = confirm(
        'Are you sure you want to CONFIRM and proceed with AI recommendations?\n\n' +
        'This will log the action in the EHR system.'
    );
    
    if (confirmation) {
        addToLog('✅ Human Nurse CONFIRMED AI protocol execution');
        alert('✅ Action Confirmed!\n\nPhysician alert and documentation logged successfully.');
        
        // TODO: Send confirmation to backend
        // sendActionConfirmation(CONFIG.CURRENT_PATIENT_ID, 'CONFIRMED');
    }
}

/**
 * Handles escalation button click
 */
function handleEscalation() {
    const reason = prompt(
        'Please provide escalation reason (required):\n\n' +
        'This will alert the Senior Nurse immediately.'
    );
    
    if (reason && reason.trim().length >= 5) {
        addToLog(`⚠️ ESCALATION: Senior Nurse alerted. Reason: ${reason}`);
        alert(
            `⚠️ Escalation Sent!\n\n` +
            `Senior Nurse has been alerted with reason:\n"${reason}"`
        );
        
        // TODO: Send escalation to backend
        // sendEscalation(CONFIG.CURRENT_PATIENT_ID, reason);
        
    } else if (reason !== null) {
        alert('Escalation cancelled.\n\nPlease provide a valid reason (minimum 5 characters).');
    }
}

/**
 * Handles document note button click
 */
function documentNote() {
    const noteText = getElement('nurse-note')?.value.trim();
    
    if (!noteText) {
        alert('Please write a note before documenting.');
        return;
    }
    
    if (noteText.length < 10) {
        alert('Please write a meaningful note (minimum 10 characters).');
        return;
    }
    
    const preview = noteText.substring(0, 50) + (noteText.length > 50 ? '...' : '');
    addToLog(`📝 Note Documented: "${preview}"`);
    alert(`✅ Note successfully documented:\n\n"${preview}"`);
    
    // Clear textarea
    const textarea = getElement('nurse-note');
    if (textarea) textarea.value = '';
    
    // TODO: Send note to backend
    // sendNurseNote(CONFIG.CURRENT_PATIENT_ID, noteText);
}

// ============================================
// MONITORING & INITIALIZATION
// ============================================

/**
 * Starts automatic vitals monitoring with periodic refresh
 */
function startVitalsMonitoring() {
    // Initial fetch
    fetchPatientData();
    
    // Set up periodic refresh
    AppState.monitoringInterval = setInterval(
        fetchPatientData,
        CONFIG.VITALS_REFRESH_INTERVAL
    );
    
    addToLog(`🔄 Auto-refresh enabled (every ${CONFIG.VITALS_REFRESH_INTERVAL / 1000}s)`);
}

/**
 * Stops automatic vitals monitoring
 */
function stopVitalsMonitoring() {
    if (AppState.monitoringInterval) {
        clearInterval(AppState.monitoringInterval);
        AppState.monitoringInterval = null;
        addToLog('⏸️ Auto-refresh paused');
    }
}

/**
 * Sets up event listeners for user interactions
 */
function setupEventListeners() {
    // Confirmation button
    const btnConfirm = getElement('btn-confirm');
    if (btnConfirm) {
        btnConfirm.addEventListener('click', handleConfirmation);
    }
    
    // Override/Escalation button
    const btnOverride = getElement('btn-override');
    if (btnOverride) {
        btnOverride.addEventListener('click', handleEscalation);
    }
    
    // Document note button
    const btnDocument = getElement('btn-document');
    if (btnDocument) {
        btnDocument.addEventListener('click', documentNote);
    }

    // ============================================
    // ADMIN PANEL EVENT LISTENERS
    // ============================================

    // Admin button - Open modal
    const adminBtn = getElement('admin-btn');
    if (adminBtn) {
        adminBtn.addEventListener('click', openAdminModal);
    }

    // Close modal button
    const adminClose = document.querySelector('.admin-close');
    if (adminClose) {
        adminClose.addEventListener('click', closeAdminModal);
    }

    // Close modal when clicking outside
    const adminModal = getElement('admin-modal');
    if (adminModal) {
        adminModal.addEventListener('click', (e) => {
            if (e.target === adminModal) {
                closeAdminModal();
            }
        });
    }

    // Admin login button
    const adminLoginBtn = getElement('admin-login-btn');
    if (adminLoginBtn) {
        adminLoginBtn.addEventListener('click', handleAdminLogin);
    }

    // Admin password input - Enter key
    const adminPasswordInput = getElement('admin-password');
    if (adminPasswordInput) {
        adminPasswordInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                handleAdminLogin();
            }
        });
    }

    // Patient registration form submit
    const patientForm = getElement('patient-registration-form');
    if (patientForm) {
        patientForm.addEventListener('submit', handlePatientRegistration);
    }

    // Cancel button
    const adminCancelBtn = getElement('admin-cancel-btn');
    if (adminCancelBtn) {
        adminCancelBtn.addEventListener('click', closeAdminModal);
    }
    
    // Keyboard shortcuts
    document.addEventListener('keydown', (event) => {
        // Ctrl/Cmd + Enter in textarea = Document note
        if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
            const activeElement = document.activeElement;
            if (activeElement && activeElement.id === 'nurse-note') {
                documentNote();
            }
        }

        // ESC key to close admin modal
        if (event.key === 'Escape') {
            const modal = getElement('admin-modal');
            if (modal && modal.style.display === 'flex') {
                closeAdminModal();
            }
        }
    });
}

// function setupEventListeners() {
//     // Confirmation button
//     const btnConfirm = getElement('btn-confirm');
//     if (btnConfirm) {
//         btnConfirm.addEventListener('click', handleConfirmation);
//     }
    
//     // Override/Escalation button
//     const btnOverride = getElement('btn-override');
//     if (btnOverride) {
//         btnOverride.addEventListener('click', handleEscalation);
//     }
    
//     // Document note button
//     const btnDocument = getElement('btn-document');
//     if (btnDocument) {
//         btnDocument.addEventListener('click', documentNote);
//     }
    
//     // Keyboard shortcuts
//     document.addEventListener('keydown', (event) => {
//         // Ctrl/Cmd + Enter in textarea = Document note
//         if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
//             const activeElement = document.activeElement;
//             if (activeElement && activeElement.id === 'nurse-note') {
//                 documentNote();
//             }
//         }
//     });
// }

/**

// ============================================
// ADMIN PANEL FUNCTIONS
// ============================================

/**
 * Opens the admin modal
 */
function openAdminModal() {
    const modal = getElement('admin-modal');
    if (modal) {
        modal.style.display = 'flex';
        // Reset to password screen
        const passwordScreen = getElement('admin-password-screen');
        const formScreen = getElement('admin-panel-form');
        if (passwordScreen) passwordScreen.style.display = 'block';
        if (formScreen) formScreen.style.display = 'none';
        
        // Clear password input
        const passwordInput = getElement('admin-password');
        if (passwordInput) {
            passwordInput.value = '';
            passwordInput.focus();
        }
    }
}

/**
 * Closes the admin modal
 */
function closeAdminModal() {
    const modal = getElement('admin-modal');
    if (modal) {
        modal.style.display = 'none';
    }
    
    // Reset form
    const form = getElement('patient-registration-form');
    if (form) {
        form.reset();
    }
}

/**
 * Handles admin login
 */
function handleAdminLogin() {
    const passwordInput = getElement('admin-password');
    if (!passwordInput) return;
    
    const enteredPassword = passwordInput.value.trim();
    
    if (enteredPassword === CONFIG.ADMIN_PASSWORD) {
        // Correct password
        addToLog('✅ Admin panel accessed');
        
        // Show form, hide password screen
        const passwordScreen = getElement('admin-password-screen');
        const formScreen = getElement('admin-panel-form');
        
        if (passwordScreen) passwordScreen.style.display = 'none';
        if (formScreen) formScreen.style.display = 'block';
        
    } else {
        // Wrong password
        alert('❌ Incorrect Password!\n\nPlease try again.');
        passwordInput.value = '';
        passwordInput.focus();
    }
}

/**
 * Handles patient registration form submission
 */
function handlePatientRegistration(event) {
    event.preventDefault();
    
    // Get form data
    const formData = new FormData(event.target);
    const patientData = {
        patient_id: formData.get('patient_id'),
        first_name: formData.get('first_name'),
        last_name: formData.get('last_name'),
        date_of_birth: formData.get('date_of_birth'),
        gender: formData.get('gender'),
        blood_group: formData.get('blood_group'),
        room_number: formData.get('room_number'),
        bed_number: formData.get('bed_number'),
        admission_date: formData.get('admission_date'),
        diagnosis: formData.get('diagnosis'),
        allergies: formData.get('allergies'),
        vitals: {
            hr: parseInt(formData.get('heart_rate')),
            bp: formData.get('blood_pressure'),
            temp: parseFloat(formData.get('temperature'))
        },
        emergency_contact: {
            name: formData.get('emergency_name'),
            relation: formData.get('emergency_relation'),
            phone: formData.get('emergency_phone')
        }
    };
    
    // Calculate age
    const birthDate = new Date(patientData.date_of_birth);
    const today = new Date();
    const age = today.getFullYear() - birthDate.getFullYear();
    
    // Store in AppState (in production, this will be sent to backend)
    AppState.currentPatient = patientData;

    // Update UI with new patient data
    updatePatientInfoUI(patientData, age);
    
    // Update vitals display with form data
    const vitalsData = {
        hr: patientData.vitals.hr,
        bp: patientData.vitals.bp,
        temp: patientData.vitals.temp,
        time: getCurrentTimeString()
    };
    AppState.currentVitals = vitalsData;
    updateVitalsUI(vitalsData);
    analyzePatientCondition(vitalsData);
    
    // Log action
    addToLog(`📋 New patient registered: ${patientData.patient_id} - ${patientData.first_name} ${patientData.last_name}`);
    addToLog(`💓 Initial vitals recorded: HR ${vitalsData.hr}, BP ${vitalsData.bp}, Temp ${vitalsData.temp}°F`);
    
    // Show success message
    alert(
        `✅ Patient Registered Successfully!\n\n` +
        `Patient ID: ${patientData.patient_id}\n` +
        `Name: ${patientData.first_name} ${patientData.last_name}\n` +
        `Room: ${patientData.room_number}\n` +
        `Vitals: HR ${vitalsData.hr}, BP ${vitalsData.bp}, Temp ${vitalsData.temp}°F\n\n` +
        `The dashboard has been updated with the new patient information.`
    );
    
    // Close modal
    closeAdminModal();
    
    // Update UI with new patient data
    // updatePatientInfoUI(patientData, age);
    
    // // Log action
    // addToLog(`📋 New patient registered: ${patientData.patient_id} - ${patientData.first_name} ${patientData.last_name}`);
    
    // // Show success message
    // alert(
    //     `✅ Patient Registered Successfully!\n\n` +
    //     `Patient ID: ${patientData.patient_id}\n` +
    //     `Name: ${patientData.first_name} ${patientData.last_name}\n` +
    //     `Room: ${patientData.room_number}\n\n` +
    //     `The dashboard has been updated with the new patient information.`
    // );
    
    // // Close modal
    // closeAdminModal();
    
    // TODO: Send to backend API when ready
    // sendPatientToBackend(patientData);
}

/**
 * Updates the patient information on the UI
 */
function updatePatientInfoUI(patientData, age) {
    // Update patient ID
    const patientIdElement = getElement('patient-id');
    if (patientIdElement) {
        patientIdElement.textContent = patientData.patient_id;
    }
    
    // Update header title
    const headerTitle = getElement('header-title');
    if (headerTitle) {
        headerTitle.textContent = `Agentic Triage Dashboard: ${patientData.patient_id}`;
    }
    
    // Update patient info section
    const patientInfoCard = document.querySelector('.patient-info');
    if (patientInfoCard) {
        patientInfoCard.innerHTML = `
            <p><strong>Patient ID:</strong> <span id="patient-id">${patientData.patient_id}</span> (${patientData.gender}, ${age} yrs)</p>
            <p><strong>Room/Bed:</strong> ${patientData.room_number}${patientData.bed_number ? ' / ' + patientData.bed_number : ''}</p>
            <p><strong>Diagnosis:</strong> ${patientData.diagnosis}</p>
            ${patientData.allergies ? `
                <div class="alert-box-danger">
                    <strong>⚠️ ALLERGIES:</strong> ${patientData.allergies.toUpperCase()} (MUST READ!)
                </div>
            ` : ''}
        `;
    }
    
    // Update CONFIG with new patient ID
    CONFIG.CURRENT_PATIENT_ID = patientData.patient_id;
}

// Initializes the application
function initializeApp() {
    console.log('🏥 Nurse Triage Dashboard - Initializing...');
    
    // Setup event listeners
    setupEventListeners();
    
    // Add initial log entries
    addToLog('🏥 System initialized successfully');
    addToLog(`Connected to patient ${CONFIG.CURRENT_PATIENT_ID}`);
    
    // Start monitoring
    startVitalsMonitoring();
    
    console.log('✅ Application ready');
}

// ============================================
// APPLICATION ENTRY POINT
// ============================================

// Initialize when DOM is fully loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeApp);
} else {
    // DOM already loaded
    initializeApp();
}

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    stopVitalsMonitoring();
});