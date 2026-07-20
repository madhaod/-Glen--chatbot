# 🎯 STEP-BY-STEP SETUP GUIDE

## Your Computer, No Experience Needed!

This guide will walk you through EVERY SINGLE STEP.

---

## 🎬 BEFORE YOU START

Make sure you have:
- ✅ Downloaded all the files
- ✅ Internet connection
- ✅ Twilio account created (https://www.twilio.com - free)
- ✅ Your Twilio credentials ready (Account SID, Auth Token, WhatsApp Number)

**Don't have Twilio yet?** Go create free account at https://www.twilio.com

---

## 📍 PART 1: Choose Your Operating System

### Are you on Windows, Mac, or Linux?

---

## 🪟 WINDOWS USERS - START HERE

### Step 1: Make Folder for Project

1. Open File Explorer
2. Create new folder: `C:\opd-chatbot` or anywhere you want
3. Download all files into this folder

Your folder should look like:
```
C:\opd-chatbot\
  ├── INSTALL_WINDOWS.bat
  ├── RUN_APP.bat
  ├── app.py
  ├── requirements.txt
  ├── .env.example
  └── ... other files
```

### Step 2: Run Installation (Automatic)

1. **Find:** `INSTALL_WINDOWS.bat` file in your folder
2. **Double-click** it
3. A black command window will open
4. **Wait** 5-10 minutes
5. Watch messages appear - don't close window!
6. When done, you'll see: `✅ SETUP COMPLETE!`
7. Read the next steps shown in the window
8. Press any key to close

✅ **Installation Done!**

### Step 3: Edit Configuration File (.env)

1. In your folder, find: `.env` file
2. Right-click on it
3. Select: "Open with" → "Notepad"
4. You'll see something like:
```
TWILIO_ACCOUNT_SID=your_account_sid_here
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155552671
DATABASE_URL=sqlite:///appointments.db
```

5. Replace the values with YOUR credentials:
   - Get **TWILIO_ACCOUNT_SID** from: https://console.twilio.com (login)
   - Get **TWILIO_AUTH_TOKEN** from: https://console.twilio.com (login)
   - Get **TWILIO_WHATSAPP_NUMBER** from: https://console.twilio.com > Messaging > Services > WhatsApp

Example after editing:
```
TWILIO_ACCOUNT_SID=AC1234567890abcdef1234567890ab
TWILIO_AUTH_TOKEN=abcdef1234567890abcdef1234567890
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155552671
DATABASE_URL=sqlite:///appointments.db
```

6. **Save** (Ctrl+S or File → Save)
7. Close Notepad

✅ **Configuration Done!**

### Step 4: Start Your Chatbot

1. Find: `RUN_APP.bat` in your folder
2. Double-click it
3. A black window will open showing:
```
Starting WhatsApp OPD Chatbot...

===================================================
   🚀 Starting Chatbot Server
===================================================

The app will run on: http://localhost:5000
Dashboard: http://localhost:5000/dashboard

Press Ctrl+C to stop the server

===================================================

 * Serving Flask app 'app'
 * Running on http://127.0.0.1:5000
```

✅ **Your app is RUNNING!**

### Step 5: Test Dashboard

1. Open your web browser (Chrome, Edge, Firefox)
2. Go to: `http://localhost:5000/dashboard`
3. You should see a beautiful dashboard!

✅ **Dashboard Works!**

### Step 6: Expose to Internet (Ngrok)

Your app is running locally, but WhatsApp needs to reach it from internet.

**Download Ngrok:**
1. Go: https://ngrok.com/download
2. Download for Windows
3. Extract it (unzip)
4. Remember where you extracted it

**Run Ngrok:**
1. Open a NEW Command Prompt (leave the chatbot running!)
2. Go to where you extracted ngrok:
   ```cmd
   cd C:\path\where\you\extracted\ngrok
   ```
3. Run:
   ```cmd
   ngrok http 5000
   ```
4. You'll see output like:
```
Session Status                online
Account                       Free
Forwarding                    https://xxxx-xxxx-xxxx-xxxx.ngrok.io -> http://localhost:5000
```

**Copy the URL:** `https://xxxx-xxxx-xxxx-xxxx.ngrok.io`

✅ **Ngrok Running!**

### Step 7: Configure Twilio Webhook

1. Go to: https://console.twilio.com/
2. Login
3. Navigate: **Messaging** → **Services** → **WhatsApp**
4. Find your WhatsApp service
5. Click: **Integration**
6. Find: **Webhook URL** field
7. Paste your ngrok URL with `/webhook`:
   ```
   https://xxxx-xxxx-xxxx-xxxx.ngrok.io/webhook
   ```
8. Click **Save**

✅ **Webhook Configured!**

### Step 8: Test Your Chatbot

1. Get your Twilio WhatsApp number from Twilio Console
2. Open WhatsApp on your phone
3. Send message to your Twilio number: "Hi"
4. Your bot should respond: "👋 Welcome to OPD..."
5. Follow the booking flow!

✅ **Chatbot Works!**

### Step 9: Check Dashboard

1. Go to: `http://localhost:5000/dashboard`
2. You should see your appointment!

✅ **Everything Works!**

---

## 🍎 MAC USERS - START HERE

### Step 1: Create Project Folder

1. Open Finder
2. Create folder: `opd-chatbot` in your home directory
3. Download all files into this folder

### Step 2: Run Installation (Automatic)

1. Open Terminal (Applications → Utilities → Terminal)
2. Navigate to your folder:
   ```bash
   cd ~/opd-chatbot
   ```
3. Make installation script executable:
   ```bash
   chmod +x INSTALL_MAC_LINUX.sh
   ```
4. Run installation:
   ```bash
   ./INSTALL_MAC_LINUX.sh
   ```
5. **Wait** 5-10 minutes
6. When done, you'll see: `✅ SETUP COMPLETE!`

✅ **Installation Done!**

### Step 3: Edit Configuration File (.env)

1. Open Terminal
2. Go to your folder:
   ```bash
   cd ~/opd-chatbot
   ```
3. Open .env in editor:
   ```bash
   nano .env
   ```
4. Edit the credentials (use arrow keys to move, type to edit)
5. When done: Press **Ctrl+X**, then **Y**, then **Enter**

✅ **Configuration Done!**

### Step 4: Start Your Chatbot

1. Open Terminal
2. Go to folder:
   ```bash
   cd ~/opd-chatbot
   ```
3. Run app:
   ```bash
   ./RUN_APP.sh
   ```
   Or:
   ```bash
   python3 app.py
   ```
4. You'll see: `Running on http://127.0.0.1:5000`

✅ **Your app is RUNNING!**

### Step 5-9: Follow Windows Steps 5-9 Above

The process is the same for Mac. Just use Terminal instead of Command Prompt.

---

## 🐧 LINUX USERS - START HERE

Same as Mac! Follow the Mac steps above.

---

## ✅ FINAL CHECKLIST

Before declaring success:

- ✅ Installation script ran without errors
- ✅ .env file created and edited
- ✅ App starts with `python app.py`
- ✅ Dashboard loads at `http://localhost:5000/dashboard`
- ✅ Ngrok running (shows Forwarding URL)
- ✅ Twilio webhook configured correctly
- ✅ Can send WhatsApp message to bot
- ✅ Bot responds with greeting
- ✅ Can complete appointment booking flow
- ✅ Appointment appears in dashboard

**All checked?** 🎉 **YOU'RE DONE!**

---

## 🆘 SOMETHING WENT WRONG?

### Installation script failed
**Solution:** 
- Make sure Python 3.8+ is installed
- On Mac: `brew install python3`
- On Linux: `sudo apt-get install python3 python3-venv`
- Run script again

### Can't find .env file
**Solution:**
- .env is a hidden file on Mac/Linux
- Show hidden files: Cmd+Shift+. (Mac) or Ctrl+H (Linux)
- Or open terminal and use: `nano .env`

### App won't start
**Solution:**
- Did you edit .env with credentials?
- Is port 5000 available? (no other app using it)
- Try: `python app.py --port 5001`

### Webhook not working
**Solution:**
- Make sure ngrok is still running
- Check webhook URL is copied exactly right
- Ngrok URL changes when restarted - update Twilio

### WhatsApp doesn't respond
**Solution:**
- Make sure Twilio credentials in .env are correct
- Check webhook URL in Twilio console
- Look at terminal window - you'll see errors
- Make sure app.py is still running

---

## 🚀 NEXT: Deploy to Cloud

Once everything works locally, deploy to a free cloud server!

See: **QUICKSTART.md** for deployment options

---

## 📞 NEED MORE HELP?

- **Installation issues:** See HOW_TO_INSTALL.md
- **Twilio setup:** https://www.twilio.com/docs/whatsapp
- **Deployment:** QUICKSTART.md
- **Features:** README.md

---

## 🎉 YOU DID IT!

You've successfully set up your WhatsApp OPD appointment chatbot!

**Now:**
1. Share your WhatsApp number with clinic
2. Patients can book appointments via WhatsApp
3. Check dashboard to manage appointments
4. Deploy to cloud for 24/7 uptime

---

**Questions? No problem - guides above have detailed explanations!**

**Happy Chatting! 🤖**
