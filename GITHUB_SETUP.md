# GitHub Repository Setup Guide

This guide will help you set up your GitHub repository with the same colorful Nicepage-style theme used in your video downloader application.

## 📁 Files Included for GitHub

### Essential GitHub Files:
- `_config.yml` - Jekyll configuration with Cayman theme
- `docs/index.md` - Main documentation page with colorful styling
- `docs/_layouts/default.html` - Custom layout with Nicepage colors
- `docs/assets/css/custom.css` - Enhanced CSS with your color scheme
- `.github/workflows/deploy.yml` - GitHub Actions for deployment

## 🚀 How to Set Up Your GitHub Repository

### Step 1: Create Repository
1. Go to GitHub and create a new repository
2. Name it `video-downloader` (or your preferred name)
3. Make it public for GitHub Pages to work

### Step 2: Upload Files
1. Upload all files from the `video-downloader-package` folder
2. Make sure the `docs/` folder and `_config.yml` are in the root

### Step 3: Enable GitHub Pages
1. Go to your repository **Settings**
2. Scroll down to **Pages** section
3. Under **Source**, select "Deploy from a branch"
4. Choose **main** branch and **/ (root)** folder
5. Click **Save**

### Step 4: Customize Your Theme
Edit these files to match your project:

**In `_config.yml`:**
```yaml
title: Your Project Name
description: Your project description
url: "https://yourusername.github.io"
baseurl: "/your-repository-name"
github_username: yourusername
```

**In `docs/index.md`:**
- Replace "yourusername" with your GitHub username
- Update repository URLs
- Add your own screenshots and content

### Step 5: Theme Features

Your GitHub repository will have:

✨ **Colorful Header**
- Blue-to-red gradient background
- Wave pattern overlay
- Professional download buttons

🎨 **Nicepage-Style Design**
- Same blue (#478ac9), red (#db545a), yellow (#f1c50e) colors
- Animated feature cards
- Platform badges with hover effects

📱 **Mobile Responsive**
- Works perfectly on all devices
- Adaptive layout and buttons

🚀 **GitHub Integration**
- Automatic deployment with GitHub Actions
- SEO optimization with Jekyll plugins
- Professional documentation layout

## 🎯 Color Scheme Used

```css
:root {
    --primary-color: #478ac9;    /* Blue */
    --secondary-color: #db545a;  /* Red */
    --accent-color: #f1c50e;     /* Yellow */
    --dark-color: #292d33;       /* Dark gray */
}
```

## 📸 Adding Screenshots

1. Create `docs/assets/` folder
2. Add your app screenshots
3. Reference them in `docs/index.md`:
   ```markdown
   ![Screenshot](assets/screenshot.png)
   ```

## 🔧 Advanced Customization

### Adding More Pages
Create new `.md` files in `docs/` folder:
```
docs/
├── index.md          # Home page
├── installation.md   # Installation guide
├── features.md       # Features page
└── support.md        # Support page
```

### Custom CSS
Edit `docs/assets/css/custom.css` to:
- Change colors
- Add animations
- Modify layout
- Add custom components

### GitHub Actions
The included workflow automatically:
- Builds your site when you push changes
- Deploys to GitHub Pages
- Handles dependencies

## 📋 Checklist

- [ ] Repository created and files uploaded
- [ ] GitHub Pages enabled in Settings
- [ ] `_config.yml` customized with your info
- [ ] `docs/index.md` updated with your content
- [ ] Screenshots added to `docs/assets/`
- [ ] Repository URL updated in documentation
- [ ] Theme colors and styling verified

## 🌐 Result

Your GitHub repository will have:
- Professional landing page with your app's colors
- Download buttons and GitHub integration
- Mobile-responsive design
- SEO optimization
- Automatic deployment

Visit your site at: `https://yourusername.github.io/repository-name`

## 🆘 Troubleshooting

**Pages not loading?**
- Check if GitHub Pages is enabled
- Verify `_config.yml` syntax
- Ensure `docs/index.md` exists

**Theme not applying?**
- Check file paths in `_config.yml`
- Verify CSS files are in correct location
- Clear browser cache

**Colors not showing?**
- Check `docs/_layouts/default.html`
- Verify CSS variables are defined
- Inspect browser console for errors