document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("register-form");
  if (!form) return;

  const clientErrorsContainer = document.getElementById("client-errors");

  const dangerousPatterns = [
    /<\s*script/i,
    /on\w+\s*=/i,      // onclick, onerror, etc.
    /javascript\s*:/i,
  ];

  const disallowedCharsSimple = /[<>{};&]/;

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

  function containsDangerousPattern(value) {
    if (!value) return false;
    return dangerousPatterns.some((re) => re.test(value));
  }

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

    if (containsDangerousPattern(email) || disallowedCharsSimple.test(email)) {
      errors.push("Email contains forbidden characters or patterns.");
    }
  }

  function validatePasswordFields(password, confirmPassword, errors) {
    if (!password || !confirmPassword) {
      errors.push("Password and confirmation are required.");
      return;
    }

    if (password !== confirmPassword) {
      errors.push("Passwords do not match.");
    }
    if (password.length < 8) {
      errors.push("Password must be at least 8 characters.");
    }
    if (!/[A-Za-z]/.test(password) || !/\d/.test(password)) {
      errors.push("Password must contain at least one letter and one digit.");
    }
    if (containsDangerousPattern(password)) {
      errors.push("Password contains forbidden patterns.");
    }
  }

  function validateRegistrationForm() {
    const errors = [];

    const email = form.email.value;
    const password = form.password.value;
    const confirmPassword = form.confirm_password.value;

    validateEmailField(email, errors);
    validatePasswordFields(password, confirmPassword, errors);

    console.log("Client-side validation errors:", errors);

    return errors;
  }

  form.addEventListener("submit", function (e) {
    const errors = validateRegistrationForm();
    if (errors.length > 0) {
      e.preventDefault();
      showClientErrors(errors);
    }
  });
});
