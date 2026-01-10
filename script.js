// Register ScrollTrigger plugin
gsap.registerPlugin(ScrollTrigger);

// Wait for DOM and images to load before initializing animations
window.addEventListener('load', () => {
    initializeAnimations();
});

function initializeAnimations() {
    const traemContainer = document.querySelector('.traem-container');
    const traemElement = document.getElementById('traem');

    // Timing configuration - easy to adjust
    let time = 0;
    const ITEM_DURATION = 1.5;
    const ITEM_GAP = 1.0;

    // Main animation timeline
    const mainTimeline = gsap.timeline({
        scrollTrigger: {
            trigger: ".scroll-section[data-step='0']",
            start: "top top",
            end: "bottom+=6000 bottom", // Extended for more items
            scrub: 1,
            invalidateOnRefresh: true,
        }
    });

    // Continuous rotation based on scroll
    gsap.to(traemContainer, {
        // rotation: 360 * 1.5, // Increased for longer scroll
        ease: "none",
        scrollTrigger: {
            trigger: ".scroll-section[data-step='0']",
            start: "top top",
            end: "bottom+=6000 bottom",
            scrub: 0.5,
            invalidateOnRefresh: true,
        }
    });

    // ========== PHASE 1: ITEMS IN ==========

    // 1. Traem entrance
    mainTimeline.to(traemElement, {
        opacity: 1,
        scale: 1,
        duration: 2,
        ease: "power2.out",
    }, time);
    time += 2 + ITEM_GAP;

    // 2. Rice
    mainTimeline.to("#rice", {
        opacity: 1,
        scale: 1,
        duration: ITEM_DURATION,
        ease: "back.out(1.2)",
    }, time);
    time += ITEM_DURATION + ITEM_GAP;

    // 3. Methi Maaz - 4 portions
    mainTimeline.to("#methi-maaz-top, #methi-maaz-right, #methi-maaz-bottom, #methi-maaz-left", {
        opacity: 0.9,
        scale: 1,
        duration: ITEM_DURATION,
        ease: "back.out(1.2)",
        stagger: 0.1,
    }, time);
    time += ITEM_DURATION + ITEM_GAP;

    // 4. Kebab - 2 pieces diagonal
    mainTimeline.to("#kebab-1, #kebab-2", {
        opacity: 1,
        scale: 2.7,
        rotation: 45,
        duration: ITEM_DURATION,
        ease: "back.out(1.2)",
        stagger: 0.2,
    }, time);
    time += ITEM_DURATION + ITEM_GAP;

    // 5. Chicken - 2 pieces
    mainTimeline.to("#chicken-1, #chicken-2", {
        opacity: 1,
        x: 0,
        y: 0,
        rotation: 0,
        duration: ITEM_DURATION,
        ease: "power2.out",
        stagger: 0.2,
    }, time);
    time += ITEM_DURATION + ITEM_GAP;

    // 6. Shank (Dani Phol) - 1 piece center
    mainTimeline.to("#shank", {
        opacity: 1,
        scale: 1,
        duration: ITEM_DURATION,
        ease: "back.out(1.2)",
    }, time);
    time += ITEM_DURATION + ITEM_GAP;

    // 7. Tabakh Maaz - 2 pieces
    mainTimeline.to("#tabakh-maaz-1, #tabakh-maaz-2", {
        opacity: 1,
        scale: 1,
        duration: ITEM_DURATION,
        ease: "power2.out",
        stagger: 0.2,
    }, time);
    time += ITEM_DURATION + ITEM_GAP;

    // 8. Covering Plate - 1 piece overlay
    mainTimeline.to("#covering-plate", {
        opacity: 0.95,
        scale: 1,
        duration: ITEM_DURATION,
        ease: "power2.out",
    }, time);
    time += ITEM_DURATION + ITEM_GAP * 2; // Extra pause with covering on

    // ========== PHASE 2: ITEMS OUT (reverse order) ==========

    const REMOVE_DURATION = 1.0;

    // Remove covering plate
    mainTimeline.to("#covering-plate", {
        opacity: 0,
        scale: 0.9,
        duration: REMOVE_DURATION,
        ease: "power2.in",
    }, time);
    time += REMOVE_DURATION + ITEM_GAP;

    // Remove tabakh maaz
    mainTimeline.to("#tabakh-maaz-1, #tabakh-maaz-2", {
        opacity: 0,
        scale: 0.5,
        duration: REMOVE_DURATION,
        ease: "power2.in",
    }, time);
    time += REMOVE_DURATION + ITEM_GAP;

    // Remove shank
    mainTimeline.to("#shank", {
        opacity: 0,
        scale: 0.5,
        duration: REMOVE_DURATION,
        ease: "power2.in",
    }, time);
    time += REMOVE_DURATION + ITEM_GAP;

    // Remove chicken
    mainTimeline.to("#chicken-1, #chicken-2", {
        opacity: 0,
        scale: 0.5,
        duration: REMOVE_DURATION,
        ease: "power2.in",
    }, time);
    time += REMOVE_DURATION + ITEM_GAP;

    // Remove kebabs
    mainTimeline.to("#kebab-1, #kebab-2", {
        opacity: 0,
        scale: 0.5,
        duration: REMOVE_DURATION,
        ease: "power2.in",
    }, time);
    time += REMOVE_DURATION + ITEM_GAP;

    // Remove methi maaz
    mainTimeline.to("#methi-maaz-top, #methi-maaz-right, #methi-maaz-bottom, #methi-maaz-left", {
        opacity: 0,
        scale: 0.5,
        duration: REMOVE_DURATION,
        ease: "power2.in",
    }, time);
    time += REMOVE_DURATION + ITEM_GAP * 2;

    // ========== PHASE 3: RISTA SEQUENCE ==========

    // Rista appears in center - 4 pieces
    mainTimeline.to("#rista-1, #rista-2, #rista-3, #rista-4", {
        opacity: 1,
        scale: 1,
        duration: ITEM_DURATION,
        ease: "back.out(1.2)",
        stagger: 0.1,
    }, time);
    time += ITEM_DURATION + ITEM_GAP;

    // Rista expands to edges (cardinal positions)
    mainTimeline.to("#rista-1", {
        x: "0%",
        y: "-150%",
        duration: 1.5,
        ease: "power2.inOut",
    }, time);
    mainTimeline.to("#rista-2", {
        x: "150%",
        y: "0%",
        duration: 1.5,
        ease: "power2.inOut",
    }, time);
    mainTimeline.to("#rista-3", {
        x: "0%",
        y: "150%",
        duration: 1.5,
        ease: "power2.inOut",
    }, time);
    mainTimeline.to("#rista-4", {
        x: "-150%",
        y: "0%",
        duration: 1.5,
        ease: "power2.inOut",
    }, time);
    time += 1.5 + ITEM_GAP;

    // Rista fades out
    mainTimeline.to("#rista-1, #rista-2, #rista-3, #rista-4", {
        opacity: 0,
        scale: 0.5,
        duration: REMOVE_DURATION,
        ease: "power2.in",
    }, time);

    // Step labels fade in/out
    document.querySelectorAll('.step-label').forEach((label) => {
        gsap.to(label, {
            opacity: 0.8,
            scrollTrigger: {
                trigger: label.closest('.scroll-section'),
                start: "top center",
                end: "bottom center",
                scrub: true,
                toggleActions: "play reverse play reverse"
            }
        });
    });

    // Refresh ScrollTrigger after everything is set up
    ScrollTrigger.refresh();

    console.log("✅ Animations initialized with new sequence!");
    console.log("📊 Timeline duration:", time.toFixed(1), "seconds");
}

// Performance optimization: Use will-change sparingly
const animatedElements = document.querySelectorAll('.traem, .food-item');
const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.willChange = 'transform, opacity';
        } else {
            entry.target.style.willChange = 'auto';
        }
    });
});

animatedElements.forEach(el => observer.observe(el));

// Debug: Log scroll progress (comment out in production)
/*
ScrollTrigger.create({
    trigger: ".scroll-section[data-step='0']",
    start: "top top",
    end: "bottom+=4000 bottom",
    onUpdate: (self) => {
        console.log("Scroll Progress:", (self.progress * 100).toFixed(2) + "%");
    }
});
*/
