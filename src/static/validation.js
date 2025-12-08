document.addEventListener("DOMContentLoaded", function () {
    const clientErrorsContainer = document.getElementById("client-errors");

    function showClientErrors(errors) {
        if (!clientErrorsContainer) return;
        clientErrorsContainer.innerHTML = "";

        if (!errors.length) {
            clientErrorsContainer.style.display = "none";
            return;
        }

        const ul = document.createElement("ul");
        errors.forEach((err) => {
            const li = document.createElement("li");
            li.textContent = err;
            ul.appendChild(li);
        });

        clientErrorsContainer.appendChild(ul);
        clientErrorsContainer.style.display = "block";
    }

    const form = document.getElementById("register-form");
    if (!form) return;

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
            errors.push("Email is too long.");
        }
    }

    function validatePasswordFields(password, confirmPassword, errors) {
        // Matching passwords
        if (!password || !confirmPassword) {
            errors.push("Password and confirmation are required.");
            return;
        }
        if (password !== confirmPassword) {
            errors.push("Passwords do not match.");
        }

        // Password complexity
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
            errors.push(
                "Password must contain at least one special character."
            );
        }
    }

    function validateRegistrationForm() {
        const errors = [];

        const email = form.email.value;
        const password = form.password.value;
        const confirmPassword = form.confirm_password.value;

        validateEmailField(email, errors);
        validatePasswordFields(password, confirmPassword, errors);

        return errors;
    }

    form.addEventListener("submit", (event) => {
        const errors = validateRegistrationForm();
        if (errors.length > 0) {
            event.preventDefault();
            showClientErrors(errors);
        }
    });
});
