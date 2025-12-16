/**
 * Form Validation Script for User Registration Lab
 * Handles client-side validation for all forms
 */

document.addEventListener("DOMContentLoaded", function () {
    // Initialize validation for different forms
    initRegisterFormValidation();
    initLoginFormValidation();
    initPasswordResetFormValidation();
    initForgottenPasswordFormValidation();
});

/**
 * Utility function to show client-side errors
 */
function showClientErrors(containerId, errors) {
    const container = document.getElementById(containerId);
    if (!container) return;

    container.innerHTML = "";

    if (!errors.length) {
        container.style.display = "none";
        container.classList.add("hidden");
        return;
    }

    const ul = document.createElement("ul");
    ul.className = "list-disc list-inside space-y-1";

    errors.forEach((err) => {
        const li = document.createElement("li");
        li.textContent = err;
        ul.appendChild(li);
    });

    container.appendChild(ul);
    container.style.display = "block";
    container.classList.remove("hidden");
}

/**
 * Email validation
 */
function validateEmailField(email, errors) {
    email = email.trim().toLowerCase();

    if (!email) {
        errors.push("Email is required.");
        return;
    }

    const re = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;
    if (!re.test(email)) {
        errors.push("Email format is invalid.");
    }

    if (email.length > 255) {
        errors.push("Email format is invalid.");
    }
}

/**
 * Password strength validation
 */
function validatePasswordStrength(password, errors) {
    if (!password) {
        errors.push("Password is required.");
        return;
    }

    if (password.length < 8) {
        errors.push("Password must be at least 8 characters.");
    }
    if (!/[A-Z]/.test(password)) {
        errors.push("Password must contain at least one uppercase letter.");
    }
    if (!/[a-z]/.test(password)) {
        errors.push("Password must contain at least one lowercase letter.");
    }
    if (!/\d/.test(password)) {
        errors.push("Password must contain at least one digit.");
    }
    if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
        errors.push("Password must contain at least one special character.");
    }
}

/**
 * Password match validation
 */
function validatePasswordMatch(password, confirmPassword, errors) {
    if (!password || !confirmPassword) {
        errors.push("Password and confirmation are required.");
        return;
    }
    if (password !== confirmPassword) {
        errors.push("Passwords do not match.");
    }
}

/**
 * Registration form validation
 */
function initRegisterFormValidation() {
    const form = document.getElementById("register-form");
    if (!form) return;

    function validateRegistrationForm() {
        const errors = [];
        const email = form.email.value;
        const password = form.password.value;
        const confirmPassword = form.confirm_password.value;

        validateEmailField(email, errors);
        validatePasswordStrength(password, errors);
        validatePasswordMatch(password, confirmPassword, errors);

        return errors;
    }

    form.addEventListener("submit", (event) => {
        const errors = validateRegistrationForm();
        if (errors.length > 0) {
            event.preventDefault();
            showClientErrors("client-errors", errors);
            // Scroll to errors with reduced motion support
            const errorContainer = document.getElementById("client-errors");
            if (errorContainer) {
                const prefersReducedMotion = window.matchMedia(
                    "(prefers-reduced-motion: reduce)"
                ).matches;
                errorContainer.scrollIntoView({
                    behavior: prefersReducedMotion ? "auto" : "smooth",
                    block: "center",
                });
            }
        }
    });
}

/**
 * Login form validation
 */
function initLoginFormValidation() {
    const form = document.getElementById("login-form");
    if (!form) return;

    function validateLoginForm() {
        const errors = [];
        const email = form.email.value;
        const password = form.password.value;

        validateEmailField(email, errors);

        if (!password) {
            errors.push("Password is required.");
        }

        return errors;
    }

    form.addEventListener("submit", (event) => {
        const errors = validateLoginForm();
        if (errors.length > 0) {
            event.preventDefault();
            showClientErrors("client-errors", errors);
            // Scroll to errors with reduced motion support
            const errorContainer = document.getElementById("client-errors");
            if (errorContainer) {
                const prefersReducedMotion = window.matchMedia(
                    "(prefers-reduced-motion: reduce)"
                ).matches;
                errorContainer.scrollIntoView({
                    behavior: prefersReducedMotion ? "auto" : "smooth",
                    block: "center",
                });
            }
        }
    });
}

/**
 * Password reset form validation
 */
function initPasswordResetFormValidation() {
    const form = document.getElementById("password-reset-form");
    if (!form) return;

    function validatePasswordResetForm() {
        const errors = [];
        const password = form.password.value;
        const confirmPassword = form.confirm_password.value;

        validatePasswordStrength(password, errors);
        validatePasswordMatch(password, confirmPassword, errors);

        return errors;
    }

    form.addEventListener("submit", (event) => {
        const errors = validatePasswordResetForm();
        if (errors.length > 0) {
            event.preventDefault();
            showClientErrors("client-errors", errors);
            // Scroll to errors with reduced motion support
            const errorContainer = document.getElementById("client-errors");
            if (errorContainer) {
                const prefersReducedMotion = window.matchMedia(
                    "(prefers-reduced-motion: reduce)"
                ).matches;
                errorContainer.scrollIntoView({
                    behavior: prefersReducedMotion ? "auto" : "smooth",
                    block: "center",
                });
            }
        }
    });
}

/**
 * Forgotten password form validation
 */
function initForgottenPasswordFormValidation() {
    const form = document.getElementById("forgotten-password-form");
    if (!form) return;

    function validateForgottenPasswordForm() {
        const errors = [];
        const email = form.email.value;

        validateEmailField(email, errors);

        return errors;
    }

    form.addEventListener("submit", (event) => {
        const errors = validateForgottenPasswordForm();
        if (errors.length > 0) {
            event.preventDefault();
            showClientErrors("client-errors", errors);
            // Scroll to errors with reduced motion support
            const errorContainer = document.getElementById("client-errors");
            if (errorContainer) {
                const prefersReducedMotion = window.matchMedia(
                    "(prefers-reduced-motion: reduce)"
                ).matches;
                errorContainer.scrollIntoView({
                    behavior: prefersReducedMotion ? "auto" : "smooth",
                    block: "center",
                });
            }
        }
    });
}
