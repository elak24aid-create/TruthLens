# Render Web Service Deployment Guide

This guide provides exact step-by-step instructions to manually connect your existing TruthLens GitHub repository to Render for a free, real cloud deployment.

**IMPORTANT LIMITATION (PERSISTENCE):** 
Because we are using a free tier on Render without a connected paid database (like PostgreSQL or AWS S3), the backend operates with an ephemeral filesystem. This means that local JSON files storing **users, history data, community reports, and uploaded media** will be wiped clean every time the Render service restarts (which occurs during redeploys, or after periods of inactivity on the free tier). The core detection engine and logic will continue to function normally.

## Step-by-Step Instructions

1. **Log in to Render**
   - Go to [https://render.com](https://render.com) and log in.

2. **Create a New Web Service**
   - Click the **New +** button in the top right.
   - Select **Web Service**.
   - Under "Connect a repository", authorize your GitHub account if you haven't already.
   - Select the **TruthLens** repository: `https://github.com/elak24aid-create/TruthLens`

3. **Configure the Web Service**
   Fill in the form with the following exact settings:
   - **Name:** `TruthLens-API`
   - **Region:** Choose the region closest to you (e.g., Oregon, Frankfurt).
   - **Branch:** `main`
   - **Root Directory:** `backend`
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

4. **Select Instance Type**
   - Choose the **Free** instance type ($0/month). No credit card or automatic billing is required.

5. **Configure Environment Variables**
   Expand the **Advanced** section and click **Add Environment Variable** for each of the following:

   - **Key:** `PYTHON_VERSION`
     - **Value:** `3.10.11` (or your preferred Python 3.10+ version to ensure compatibility)
   - **Key:** `GEMINI_MODEL`
     - **Value:** `gemini-3.5-flash-lite`

   *(Note: Do not add `GOOGLE_API_KEY` unless you want to optionally enable Gemini features. If you add it, mark it as a secret, but it is not required for the free-first baseline to run).*

6. **Health Check Path (Optional but Recommended)**
   - Still in the Advanced section, find **Health Check Path**.
   - Enter: `/api/health`

7. **Deploy**
   - Click the **Create Web Service** button at the bottom.
   - Render will begin building the application. You can monitor the progress in the logs.
   - Once it says "Live", your backend is publicly deployed!

8. **Verify Deployment**
   - Render will provide a public URL for your service (e.g., `https://truthlens-api-xxxx.onrender.com`).
   - Open that URL in your browser with the `/api/health` path appended (e.g., `https://truthlens-api-xxxx.onrender.com/api/health`) to ensure it responds with `{"status": "ok", ...}`.
