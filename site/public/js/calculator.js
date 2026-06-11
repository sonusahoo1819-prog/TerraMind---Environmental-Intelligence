// TerraMind Interactive Footprint Calculator Engine
(function() {
    // DOM Elements
    const mileageInput = document.querySelector('input[type="range"]');
    const solarInput = document.querySelector('input[type="number"]');
    const floatingScore = document.getElementById('floating-score');
    
    // Sidebar Display Elements
    const sidebarScoreVal = document.querySelector('aside .font-display-lg');
    const sidebarGauge = document.querySelector('.progress-gauge');
    const nationalAvgPct = document.querySelector('aside .font-label-md.text-primary');
    const avgProgressBar = document.querySelector('aside .bg-primary.w-\\[40\\%\\]');
    
    // Category Buttons
    const transitBtn = document.querySelectorAll('button')[3]; // Public Transit (indexing based on order in DOM)
    const evBtn = document.querySelectorAll('button')[4];      // EV Charging
    const veganBtn = document.querySelectorAll('button')[7];
    const vegBtn = document.querySelectorAll('button')[8];
    const flexBtn = document.querySelectorAll('button')[9];
    const meatBtn = document.querySelectorAll('button')[10];
    const compostBtn = document.querySelectorAll('button')[11]; // Composting Active button
    
    // State variables
    let weeklyMileage = 100;
    let solarPercent = 45;
    let isPublicTransit = false;
    let isEV = false;
    let dietChoice = 'flexitarian'; // vegan, vegetarian, flexitarian, meat
    let isComposting = false;
    
    // Initial UI Setup
    if (mileageInput) {
        mileageInput.min = "0";
        mileageInput.max = "300";
        mileageInput.value = "100";
    }
    
    // Helper to calculate total Co2 in tons/year
    function calculateTotalCO2() {
        // 1. Transportation: (mileage * 52 weeks) * Co2 per mile
        // Standard gas car is ~0.404 kg Co2 per mile.
        let transitFactor = 0.404;
        if (isEV) transitFactor = 0.08; // EV footprint is very small (grid emission)
        else if (isPublicTransit) transitFactor = 0.14; // Public transit avg per passenger mile
        
        let transportCO2 = (weeklyMileage * 52 * transitFactor) / 1000; // in tons
        
        // 2. Electricity: $120/mo avg. 1 USD is approx 0.8 kg Co2 in typical grid
        let baseElectricity = (120 * 12 * 0.8) / 1000; // base tons
        let electricityCO2 = baseElectricity * (1 - solarPercent / 100);
        
        // 3. Diet:
        let dietCO2 = 1.8; // Flexitarian
        if (dietChoice === 'vegan') dietCO2 = 0.8;
        else if (dietChoice === 'vegetarian') dietCO2 = 1.2;
        else if (dietChoice === 'meat') dietCO2 = 3.2;
        
        // 4. Waste & Recycling (standard base 0.6t offset by composting)
        let wasteCO2 = 0.6;
        if (isComposting) wasteCO2 -= 0.2;
        
        // 5. Flights (fixed based on 24.5 hours * 0.15t per hour)
        let flightCO2 = 24.5 * 0.15;
        
        const total = transportCO2 + electricityCO2 + dietCO2 + wasteCO2 + flightCO2;
        return parseFloat(total.toFixed(1));
    }
    
    // Update Gauge and Score Displays
    function updateUI() {
        const totalCO2 = calculateTotalCO2();
        
        // Update floating score
        if (floatingScore) {
            floatingScore.innerHTML = `${totalCO2} <span class="text-label-md font-normal">tCO2e</span>`;
        }
        
        // Update sidebar score
        if (sidebarScoreVal) {
            sidebarScoreVal.textContent = totalCO2;
        }
        
        // Update gauge stroke-dashoffset (Full gauge is 282.7)
        // Score maps 0 to 12 tons (lower score = greener gauge)
        if (sidebarGauge) {
            const maxCO2 = 12.0;
            const percentage = Math.min((totalCO2 / maxCO2) * 100, 100);
            const dashoffset = 282.7 - (282.7 * (100 - percentage) / 100);
            sidebarGauge.style.strokeDashoffset = dashoffset;
            
            // Dynamic color change based on footprint scale
            if (totalCO2 < 4.5) {
                sidebarGauge.style.stroke = "#00C26E"; // Emerald
            } else if (totalCO2 < 7.5) {
                sidebarGauge.style.stroke = "#FFD54A"; // Solar Yellow
            } else {
                sidebarGauge.style.stroke = "#ffb4ab"; // Warning Red
            }
        }
        
        // Update national average comparison
        // US average is ~16.0 tons/year. UK is ~6.0. Global is ~4.5.
        // Let's use 5.0 tons as our benchmark target
        const benchmark = 5.0;
        const diffPercent = Math.round(((totalCO2 - benchmark) / benchmark) * 100);
        if (nationalAvgPct) {
            if (diffPercent < 0) {
                nationalAvgPct.textContent = `${diffPercent}%`;
                nationalAvgPct.className = "font-label-md text-primary"; // green
            } else {
                nationalAvgPct.textContent = `+${diffPercent}%`;
                nationalAvgPct.className = "font-label-md text-error"; // red
            }
        }
        
        if (avgProgressBar) {
            const fillRatio = Math.min(Math.max((totalCO2 / 12) * 100, 10), 100);
            avgProgressBar.style.width = `${fillRatio}%`;
            if (totalCO2 < 5.0) {
                avgProgressBar.style.backgroundColor = "#00C26E";
            } else {
                avgProgressBar.style.backgroundColor = "#ffb4ab";
            }
        }
    }
    
    // Add Event Listeners
    if (mileageInput) {
        mileageInput.addEventListener('input', (e) => {
            weeklyMileage = parseFloat(e.target.value);
            updateUI();
        });
    }
    
    if (solarInput) {
        solarInput.addEventListener('input', (e) => {
            let val = parseInt(e.target.value) || 0;
            if (val > 100) val = 100;
            if (val < 0) val = 0;
            solarPercent = val;
            updateUI();
        });
    }
    
    // Button Toggle Helpers
    function toggleButton(btn, isActive, colorClass = "border-primary") {
        if (isActive) {
            btn.classList.add(colorClass, "bg-white/10");
            btn.classList.remove("bg-surface-variant/50");
        } else {
            btn.classList.remove(colorClass, "bg-white/10");
            btn.classList.add("bg-surface-variant/50");
        }
    }
    
    if (transitBtn) {
        transitBtn.addEventListener('click', () => {
            isPublicTransit = !isPublicTransit;
            if (isPublicTransit) isEV = false; // mutually exclusive
            toggleButton(transitBtn, isPublicTransit, "border-primary");
            if (evBtn) toggleButton(evBtn, isEV, "border-primary");
            updateUI();
        });
    }
    
    if (evBtn) {
        evBtn.addEventListener('click', () => {
            isEV = !isEV;
            if (isEV) isPublicTransit = false; // mutually exclusive
            toggleButton(evBtn, isEV, "border-primary");
            if (transitBtn) toggleButton(transitBtn, isPublicTransit, "border-primary");
            updateUI();
        });
    }
    
    // Diet choices handling
    function setDiet(choice) {
        dietChoice = choice;
        const diets = [
            { btn: veganBtn, val: 'vegan', activeClass: 'border-tertiary text-tertiary bg-tertiary/20' },
            { btn: vegBtn, val: 'vegetarian', activeClass: 'border-tertiary text-tertiary bg-tertiary/20' },
            { btn: flexBtn, val: 'flexitarian', activeClass: 'border-tertiary text-tertiary bg-tertiary/20' },
            { btn: meatBtn, val: 'meat', activeClass: 'border-tertiary text-tertiary bg-tertiary/20' }
        ];
        
        diets.forEach(item => {
            if (!item.btn) return;
            if (item.val === choice) {
                // Set active styling classes
                item.btn.className = `p-3 rounded-lg border transition-all flex flex-col items-center ${item.activeClass}`;
            } else {
                // Set inactive styling classes
                item.btn.className = "bg-surface-variant/30 hover:border-tertiary p-3 rounded-lg border border-transparent transition-all flex flex-col items-center";
            }
        });
        updateUI();
    }
    
    if (veganBtn) veganBtn.addEventListener('click', () => setDiet('vegan'));
    if (vegBtn) vegBtn.addEventListener('click', () => setDiet('vegetarian'));
    if (flexBtn) flexBtn.addEventListener('click', () => setDiet('flexitarian'));
    if (meatBtn) meatBtn.addEventListener('click', () => setDiet('meat'));
    
    // Composting Toggle
    if (compostBtn) {
        compostBtn.addEventListener('click', () => {
            isComposting = !isComposting;
            if (isComposting) {
                compostBtn.className = "w-full py-2 bg-primary-container/20 rounded-lg font-label-md border border-primary-container text-primary-container transition-colors";
            } else {
                compostBtn.className = "w-full py-2 bg-surface-variant/30 rounded-lg font-label-md border border-outline-glass hover:bg-primary-container/10 transition-colors";
            }
            updateUI();
        });
    }
    
    // Run initial UI updates
    updateUI();

    // ==========================================
    // API INTEGRATION (Supabase Backend)
    // ==========================================

    // Fetch initial data from server on load
    fetch('/api/dashboard/summary')
        .then(res => res.json())
        .then(data => {
            if (data.latest_log) {
                const log = data.latest_log;
                // Set state from latest log
                solarPercent = log.renewable_energy || 45;
                isPublicTransit = log.public_transport > 50;
                isEV = log.commuting_mode === 'Electric';
                
                // Map diet back
                const dietMap = {'Vegan': 'vegan', 'Veggie': 'vegetarian', 'Flexi': 'flexitarian', 'Omnivore': 'meat'};
                dietChoice = dietMap[log.diet] || 'flexitarian';
                
                // Update inputs in UI
                if (mileageInput) {
                    weeklyMileage = log.commuting_mode === 'Electric' ? 50 : 120; // fallback estimations
                    mileageInput.value = weeklyMileage;
                }
                if (solarInput) solarInput.value = solarPercent;
                
                // Toggle buttons in UI
                if (transitBtn) toggleButton(transitBtn, isPublicTransit, "border-primary");
                if (evBtn) toggleButton(evBtn, isEV, "border-primary");
                setDiet(dietChoice);
                
                updateUI();
            }
        })
        .catch(err => console.warn("Could not fetch user summary on startup: using local defaults.", err));

    // Attach click listener to Save Footprint Data button
    const saveBtn = document.querySelector('aside button.bg-primary');
    if (saveBtn) {
        saveBtn.addEventListener('click', () => {
            saveBtn.textContent = 'Saving...';
            saveBtn.disabled = true;
            
            // Map state to payload
            const dietMap = {'vegan': 'Vegan', 'vegetarian': 'Veggie', 'flexitarian': 'Flexi', 'meat': 'Omnivore'};
            const payload = {
                public_transport: isPublicTransit ? 80 : 10,
                renewable_energy: solarPercent,
                diet: dietMap[dietChoice] || 'Flexi',
                commuting_mode: isEV ? 'Electric' : 'Gas Car'
            };
            
            fetch('/api/calculator/log', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            })
            .then(res => res.json())
            .then(data => {
                saveBtn.textContent = 'Save Footprint Data';
                saveBtn.disabled = false;
                if (data.success) {
                    alert('Footprint data successfully logged and carbon score updated!');
                }
            })
            .catch(err => {
                console.error("Save error:", err);
                alert("Failed to save footprint data. Running in offline/mock mode.");
                saveBtn.textContent = 'Save Footprint Data';
                saveBtn.disabled = false;
            });
        });
    }

    // Attach click listener to Coach recommendations button
    const coachBtn = document.querySelector('aside button.border-primary\\/30');
    if (coachBtn) {
        coachBtn.addEventListener('click', () => {
            window.location.href = 'aicoach.html';
        });
    }
})();
