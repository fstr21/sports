@echo off
echo 🚀 Setting up Sports HTTP Server + ngrok
echo.

echo Step 1: Setting environment variables...
set SPORTS_API_KEY=sports-api-key-12345-replace-with-your-own-secure-key
set SERVER_HOST=0.0.0.0
set SERVER_PORT=8000

echo ✅ Environment variables set
echo.

echo Step 2: Install Python packages...
pip install fastapi uvicorn httpx pydantic python-multipart python-dotenv

echo.
echo Step 3: Test setup...
python setup_http_server.py

echo.
echo 🎉 Setup complete!
echo.
echo Next steps:
echo 1. Start server: python sports_http_server.py
echo 2. In another terminal: ngrok http 8000
echo 3. Use the ngrok URL from any remote machine!
pause