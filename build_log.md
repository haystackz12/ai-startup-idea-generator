# 🛠️ Build Log: AI Startup Idea Generator

This document captures the complete development journey of the **AI Startup Idea Generator**, from initial concept through deployment.

---

## 📌 Project Objective

To create a web-based tool that generates AI startup ideas from user keywords or problems, complete with a name, pitch, logo, branding palette, MVP feature list, and downloadable assets — all in one day.

---

## 🧠 Phase 1: Ideation

* **Goal:** Lightweight MVP that produces a complete startup concept using GPT-4 and DALL·E.
* Tools selected:

  * GPT-4o for idea generation and branding content
  * DALL·E 3 for logo generation
  * Streamlit for UI and web app hosting
  * Python for scripting, logic, and packaging

---

## ⚙️ Phase 2: Initial Build (Day 1)

* Created `app.py` with Streamlit layout
* Built initial prompt template for GPT-4o to generate startup ideas
* Integrated DALL·E image generation
* Output: startup name, tagline, pitch, color palette, MVP list
* Used `st.image()` and `st.columns()` to display branding swatches and logo
* Built `.zip` bundler using `zipfile` and `io.BytesIO()`

---

## 🧪 Phase 3: Testing & Fixes

* ✅ Migrated OpenAI API to v1.0+ (used `client.chat.completions.create`)
* ✅ Fixed image size issue (512x512 deprecated)
* ✅ Converted to generate only one logo by default
* ✅ Added download button using `st.download_button`
* ✅ Created `.gitignore` and `requirements.txt`
* ✅ Made industry tag a required field
* ✅ Resolved session state bugs for logo refresh and idea clearing

---

## 🎨 Phase 4: UX Improvements

* Added "🧹 Clear & Start Over" button
* Added markdown intro to explain the app and usage
* Added Streamlit `secrets.toml` support for API key management
* Improved layout and instructions for user experience

---

## ☁️ Phase 5: Deployment

* Repo pushed to GitHub
* App deployed to Streamlit Cloud:

  * [https://ai-startup-idea-generator-3wfbxmhjzdmtehqofqtx8x.streamlit.app](https://ai-startup-idea-generator-3wfbxmhjzdmtehqofqtx8x.streamlit.app)
* Created `README.md` with badges, screenshot, and usage docs
* Verified secrets setup and auto-deployment from GitHub

---

## ✅ Completed Features Summary

* GPT-powered idea generation
* Moodboard-style branding
* Logo generation
* MVP feature list
* Color palette swatches
* ZIP export of startup assets
* Idea history
* Reset button for new sessions

---

## 📅 Timeline

* **Start:** June 22, 2025 @ 3:00 PM MT
* **Finish:** June 23, 2025 @ 1:45 AM MT
* **Total build time:** \~10 hours

---

## 👤 Created by

**Michael Hastings**

MIT License 2025
