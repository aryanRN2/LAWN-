document.addEventListener('DOMContentLoaded', () => {
    // Navbar Scroll Effect
    const navbar = document.getElementById('mainNav');
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });

    // Color Picker logic
    const colorPicks = document.querySelectorAll('.color-pick');
    let selectedScore = 3;

    colorPicks.forEach(pick => {
        pick.addEventListener('click', () => {
            colorPicks.forEach(p => p.classList.remove('active'));
            pick.classList.add('active');
            selectedScore = parseInt(pick.getAttribute('data-score'));
        });
    });

    // Score Calculation
    const calculateBtn = document.getElementById('calculateScore');
    const resultArea = document.getElementById('resultArea');
    const scoreDisplay = document.getElementById('scoreDisplay');
    const recommendationText = document.getElementById('recommendationText');

    calculateBtn.addEventListener('click', () => {
        const waterFreq = parseInt(document.getElementById('waterFreq').value);
        const totalScore = waterFreq + selectedScore;
        
        resultArea.classList.remove('d-none');
        
        let recommendation = "";
        let scoreLabel = "";

        if (totalScore <= 2) {
            scoreLabel = "Critical Condition";
            recommendation = "Your lawn needs immediate attention. We recommend a soil test and deep hydration treatment.";
        } else if (totalScore <= 4) {
            scoreLabel = "Fair Condition";
            recommendation = "Your lawn is surviving but not thriving. Weekly mowing and organic fertilization could transform it.";
        } else {
            scoreLabel = "Great Potential";
            recommendation = "You have a solid base! A precision edging service and seasonal overseeding will make it the talk of the town.";
        }

        scoreDisplay.textContent = scoreLabel;
        recommendationText.textContent = recommendation;

        // Smooth scroll to result
        resultArea.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    });

    // Smooth Scrolling for links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });

    // Simple Animation on Scroll
    const observerOptions = {
        threshold: 0.1
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = "1";
                entry.target.style.transform = "translateY(0)";
            }
        });
    }, observerOptions);

    document.querySelectorAll('.service-card, .experience-badge').forEach(el => {
        el.style.opacity = "0";
        el.style.transform = "translateY(30px)";
        el.style.transition = "all 0.6s ease-out";
        observer.observe(el);
    });
});
