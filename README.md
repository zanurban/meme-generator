# Meme Generator — Project description and instructions

Overview
--------
Meme Generator is a small web application for quickly creating memes. A user can upload an image, enter top and bottom text, and download the generated image. The project is intended to be easy to run and reproducible using Docker, meeting the assignment requirements.

Key features
------------
- Image upload (supported formats: JPG, JPEG, PNG, GIF, BMP)
- Top and bottom text overlay (classic meme format)
- Automatic text sizing and wrapping to avoid overflow
- Download/export generated image
- Easy run via Docker and (optionally) Docker Compose

Technologies
------------
- Python 3.x + Flask (backend)
- Pillow (image processing)
- HTML/CSS/JavaScript (frontend)
- Docker (+ optional Docker Compose)

How it works (brief technical description)
-----------------------------------------
1. The user uploads an image and provides text through a web form.
2. The browser sends a POST request to the Flask server with the file and parameters.
3. The server validates and (optionally) rescales the image, then draws the text using Pillow.
4. If input text is long, the application reduces font size or wraps text so it does not overflow the image bounds.
5. The generated image is saved temporarily and returned to the user for download.

Constraints and recommendations
-------------------------------
- Recommended maximum dimensions: 1200x900 (configurable in source).
- Maximum upload size: check `app.py` (typically ~16 MB).
- Long captions will be auto-resized to avoid clipping; for very long messages consider shortening them.

Local installation
------------------
1. Clone the repository:

```bash
git clone <REPO_URL>
cd <REPO_FOLDER>
```

2. Confirm these files are present: `app.py`, `requirements.txt`, `Dockerfile`, `templates/` and, if used, `docker-compose.yml`.

Run with Docker (recommended)
----------------------------
Build the Docker image:

```bash
docker build -t meme-generator:latest .
```

Run the container (example mapping port 5000):

```bash
docker run --rm -p 5000:5000 meme-generator:latest
```

Open the application in your browser:

```
http://localhost:5000/
```

Run with Docker Compose (optional)
----------------------------------
Build and run with compose:

```bash
docker-compose up --build
```

Run in background (detached):

```bash
docker-compose up -d --build
```

View logs:

```bash
docker-compose logs -f
# or
docker logs -f <container_id>
```

Recommended `.dockerignore` / `.gitignore`
------------------------------------------
Add a `.dockerignore` to speed builds and avoid copying unnecessary files:

```
__pycache__/
.git
venv/
uploads/
*.pyc
.env
```

Repository structure (expected)
-------------------------------
- `app.py` — main Flask application (file upload, image processing)
- `requirements.txt` — Python dependencies
- `Dockerfile` — Docker build instructions
- `docker-compose.yml` — optional, for easy local multi-service run
- `templates/index.html` — main web UI
- `uploads/` — temporary uploads (should be ignored in Git)

PDF submission instructions (assignment requirement)
----------------------------------------------------
Your PDF must include:
1. The GitHub repository URL (for example: `https://github.com/username/repo`).
2. A screenshot of the repository main page showing that the `Dockerfile` and source code are present. The screenshot should show the visible portion of the `README.md` with run instructions.

Tip: include a terminal screenshot showing a successful `docker build` if you want to document the build step.

Optional (bonus) — GitHub Actions workflow
-----------------------------------------
You can add a workflow at `.github/workflows/docker-build.yml` that triggers on `push` and verifies the project builds with Docker. The workflow in this repository performs the following:
- `actions/checkout` to retrieve the code
- setup buildx for Docker
- `docker build -t meme-generator:ci .` to ensure the image builds
- run the built image and perform a simple HTTP health-check against the application root

Note: the workflow does not push images to a registry; it only validates a successful build and basic health of the container.

Checklist (for submission)
--------------------------
- [ ] The repository is publicly available on GitHub.
- [ ] The repository contains the application source code, a `Dockerfile`, and this `README.md` with run instructions.
- [ ] (If applicable) `docker-compose.yml` exists and works.
- [ ] Locally tested: `docker build -t meme-generator:latest .` and `docker run --rm -p 5000:5000 meme-generator:latest` with `http://localhost:5000/` reachable.
- [ ] PDF report contains the repository URL and a screenshot of the repository main page.
- [ ] (Bonus) `.github/workflows/docker-build.yml` exists and validates the Docker build on push.

Contact and license
-------------------
Open an issue in the repository or add contact details here. Optionally add a `LICENSE` file (for example, MIT).

---

If you want I can:
- add a `.dockerignore` file to the repo,
- keep a backup of the previous README as `README.backup.md`,
- add an English-to-Slovenian or more formal translation,
- or adjust the GitHub Actions workflow to run tests or push built images to a registry.
