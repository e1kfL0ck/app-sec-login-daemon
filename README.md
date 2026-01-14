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

MFA can be enabled by users inside the app. By default, the demo/testing users come with it pre-enabled. You can use an authenticator app like Proton Authenticator or Authy to scan the QR code and generate time-based one-time passwords (TOTP).

When logging in, after entering your username and password, you will be prompted to enter the 6-digit code from your authenticator app.

## Tailwind CSS Setup

npm is used to manage Tailwind CSS dependencies and build processes. The following instructions guide you through setting up Tailwind CSS for local development and Docker deployment.

### Local Development

1. **Install Node.js dependencies:**

   ```bash
   npm install
   ```

2. **Build CSS (one-time):**

   ```bash
   npm run build:css
   ```

### Docker Deployment

The Dockerfile uses a multi-stage build:

1. **Build stage:** Compiles Tailwind CSS using Node.js
2. **Production stage:** Runs the Flask application with precompiled CSS
Simply build and run normally:

```bash
docker-compose up --build
```
