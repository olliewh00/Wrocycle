# Wrocycle Helper: Instructor & Deployment Guide
**Wrocław University of Science & Technology (Politechnika Wrocławska - PWr)**

This guide provides a comprehensive overview of how the **Wrocycle Helper** application works, its technical architecture, and detailed instructions for hosting it—either on Streamlit Community Cloud or self-hosted on a **PWr Virtual Machine (VM)**—before embedding it into a PicoCMS website.

---

## 1. What the Code Does & How It Works

**Wrocycle Helper** is a split-second waste sorting assistant designed specifically for university students living in Wrocław dormitories (e.g., T-15, T-17, T-19). It uses a Vision LLM API (defaulting to Google's flagship `gemini-2.5-flash` model or OpenAI's `gpt-4o-mini`) to classify objects in photos taken by a camera or uploaded files.

### Waste Classification Framework (Ekosystem Wrocław)
The app strictly routes waste according to the official Wrocław municipal fractions:
1. **Plastics & Metals (Yellow / Żółty)**: PET bottles, drink cans, wrappers, Tetra Paks (milk/juice cartons).
2. **Clean Paper (Blue / Niebieski)**: Clean, dry cardboard/paper.
3. **Glass Packaging (Green / Zielony)**: Glass bottles and jars (excluding metal lids).
4. **Bio-Waste (Brown / Brązowy)**: Vegetable/fruit scraps, coffee grounds.
5. **Mixed Waste (Black / Czarny)**: Dirty/oily paper (like pizza boxes), used tissues, receipts, food leftovers, meat, ceramics.
6. **Kaucja (Deposit Return System / Zwrot w Sklepie)**: A special category for returnable PET bottles, aluminum cans, or glass bottles with deposit markings.

### Technical Architecture
The codebase is structured into three primary modules to keep it lightweight and maintainable:
* **`classifier_service.py`**: The core API router. It handles loading environment configurations, initializing the Gemini/OpenAI SDKs, sending images alongside Wrocław rules system instructions, and parsing the response. It strips markdown blocks (like ` ```json `) to guarantee a valid Python dictionary is passed to the frontend.
* **`waste_classifier_app.py`**: The premium web dashboard built with Streamlit. It uses custom CSS styles to render a glassmorphic design, injects custom typography, prompts camera input, and displays large, color-coded glowing blocks matching the official waste bin colors.
* **`waste_classifier_cli.py`**: A desktop/terminal tool utilizing OpenCV. It launches the default webcam (`cv2.VideoCapture(0)`), overlays capture controls, and outputs ANSI-colored results directly into the terminal window.

---

## 2. Option A: Hosting on Streamlit Community Cloud (Quickest)

1. Push the files (`waste_classifier_app.py`, `classifier_service.py`, `requirements.txt`) to a GitHub repository.
2. Sign in to [share.streamlit.io](https://share.streamlit.io/) with your GitHub account.
3. Click **New app**, choose the repository, and select `waste_classifier_app.py` as the entry point.
4. Under **Settings > Secrets**, add the API key:
   ```toml
   GEMINI_API_KEY = "AIzaSy..."
   GEMINI_MODEL = "gemini-2.5-flash"
   ```
5. Deploy. You will receive a public URL (e.g., `https://wrocycle.streamlit.app`).

---

## 3. Option B: Self-Hosting on a PWr Virtual Machine (VM)

For complete control and data privacy, the application can be hosted on a university Linux VM (e.g., Ubuntu Server). Since browsers require **HTTPS** to allow webcam access, we must set up Nginx as a reverse proxy with an SSL certificate.

### Step 1: Install System Dependencies
Connect to the PWr VM via SSH and install required packages:
```bash
sudo apt update
sudo apt install python3-pip python3-venv git nginx snapd -y
```

### Step 2: Clone Code & Configure Environment
Clone your repository or copy the code files to `/var/www/wrocycle`:
```bash
sudo mkdir -p /var/www/wrocycle
sudo chown -R $USER:$USER /var/www/wrocycle
cd /var/www/wrocycle

# Create virtual environment and install requirements
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file in `/var/www/wrocycle/.env`:
```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
```

### Step 3: Set up Systemd Service (Runs App in Background)
To ensure the Streamlit app runs continuously in the background and restarts automatically if the server reboots, create a service file:
```bash
sudo nano /etc/systemd/system/wrocycle.service
```

Add the following configuration:
```ini
[Unit]
Description=Wrocycle Helper Streamlit App
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/var/www/wrocycle
ExecStart=/var/www/wrocycle/venv/bin/streamlit run waste_classifier_app.py --server.port 8501 --server.address 127.0.0.1
Restart=always

[Install]
WantedBy=multi-user.target
```
*(Make sure to adjust `User=ubuntu` to match the VM's login username).*

Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable wrocycle
sudo systemctl start wrocycle
```

### Step 4: Configure Nginx Reverse Proxy with HTTPS
Web browsers block access to cameras inside iframes unless the page is hosted on `https://` (or `localhost` for development). 

Create an Nginx configuration file:
```bash
sudo nano /etc/nginx/sites-available/wrocycle
```

Add the following Nginx server block (replace `wrocycle.pwr.wroc.pl` with your actual VM subdomain):
```nginx
server {
    listen 80;
    server_name wrocycle.pwr.wroc.pl;

    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable the site configuration and restart Nginx:
```bash
sudo ln -s /etc/nginx/sites-available/wrocycle /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Step 5: Get SSL Certificate (Let's Encrypt Certbot)
To obtain a free SSL certificate automatically:
```bash
sudo snap install --classic certbot
sudo ln -s /snap/bin/certbot /usr/bin/certbot
sudo certbot --nginx -d wrocycle.pwr.wroc.pl
```
Certbot will configure SSL automatically and redirect all traffic from HTTP to HTTPS.

---

## 4. Embedding into PicoCMS

Once the app is running on its HTTPS URL (e.g., `https://wrocycle.pwr.wroc.pl`), it can be embedded into any PicoCMS page.

1. Navigate to the PicoCMS root installation.
2. In the `content/` folder, create a file named `wrocycle.md` (e.g., `content/wrocycle.md`):

```markdown
---
Title: Wrocycle Helper
Description: Waste sorting assistant for dorm students
Template: index
---

# Wrocycle Helper

Welcome to the waste sorting assistant. Place your packaging in front of the camera to get an instant category and sorting action.

<iframe 
    src="https://wrocycle.pwr.wroc.pl/?embed=true" 
    width="100%" 
    height="750px" 
    style="border: none; border-radius: 16px; box-shadow: 0 10px 30px rgba(0,0,0,0.15);"
    allow="camera; microphone">
</iframe>
```

### Essential Embedding Attributes:
* **`allow="camera; microphone"`**: Critical. Tells the browser that the host PicoCMS page trusts the iframe enough to let it capture the webcam feed.
* **`?embed=true`**: Query parameter appended to the Streamlit URL that hides the standard Streamlit interface controls, making the app look natively integrated.
* **HTTPS**: The parent site hosting PicoCMS must also be using HTTPS, otherwise the browser won't load the secure iframe context.
