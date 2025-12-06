// auth.js - Additional JavaScript for authentication pages

document.addEventListener('DOMContentLoaded', function() {
    // Real-time password strength indicator
    const passwordInput = document.getElementById('password1');
    if (passwordInput) {
        const strengthIndicator = document.createElement('div');
        strengthIndicator.className = 'password-strength';
        passwordInput.parentNode.appendChild(strengthIndicator);
        
        passwordInput.addEventListener('input', function() {
            const password = this.value;
            let strength = 0;
            let text = '';
            let color = '';
            
            if (password.length >= 8) strength++;
            if (/[A-Z]/.test(password)) strength++;
            if (/[0-9]/.test(password)) strength++;
            if (/[^A-Za-z0-9]/.test(password)) strength++;
            
            switch(strength) {
                case 0:
                case 1:
                    text = 'Weak';
                    color = '#d32f2f';
                    break;
                case 2:
                    text = 'Fair';
                    color = '#ff8f00';
                    break;
                case 3:
                    text = 'Good';
                    color = '#2e7d32';
                    break;
                case 4:
                    text = 'Strong';
                    color = '#1b5e20';
                    break;
            }
            
            strengthIndicator.innerHTML = `<span style="color:${color}; font-weight:bold;">${text}</span>`;
        });
    }
    
    // Form validation for password match
    const password2 = document.getElementById('password2');
    if (password2) {
        password2.addEventListener('input', function() {
            const password1 = document.getElementById('password1').value;
            const password2 = this.value;
            
            if (password2 && password1 !== password2) {
                this.style.borderColor = '#d32f2f';
                this.style.boxShadow = '0 0 0 3px rgba(211, 47, 47, 0.1)';
                
                // Show error message
                let errorMsg = this.parentNode.querySelector('.password-match-error');
                if (!errorMsg) {
                    errorMsg = document.createElement('div');
                    errorMsg.className = 'error-message password-match-error';
                    this.parentNode.appendChild(errorMsg);
                }
                errorMsg.textContent = 'Passwords do not match';
            } else {
                this.style.borderColor = '#2e7d32';
                this.style.boxShadow = '0 0 0 3px rgba(46, 125, 50, 0.1)';
                
                // Remove error message
                const errorMsg = this.parentNode.querySelector('.password-match-error');
                if (errorMsg) {
                    errorMsg.remove();
                }
            }
        });
    }
    
    // Add CSS for password strength indicator
    const style = document.createElement('style');
    style.textContent = `
        .password-strength {
            margin-top: 5px;
            font-size: 13px;
            height: 18px;
        }
        .nav-links a.active {
            background-color: var(--primary);
            color: white !important;
        }
        .nav-links a.active:hover {
            background-color: var(--primary-dark);
        }
    `;
    document.head.appendChild(style);
});