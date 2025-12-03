# app-sec-login-daemon

A simple but secure login daemon written in Python.

## Setup

In order to be able to run the app, you will need to copy the `.env.example` file and modify it with your credentials.

```bash
cp .env.example .env
```

Note that email validation of the token is at the moment not mandatory, but an error will be logged if the credentials aren't set.

## Run

While at the root of the project, run :

```bash
docker compose up --build
```

Console logs will be displayed on stdout. In order to exit, use the standard `^c`.
