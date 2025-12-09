# app-sec-login-daemon

A simple but secure login daemon written in Python.

## Setup

In order to be able to run the app, you will need to copy the `.env.example` file and modify it with your credentials.

```bash
cp .env.example .env
```

Note that email validation of the token is at the moment not mandatory, but an error will be logged if the credentials aren't set. Email credential setup is still mandatory if you want to use the password reset feature.

### Example: Add a Google App Password (for Gmail)

If you plan to send email through Gmail (SMTP) from this application, Google requires either OAuth2 or an App Password when 2-Step Verification is enabled. An App Password is a 16-character passcode that gives a less secure app access to your Google Account. Follow these steps to create one and add it to your `.env` file.

1. **Enable 2-Step Verification**: Sign in to your Google Account at `https://myaccount.google.com/` and go to **Security** → **2-Step Verification**. Follow the prompts to enable it if you haven't already.
2. **Open App Passwords**: In **Security**, find the **App passwords** section and click it. You may need to sign in again.
3. **Create an App Password**: Under "Select app", choose **Mail**. Under "Select device", choose **Other (Custom name)** and enter a name like `app-sec-login-daemon`. Click **Generate**.
4. **Copy the generated password**: Google will show a 16-character app password (no spaces). Copy it — you will not be able to see it again.
5. **Add it to `.env`**: Open your `.env` and set the mail password value. For example:

```bash
MAIL_PASSWORD=your-16-char-app-password
MAIL_USERNAME=youremail@gmail.com
MAIL_SERVER=smtp.gmail.com
```

For reference, see Google's help page: `https://support.google.com/accounts/answer/185833`.

## Run the app

While at the root of the project, run :

```bash
docker compose up --build
```

Console logs will be displayed on stdout. In order to exit, use the standard `^c`.

## MFA (or 2FA, 2-factor authentication)

In `app.py`, the line `if mfa_enabled:` is a conditional statement that branches the login flow based on whether the user has multi-factor authentication (MFA) enabled on their account.

### What It Does

After a successful login, the code queries the database to retrieve the `mfa_enabled` flag for the authenticated user. This boolean value indicates whether the user has opted into MFA protection. The `if` statement then evaluates this flag to determine which authentication path to follow.

### The Two Paths

**If MFA is enabled** (`True`): The application stores the user's ID in the session as `pre_auth_user_id` and redirects them to the MFA verification page. This is a temporary, partial authentication state—the user has proven their identity but hasn't yet completed the second authentication factor (like a TOTP code or security key).

**If MFA is disabled** (`False`): The code skips this block and proceeds directly to the next lines, where it sets `user_id` and `email` in the session as fully authenticated credentials, then redirects to the dashboard.

### Security Consideration

Notice that `session.clear()` is called *before* this check. This mitigates **session fixation attacks** by invalidating any pre-existing session data. Then the code selectively populates the session with either partial credentials (for MFA flow) or full credentials (for direct login), ensuring a clean state either way.
