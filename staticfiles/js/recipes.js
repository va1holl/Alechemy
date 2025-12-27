/**
 * Recipes Module - JavaScript
 * Handles carousels, interactions, and animations
 */

document.addEventListener('DOMContentLoaded', function() {
    initCarousels();
    initShareButton();
    initAddToEventButton();
    initReviewsModal();
});

/**
 * Initialize drag-to-scroll for carousels
 */
function initCarousels() {
    const carousels = document.querySelectorAll('.recipes-carousel');
    
    carousels.forEach(carousel => {
        let isDown = false;
        let startX;
        let scrollLeft;

        carousel.addEventListener('mousedown', (e) => {
            isDown = true;
            carousel.classList.add('dragging');
            startX = e.pageX - carousel.offsetLeft;
            scrollLeft = carousel.scrollLeft;
            carousel.style.cursor = 'grabbing';
        });

        carousel.addEventListener('mouseleave', () => {
            isDown = false;
            carousel.classList.remove('dragging');
            carousel.style.cursor = 'grab';
        });

        carousel.addEventListener('mouseup', () => {
            isDown = false;
            carousel.classList.remove('dragging');
            carousel.style.cursor = 'grab';
        });

        carousel.addEventListener('mousemove', (e) => {
            if (!isDown) return;
            e.preventDefault();
            const x = e.pageX - carousel.offsetLeft;
            const walk = (x - startX) * 2;
            carousel.scrollLeft = scrollLeft - walk;
        });

        // Touch support
        carousel.addEventListener('touchstart', (e) => {
            startX = e.touches[0].pageX - carousel.offsetLeft;
            scrollLeft = carousel.scrollLeft;
        });

        carousel.addEventListener('touchmove', (e) => {
            const x = e.touches[0].pageX - carousel.offsetLeft;
            const walk = (x - startX) * 2;
            carousel.scrollLeft = scrollLeft - walk;
        });
    });
}

/**
 * Initialize share button functionality
 */
function initShareButton() {
    const shareBtn = document.getElementById('shareBtn');
    
    if (shareBtn) {
        shareBtn.addEventListener('click', async function() {
            const title = document.querySelector('.recipe-title')?.textContent || 'Коктейль';
            const url = window.location.href;

            if (navigator.share) {
                try {
                    await navigator.share({
                        title: title,
                        text: 'Спробуй цей коктейль!',
                        url: url
                    });
                } catch (err) {
                    // User cancelled or share failed
                    console.log('Share cancelled');
                }
            } else {
                // Fallback to clipboard
                try {
                    await navigator.clipboard.writeText(url);
                    showToast('Посилання скопійовано!');
                } catch (err) {
                    // Clipboard failed, show manual copy
                    prompt('Скопіюйте посилання:', url);
                }
            }
        });
    }
}

/**
 * Initialize add to event button
 */
function initAddToEventButton() {
    const addToEventBtn = document.getElementById('addToEventBtn');
    
    if (addToEventBtn) {
        addToEventBtn.addEventListener('click', function() {
            // Store cocktail info in session storage
            const cocktailName = document.querySelector('.recipe-title')?.textContent;
            if (cocktailName) {
                sessionStorage.setItem('selectedCocktail', cocktailName);
            }
            
            // Redirect to events
            window.location.href = '/events/';
        });
    }
}

/**
 * Initialize reviews modal
 */
function initReviewsModal() {
    const addReviewBtn = document.querySelector('.add-review-btn');
    
    if (addReviewBtn) {
        addReviewBtn.addEventListener('click', function() {
            // Create modal
            const modal = document.createElement('div');
            modal.className = 'review-modal';
            modal.innerHTML = `
                <div class="review-modal-overlay"></div>
                <div class="review-modal-content">
                    <h3>Додати відгук</h3>
                    <div class="review-stars">
                        ${[1,2,3,4,5].map(i => `
                            <svg class="review-star" data-rating="${i}" viewBox="0 0 24 24" stroke-width="1.5">
                                <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
                            </svg>
                        `).join('')}
                    </div>
                    <textarea class="review-textarea" placeholder="Напишіть ваш відгук..."></textarea>
                    <div class="review-modal-buttons">
                        <button class="btn btn-secondary cancel-review">Скасувати</button>
                        <button class="btn btn-primary submit-review">Надіслати</button>
                    </div>
                </div>
            `;

            // Add modal styles
            const style = document.createElement('style');
            style.textContent = `
                .review-modal {
                    position: fixed;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    z-index: 1000;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    animation: fadeIn 0.3s ease-out;
                }
                .review-modal-overlay {
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background: rgba(0, 0, 0, 0.8);
                    backdrop-filter: blur(5px);
                }
                .review-modal-content {
                    position: relative;
                    background: #111;
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 20px;
                    padding: 24px;
                    max-width: 400px;
                    width: 90%;
                    animation: slideUp 0.3s ease-out;
                }
                .review-modal-content h3 {
                    color: #fff;
                    margin-bottom: 16px;
                    text-align: center;
                }
                .review-stars {
                    display: flex;
                    justify-content: center;
                    gap: 8px;
                    margin-bottom: 16px;
                }
                .review-star {
                    width: 32px;
                    height: 32px;
                    cursor: pointer;
                    fill: none;
                    stroke: rgba(255, 255, 255, 0.3);
                    transition: all 0.2s;
                }
                .review-star:hover,
                .review-star.active {
                    fill: #34A853;
                    stroke: #34A853;
                }
                .review-textarea {
                    width: 100%;
                    min-height: 100px;
                    background: rgba(255, 255, 255, 0.05);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 12px;
                    padding: 12px;
                    color: #fff;
                    font-size: 14px;
                    resize: vertical;
                    margin-bottom: 16px;
                }
                .review-textarea:focus {
                    outline: none;
                    border-color: #34A853;
                }
                .review-modal-buttons {
                    display: flex;
                    gap: 12px;
                }
                .review-modal-buttons .btn {
                    flex: 1;
                    padding: 12px;
                }
                @keyframes fadeIn {
                    from { opacity: 0; }
                    to { opacity: 1; }
                }
                @keyframes slideUp {
                    from { opacity: 0; transform: translateY(20px); }
                    to { opacity: 1; transform: translateY(0); }
                }
            `;
            document.head.appendChild(style);
            document.body.appendChild(modal);

            // Star rating interaction
            let selectedRating = 0;
            const stars = modal.querySelectorAll('.review-star');
            stars.forEach(star => {
                star.addEventListener('click', function() {
                    selectedRating = parseInt(this.dataset.rating);
                    stars.forEach((s, i) => {
                        s.classList.toggle('active', i < selectedRating);
                    });
                });

                star.addEventListener('mouseenter', function() {
                    const hoverRating = parseInt(this.dataset.rating);
                    stars.forEach((s, i) => {
                        s.style.fill = i < hoverRating ? '#34A853' : 'none';
                        s.style.stroke = i < hoverRating ? '#34A853' : 'rgba(255, 255, 255, 0.3)';
                    });
                });
            });

            modal.querySelector('.review-stars').addEventListener('mouseleave', function() {
                stars.forEach((s, i) => {
                    s.style.fill = i < selectedRating ? '#34A853' : 'none';
                    s.style.stroke = i < selectedRating ? '#34A853' : 'rgba(255, 255, 255, 0.3)';
                });
            });

            // Close modal
            modal.querySelector('.review-modal-overlay').addEventListener('click', () => {
                modal.remove();
                style.remove();
            });

            modal.querySelector('.cancel-review').addEventListener('click', () => {
                modal.remove();
                style.remove();
            });

            // Submit review
            modal.querySelector('.submit-review').addEventListener('click', () => {
                const text = modal.querySelector('.review-textarea').value;
                if (selectedRating === 0) {
                    showToast('Оберіть рейтинг');
                    return;
                }
                if (!text.trim()) {
                    showToast('Напишіть відгук');
                    return;
                }
                
                // Here you would submit to the server
                showToast('Відгук надіслано!');
                modal.remove();
                style.remove();
            });
        });
    }
}

/**
 * Show toast notification
 */
function showToast(message, duration = 3000) {
    // Remove existing toast
    const existingToast = document.querySelector('.toast-notification');
    if (existingToast) {
        existingToast.remove();
    }

    const toast = document.createElement('div');
    toast.className = 'toast-notification';
    toast.textContent = message;
    toast.style.cssText = `
        position: fixed;
        bottom: 100px;
        left: 50%;
        transform: translateX(-50%);
        background: #34A853;
        color: white;
        padding: 12px 24px;
        border-radius: 10px;
        font-size: 14px;
        font-weight: 500;
        z-index: 10000;
        animation: toastIn 0.3s ease-out;
    `;

    const style = document.createElement('style');
    style.textContent = `
        @keyframes toastIn {
            from { opacity: 0; transform: translateX(-50%) translateY(20px); }
            to { opacity: 1; transform: translateX(-50%) translateY(0); }
        }
        @keyframes toastOut {
            from { opacity: 1; transform: translateX(-50%) translateY(0); }
            to { opacity: 0; transform: translateX(-50%) translateY(20px); }
        }
    `;
    document.head.appendChild(style);
    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'toastOut 0.3s ease-out forwards';
        setTimeout(() => {
            toast.remove();
            style.remove();
        }, 300);
    }, duration);
}

/**
 * Lazy load images
 */
function initLazyLoad() {
    const images = document.querySelectorAll('img[data-src]');
    
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
                observer.unobserve(img);
            }
        });
    });

    images.forEach(img => imageObserver.observe(img));
}

// Initialize lazy loading
initLazyLoad();
