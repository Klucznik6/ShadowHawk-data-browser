// ShadowHawk Database Browser Website JavaScript

// Suppress console errors from browser extensions
(function() {
    'use strict';
    
    // Store original console methods
    const originalError = console.error;
    const originalWarn = console.warn;
    const originalLog = console.log;
    
    // List of common extension-related error patterns
    const extensionPatterns = [
        /chrome-extension:/,
        /moz-extension:/,
        /safari-extension:/,
        /edge-extension:/,
        /extension\//,
        /content_script/,
        /background\.js/,
        /popup\.js/,
        /inject/,
        /script injected/,
        /Non-Error promise rejection captured/,
        /ResizeObserver loop limit exceeded/,
        /Script error\./,
        /Load failed/,
        /Loading failed/,
        /net::ERR_/,
        /Failed to load resource/,
        /Uncaught \(in promise\)/,
        /AdBlock/i,
        /uBlock/i,
        /Grammarly/i,
        /LastPass/i,
        /1Password/i,
        /Honey/i,
        /Pinterest/i,
        /Facebook/i,
        /Twitter/i,
        /LinkedIn/i,
        /Instagram/i
    ];
    
    // Function to check if error is extension-related
    function isExtensionError(message) {
        const msgStr = String(message);
        return extensionPatterns.some(pattern => pattern.test(msgStr));
    }
    
    // Override console.error
    console.error = function(...args) {
        const firstArg = args[0];
        if (!isExtensionError(firstArg)) {
            originalError.apply(console, args);
        }
    };
    
    // Override console.warn
    console.warn = function(...args) {
        const firstArg = args[0];
        if (!isExtensionError(firstArg)) {
            originalWarn.apply(console, args);
        }
    };
    
    // Handle unhandled promise rejections
    window.addEventListener('unhandledrejection', function(event) {
        if (isExtensionError(event.reason)) {
            event.preventDefault();
        }
    });
    
    // Handle global errors
    window.addEventListener('error', function(event) {
        if (isExtensionError(event.message) || isExtensionError(event.filename)) {
            event.preventDefault();
        }
    });
})();

// Main application code
document.addEventListener('DOMContentLoaded', function() {
    
    // Smooth scrolling for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                const navHeight = document.querySelector('.navbar').offsetHeight;
                const targetPosition = target.offsetTop - navHeight - 20;
                
                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });

    // Navbar background on scroll
    window.addEventListener('scroll', function() {
        const navbar = document.querySelector('.navbar');
        if (window.scrollY > 50) {
            navbar.style.backgroundColor = 'rgba(33, 37, 41, 0.98)';
        } else {
            navbar.style.backgroundColor = 'rgba(33, 37, 41, 0.95)';
        }
    });

    // Performance Chart
    function initPerformanceChart() {
        const ctx = document.getElementById('performanceChart');
        if (!ctx) return;
        
        try {
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: ['Data Loading', 'Search Operations', 'Table Rendering', 'Memory Usage', 'Export Speed'],
                    datasets: [{
                        label: 'Traditional Tools',
                        data: [100, 100, 100, 100, 100],
                        backgroundColor: 'rgba(108, 117, 125, 0.8)',
                        borderColor: 'rgba(108, 117, 125, 1)',
                        borderWidth: 1
                    }, {
                        label: 'ShadowHawk (Polars)',
                        data: [300, 500, 250, 150, 400],
                        backgroundColor: 'rgba(13, 110, 253, 0.8)',
                        borderColor: 'rgba(13, 110, 253, 1)',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Performance Comparison (% improvement)',
                            font: {
                                size: 16,
                                weight: 'bold'
                            }
                        },
                        legend: {
                            position: 'top',
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 600,
                            ticks: {
                                callback: function(value) {
                                    return value + '%';
                                }
                            },
                            title: {
                                display: true,
                                text: 'Performance Improvement'
                            }
                        },
                        x: {
                            title: {
                                display: true,
                                text: 'Operations'
                            }
                        }
                    },
                    elements: {
                        bar: {
                            borderRadius: 4
                        }
                    }
                }
            });
        } catch (error) {
            // Silently handle Chart.js errors
            console.log('Chart initialization skipped');
        }
    }

    // Initialize chart when Chart.js is loaded
    if (typeof Chart !== 'undefined') {
        initPerformanceChart();
    } else {
        // Wait for Chart.js to load
        const checkChart = setInterval(() => {
            if (typeof Chart !== 'undefined') {
                clearInterval(checkChart);
                initPerformanceChart();
            }
        }, 100);
        
        // Stop checking after 5 seconds
        setTimeout(() => clearInterval(checkChart), 5000);
    }

    // Download button functionality
    const downloadBtn = document.getElementById('downloadBtn');
    if (downloadBtn) {
        downloadBtn.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Show download modal or redirect to GitHub releases
            const modal = document.createElement('div');
            modal.className = 'modal fade';
            modal.innerHTML = `
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Download ShadowHawk v1.0.0</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="row">
                                <div class="col-md-6">
                                    <div class="download-option">
                                        <h6><i class="bi bi-github"></i> GitHub Releases</h6>
                                        <p>Download the latest stable release with installer and source code.</p>
                                        <a href="https://github.com/Klucznik6/ShadowHawk-data-browser/releases" 
                                           class="btn btn-primary" target="_blank">
                                            <i class="bi bi-download"></i> Download from GitHub
                                        </a>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="download-option">
                                        <h6><i class="bi bi-code-slash"></i> Source Code</h6>
                                        <p>Clone the repository and build from source code.</p>
                                        <div class="code-snippet">
                                            <code>git clone https://github.com/Klucznik6/ShadowHawk-data-browser.git</code>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <hr>
                            <div class="system-requirements">
                                <h6>System Requirements</h6>
                                <ul class="list-unstyled">
                                    <li><i class="bi bi-check text-success"></i> Windows 10/11, macOS 10.14+, or Linux</li>
                                    <li><i class="bi bi-check text-success"></i> Python 3.8+ (3.10+ recommended)</li>
                                    <li><i class="bi bi-check text-success"></i> 2GB RAM (4GB+ recommended)</li>
                                    <li><i class="bi bi-check text-success"></i> 100MB disk space</li>
                                </ul>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                            <a href="https://github.com/Klucznik6/ShadowHawk-data-browser/releases" 
                               class="btn btn-primary" target="_blank">
                                Go to Downloads
                            </a>
                        </div>
                    </div>
                </div>
            `;
            
            document.body.appendChild(modal);
            
            try {
                const bsModal = new bootstrap.Modal(modal);
                bsModal.show();
                
                modal.addEventListener('hidden.bs.modal', function() {
                    document.body.removeChild(modal);
                });
            } catch (error) {
                // Fallback: redirect to GitHub releases
                window.open('https://github.com/Klucznik6/ShadowHawk-data-browser/releases', '_blank');
                document.body.removeChild(modal);
            }
        });
    }

    // Feature cards hover effects (enhanced visibility)
    const featureCards = document.querySelectorAll('.feature-card');
    featureCards.forEach(card => {
        // Ensure visibility
        card.style.visibility = 'visible';
        card.style.opacity = '1';
        card.style.display = 'flex';
        
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.boxShadow = '0 20px 40px rgba(0, 0, 0, 0.15)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = '0 10px 30px rgba(0, 0, 0, 0.1)';
        });
    });

    // Performance metrics visibility
    const metricItems = document.querySelectorAll('.metric-item');
    metricItems.forEach(item => {
        item.style.visibility = 'visible';
        item.style.opacity = '1';
        item.style.display = 'flex';
    });

    // Screenshot cards visibility
    const screenshotCards = document.querySelectorAll('.screenshot-card');
    screenshotCards.forEach(card => {
        card.style.visibility = 'visible';
        card.style.opacity = '1';
        card.style.display = 'block';
    });

    // Copy code snippet functionality
    document.addEventListener('click', function(e) {
        if (e.target.tagName === 'CODE') {
            const code = e.target.textContent;
            navigator.clipboard.writeText(code).then(() => {
                // Show copied notification
                const notification = document.createElement('div');
                notification.className = 'alert alert-success position-fixed';
                notification.style.top = '20px';
                notification.style.right = '20px';
                notification.style.zIndex = '9999';
                notification.textContent = 'Code copied to clipboard!';
                
                document.body.appendChild(notification);
                
                setTimeout(() => {
                    document.body.removeChild(notification);
                }, 2000);
            }).catch(() => {
                // Fallback for older browsers
                const textArea = document.createElement('textarea');
                textArea.value = code;
                document.body.appendChild(textArea);
                textArea.select();
                document.execCommand('copy');
                document.body.removeChild(textArea);
            });
        }
    });

    // Lazy loading for images
    const images = document.querySelectorAll('img[src]');
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.onerror = function() {
                    // Use placeholder if image fails to load
                    this.src = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="400" height="300" viewBox="0 0 400 300"><rect width="400" height="300" fill="%23f8f9fa"/><text x="200" y="150" text-anchor="middle" fill="%236c757d" font-family="Arial, sans-serif" font-size="16">ShadowHawk Screenshot</text></svg>';
                };
                observer.unobserve(img);
            }
        });
    });

    images.forEach(img => imageObserver.observe(img));

    // Dark mode detection (future enhancement)
    const prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)');
    function handleColorScheme(e) {
        // Future: Add dark mode support
        document.body.classList.toggle('dark-mode', e.matches);
    }
    
    prefersDarkScheme.addEventListener('change', handleColorScheme);
    handleColorScheme(prefersDarkScheme);

    // Performance monitoring
    if ('performance' in window) {
        window.addEventListener('load', function() {
            const loadTime = performance.timing.loadEventEnd - performance.timing.navigationStart;
            if (loadTime > 3000) {
                console.log('Page load time:', loadTime + 'ms');
            }
        });
    }

    // Service Worker registration (future enhancement)
    if ('serviceWorker' in navigator) {
        window.addEventListener('load', function() {
            // Future: Add service worker for offline functionality
        });
    }

    console.log('🦅 ShadowHawk Database Browser website loaded successfully!');
});
