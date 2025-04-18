# Deployment Guide for WhatsApp Chat Analyzer

This guide provides instructions for deploying the WhatsApp Chat Analyzer web app to Render, a cost-effective hosting platform with a generous free tier.

## Option 1: Deploy to Render (Recommended)

### Prerequisites
- A GitHub account
- Your code pushed to a GitHub repository

### Steps

1. **Sign up for Render**
   - Go to [render.com](https://render.com) and create an account
   - Connect your GitHub account

2. **Create a new Web Service**
   - Click "New" and select "Web Service"
   - Connect your GitHub repository
   - Select the repository containing this code
   - Configure the service:
     - Name: `whatsapp-analyzer` (or your preferred name)
     - Environment: `Python`
     - Build Command: `pip install -r web_app/requirements.txt`
     - Start Command: `cd web_app && python main.py`
     - Select the free plan

3. **Deploy**
   - Click "Create Web Service"
   - Render will automatically deploy your application
   - Once deployed, you'll receive a URL where your app is accessible

## Option 2: Deploy to Railway

1. Sign up at [railway.app](https://railway.app)
2. Create a new project and connect your GitHub repository
3. Add a `Procfile` to your web_app directory with the following content:
   ```
   web: cd web_app && python main.py
   ```
4. Deploy your application

## Option 3: Deploy to Fly.io

1. Install the Fly CLI: `curl -L https://fly.io/install.sh | sh`
2. Create a `Dockerfile` in your web_app directory
3. Run `fly launch` and follow the prompts
4. Deploy with `fly deploy`

## Maintenance

- The free tier of Render includes 750 hours of runtime per month
- Your app will automatically sleep after inactivity to conserve resources
- The first request after inactivity may take a few seconds to wake up the service 