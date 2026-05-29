# Guide: Embedding Wrocycle Helper in PicoCMS

This guide explains how to host and embed the **Wrocycle Helper** application into a PicoCMS-based website using an HTML `<iframe>`.

---

## Step 1: Host the Streamlit App
To embed the app, it must be running on a publicly accessible server. The easiest way is to deploy it to **Streamlit Community Cloud** (which is free):

1. Put the project files (`waste_classifier_app.py`, `classifier_service.py`, `requirements.txt`, and your `.env` file containing the `GEMINI_API_KEY`) into a private or public GitHub repository.
2. Go to [share.streamlit.io](https://share.streamlit.io/) and log in with GitHub.
3. Click **New app**, select your repository, branch, and set the Main file path to `waste_classifier_app.py`.
4. Under **Advanced settings**, paste the content of your `.env` file (e.g., `GEMINI_API_KEY=AIzaSy...`) into the Secrets box.
5. Click **Deploy**. Once deployed, copy the public URL (e.g., `https://wrocycle-helper.streamlit.app`).

---

## Step 2: Create the PicoCMS Page
PicoCMS is a flat-file CMS, so adding a page is as simple as creating a Markdown file in the `content/` folder of the PicoCMS installation.

Create a new file named `wrocycle.md` in the PicoCMS `content/` directory (e.g., `content/wrocycle.md`):

```markdown
---
Title: Wrocycle Helper
Description: Split-second waste sorting assistant for students.
Template: index
---

# Wrocycle Helper

Welcome to the Wrocław Dormitory Waste Sorting Assistant. Place your item in front of the camera or upload an image below to get a split-second sorting decision.

<iframe 
    src="https://your-deployed-streamlit-app-url.streamlit.app/?embed=true" 
    width="100%" 
    height="750px" 
    style="border: none; border-radius: 16px; box-shadow: 0 10px 30px rgba(0,0,0,0.15);"
    allow="camera; microphone">
</iframe>
```

---

## Crucial Configurations for the Professor

### 1. Enable Camera Access (`allow="camera"`)
Because Wrocycle Helper uses the camera to scan trash, the browser blocks camera access inside iframes by default. The `allow="camera"` attribute **must** be present on the `<iframe>` tag to explicitly grant permission:
```html
allow="camera; microphone"
```

### 2. Streamlit Embed Parameter (`?embed=true`)
When linking the URL in the `src` attribute of the iframe, append `?embed=true` to the end of the URL:
* **Standard URL**: `https://wrocycle-helper.streamlit.app`
* **Embedded URL**: `https://wrocycle-helper.streamlit.app/?embed=true`

This strips Streamlit's default navigation headers, sidebar menus, and footers, making the interface look completely native to the PicoCMS theme.

### 3. HTTPS Requirement
For security reasons, web browsers will only allow camera access (`getUserMedia`) on **secure origins** (websites using `https://` or `localhost`). Ensure the PicoCMS website is served over HTTPS, otherwise the browser will block the webcam snap feature.
