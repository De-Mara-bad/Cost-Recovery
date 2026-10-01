# 🚀 Deploy to GitHub + Streamlit Cloud

This guide shows you how to put the app online so you can access it from anywhere—no installation needed.

---

## Step 1: Create a GitHub Repository

1. Go to **https://github.com/new**
2. Create a new repository:
   - **Repository name:** `fluent-reconciliation` (or whatever you want)
   - **Description:** Fluent Cost Recovery Reconciliation App
   - **Public** or **Private** (up to you)
   - Click **Create repository**

---

## Step 2: Upload Files to GitHub

After creating the repo, GitHub will show you options. Choose **"uploading an existing file"**:

1. You'll see an **"Add file"** button → click **"Upload files"**
2. Drag and drop (or select) these files:
   - `fluent_reconciliation_app.py`
   - `requirements.txt`
   - `README.md`

3. At the bottom, click **"Commit changes"**

**Done!** Your code is now on GitHub.

---

## Step 3: Deploy to Streamlit Cloud (Free)

1. Go to **https://streamlit.io/cloud**
2. Click **"Sign up"** or **"Sign in"** with your GitHub account
3. Once signed in, click **"New app"** (top right)
4. Fill in:
   - **Repository:** Select the `fluent-reconciliation` repo you just created
   - **Branch:** `main`
   - **Main file path:** `fluent_reconciliation_app.py`
5. Click **"Deploy"**

**Wait 1-2 minutes** while Streamlit builds and deploys your app.

---

## You're Done! 🎉

Once deployed, you'll get a URL like:
```
https://fluent-reconciliation-xxxxx.streamlit.app
```

**Bookmark this URL** and you can access your app from anywhere, anytime.

---

## Using Your Online App

1. Open your Streamlit URL in your browser
2. Upload Account Transactions and Sales files
3. Configure triggers (if needed)
4. Download your Excel results

No installation, no Python knowledge needed—anyone can use it.

---

## Making Updates

If you want to change the app later:

1. Edit `fluent_reconciliation_app.py` on GitHub (click the pencil icon)
2. Make your changes
3. Commit the changes
4. **Streamlit automatically redeploys!** (within 1-2 minutes)

---

## Sharing with Your Team

Just share the URL:
- Give Ludwig, Craig, and anyone else the link
- They open it in their browser
- They can use the app immediately

---

## Troubleshooting

**App not deploying?**
- Make sure all three files are uploaded: `fluent_reconciliation_app.py`, `requirements.txt`, `README.md`
- Check that file names are exactly right (case-sensitive)

**Need to update the triggers?**
- Edit the `fluent_reconciliation_app.py` file on GitHub
- Streamlit redeploys automatically

**Running slowly?**
- Streamlit Cloud free tier has limits
- If you need more power, paid plans are available at streamlit.io/pricing

---

## File Structure (What You Need)

```
fluent-reconciliation/
├── fluent_reconciliation_app.py    (the app)
├── requirements.txt                 (libraries it needs)
└── README.md                        (description)
```

That's it!

---

## Next Steps

1. Create the GitHub repo
2. Upload the 3 files
3. Deploy to Streamlit Cloud
4. Share the URL with your team
5. Start using it!

Questions? Follow Streamlit's guide: https://docs.streamlit.io/streamlit-cloud/get-started
