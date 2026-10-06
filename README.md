
## Permanent Render deployment

The repository includes `render.yaml` for a permanent Render deployment. It creates a Python web service plus a managed PostgreSQL database, runs migrations and `collectstatic`, and serves Django through Gunicorn with WhiteNoise. Connect the GitHub repository in Render and deploy the Blueprint; set `CSRF_TRUSTED_ORIGINS` to the final `https://<your-service>.onrender.com` URL if Render does not populate it automatically.
