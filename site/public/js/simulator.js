// TerraMind Carbon Impact Simulator Engine
(function() {
    // DOM Elements
    const transportSlider = document.querySelectorAll('input[type="range"]')[0];
    const energySlider = document.querySelectorAll('input[type="range"]')[1];
    const evCheckbox = document.querySelector('input[type="checkbox"]');
    
    const co2Readout = document.getElementById('co2-readout');
    const treesReadout = document.querySelector('.border-primary .text-4xl');
    const moneyReadout = document.querySelector('.border-emerald-400 .text-4xl');
    
    // Efficiency Circle Elements
    const effPath = document.querySelector('svg path.text-primary');
    const effText = document.querySelector('.relative.w-32.h-32 .absolute');
    
    // Sliders Label Values
    const transportValLabel = document.getElementById('transport-val');
    const energyValLabel = document.getElementById('energy-val');

    // State
    let transportPct = 45;
    let energyPct = 30;
    let dietChoice = 2; // 0: Omnivore, 1: Flexi, 2: Veggie, 3: Vegan
    let isEV = true;

    // Helper: Calculate simulated savings in tons/year
    function calculateSavings() {
        // Transport savings: up to 1.6 tons
        let transportSavings = (transportPct / 100) * 1.6;
        
        // Renewable energy savings: up to 2.0 tons
        let energySavings = (energyPct / 100) * 2.0;
        
        // Diet savings: Omnivore (0t), Flexi (0.6t), Veggie (1.2t), Vegan (1.8t)
        let dietSavings = 0;
        if (dietChoice === 1) dietSavings = 0.6;
        else if (dietChoice === 2) dietSavings = 1.2;
        else if (dietChoice === 3) dietSavings = 1.8;
        
        // EV commuting savings: EV saves ~2.2 tons compared to gas car
        let commuteSavings = isEV ? 2.2 : 0;
        
        const total = transportSavings + energySavings + dietSavings + commuteSavings;
        return parseFloat(total.toFixed(1));
    }

    // Update UI Elements
    function updateUI() {
        const savings = calculateSavings();
        
        // Update CO2 text
        if (co2Readout) {
            co2Readout.textContent = savings;
        }
        
        // Update Trees Saved (1 ton Co2 = ~45 trees/year absorption)
        if (treesReadout) {
            const trees = Math.round(savings * 45);
            treesReadout.textContent = `${trees} Trees`;
        }
        
        // Update Money Saved (1 ton Co2 saved = ~$200 in fuel/power bills)
        if (moneyReadout) {
            const money = (savings * 200).toFixed(2);
            moneyReadout.textContent = `$${money}`;
        }
        
        // Update Efficiency Gauge (Max possible savings is ~7.6t)
        if (effPath && effText) {
            const maxSavings = 7.6;
            const effPercent = Math.min(Math.round((savings / maxSavings) * 100), 100);
            
            effPath.setAttribute('stroke-dasharray', `${effPercent}, 100`);
            effText.textContent = `${effPercent}%`;
        }
    }

    // Overwrite global window updateDiet function to route here
    window.updateDiet = function(activeIndex) {
        dietChoice = activeIndex;
        
        const buttons = document.querySelectorAll('.diet-btn');
        buttons.forEach((btn, index) => {
            if (index === activeIndex) {
                btn.className = "diet-btn p-2 rounded-lg bg-primary text-on-primary text-xs font-bold shadow-lg shadow-primary/20";
            } else {
                btn.className = "diet-btn p-2 rounded-lg bg-surface-container-high border border-outline-variant text-xs hover:border-primary transition-all";
            }
        });
        
        updateUI();
    };

    // Sliders listeners
    if (transportSlider) {
        transportSlider.addEventListener('input', (e) => {
            transportPct = parseInt(e.target.value);
            if (transportValLabel) transportValLabel.textContent = `${transportPct}%`;
            updateUI();
        });
    }

    if (energySlider) {
        energySlider.addEventListener('input', (e) => {
            energyPct = parseInt(e.target.value);
            if (energyValLabel) energyValLabel.textContent = `${energyPct}%`;
            updateUI();
        });
    }

    // EV checkbox listener
    if (evCheckbox) {
        evCheckbox.addEventListener('change', (e) => {
            isEV = e.target.checked;
            updateUI();
        });
    }

    // Run initial calculations
    updateUI();
})();
