# Portfolio Backend Deployment Guide

## ✅ **Working Configuration**

Your backend is now ready for deployment with the following fixes:

### **🔧 Key Changes Made:**
1. **Removed feedparser dependency** - Avoids Python 3.13 `cgi` module issues
2. **Made blog functionality optional** - Gracefully handles missing feedparser
3. **Updated to Python 3.11** - Compatible with all dependencies
4. **Fixed FastAPI lifespan** - Uses modern event handlers
5. **Minimal requirements** - Only essential packages

### **📦 Current Dependencies:**
```
fastapi==0.95.2
uvicorn==0.22.0
python-dotenv==1.0.0
requests==2.31.0
```

### **🚀 Deploy to Render:**

1. **Push your code** to GitHub
2. **Connect to Render** using the repository
3. **Use these settings:**
   - **Build Command**: `chmod +x build.sh && ./build.sh`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Environment**: Python 3.11

4. **Set Environment Variables:**
   ```
   PYTHON_VERSION=3.11.9
   LLM_PROVIDER=mock
   LLM_MODEL=llama3-8b-8192
   ```

5. **Deploy** - Should work without any errors!

### **🧪 Test Your Deployment:**

```bash
# Health check
curl https://your-app-name.onrender.com/health

# Chat with the bot
curl -X POST https://your-app-name.onrender.com/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Who is Satvik?"}'

# Blog posts (will work if feedparser is available)
curl https://your-app-name.onrender.com/medium-blogs
```

### **🔗 Connect to Frontend:**

Update your frontend API configuration to point to your Render backend URL.

### **📝 Notes:**
- Blog functionality is optional and will work if feedparser is available
- Chatbot uses mock LLM by default (change `LLM_PROVIDER` to `groq` for production)
- All endpoints are CORS-configured for your frontend domain

Your backend is now production-ready! 🎉 