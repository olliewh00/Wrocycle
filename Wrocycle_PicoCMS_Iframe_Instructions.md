

#### 1. Create a page in PicoCMS
Create a new Markdown file (e.g., `wrocycle.md`) in your PicoCMS installation under the `content/` directory (e.g., `content/wrocycle.md`).

#### 2. Paste the embedding code
Add the following content to the page. This embeds the application inside a clean, modern card layout:

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

*(Note: Please replace the `src` attribute URL above with the actual deployed app URL).*

---

### ⚠️ Crucial Details for Embedding Success:

1. **Camera Permissions (`allow="camera"`)**
   Because the app uses the device's camera to scan waste, web browsers block camera access inside iframes by default. The `allow="camera; microphone"` attribute must be present in the `<iframe>` tag to explicitly override this.
   
2. **Seamless Styling (`?embed=true`)**
   Ensure the `?embed=true` query parameter is appended to the end of your Streamlit app link in the `src` attribute. This automatically hides Streamlit’s menu headers and footers so the application integrates natively into your website template.

3. **HTTPS Requirement**
   Modern browsers block webcam access (`getUserMedia`) on insecure connections. Both your main website and the Streamlit app must be served over secure `https://` URLs for the camera feature to work.
