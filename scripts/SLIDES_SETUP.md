# Adding Trajectory Plots to Google Slides

This guide explains how to automatically add trajectory plots to your Google Slides presentation using the `add_plots_to_slides.py` script.

## Prerequisites

### 1. Install Required Python Packages

```bash
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

### 2. Set Up Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the following APIs:
   - Google Slides API
   - Google Drive API

To enable APIs:
- Click on "Enable APIs and Services"
- Search for "Google Slides API" and click "Enable"
- Search for "Google Drive API" and click "Enable"

### 3. Create OAuth 2.0 Credentials

1. In Google Cloud Console, go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. If prompted, configure the OAuth consent screen:
   - Choose "External" user type
   - Fill in required fields (app name, user support email, developer email)
   - Add scopes: `https://www.googleapis.com/auth/presentations` and `https://www.googleapis.com/auth/drive.file`
   - Add your email as a test user
4. Choose "Desktop app" as application type
5. Download the credentials JSON file
6. Rename it to `credentials.json` and place it in the project root directory

## Usage

### Run the Script

```bash
cd /Users/ivar/Desktop/current_projects/AI_projects/test_config_modular_llm
python scripts/add_plots_to_slides.py
```

### First Run

On the first run:
1. A browser window will open asking you to sign in to your Google account
2. Grant the requested permissions (read/write access to presentations and drive)
3. The script will save your credentials in `token.pickle` for future runs

### What the Script Does

The script will:
1. Find all trajectory plots for:
   - Task orders: `game_myth` and `myth_game`
   - All 6 myth topics
   - First 2 runs of each combination
2. Upload each plot to Google Drive (temporarily)
3. Add the plots to your presentation starting from slide 105
4. Add a title to each slide indicating the task order, topic, and run number

### Expected Output

The script will add 24 plots total:
- 6 topics × 2 task orders × 2 runs = 24 plots
- Slides 105-128 will contain the plots

Each slide will have:
- A title: "Task Order - Topic Name (Run N)"
- The trajectory plot image

## Troubleshooting

### "File credentials.json not found"
- Make sure you've downloaded the OAuth credentials from Google Cloud Console
- Rename the file to exactly `credentials.json`
- Place it in the project root directory

### "Access denied" or authentication errors
- Make sure you've added your email as a test user in the OAuth consent screen
- Delete `token.pickle` and try again

### "Slide doesn't exist"
- The presentation must have at least 128 slides (105 + 23 more)
- Add blank slides to your presentation if needed

### Permission errors on Google Drive
- The script uploads images to your Google Drive and shares them with "anyone with the link"
- Make sure your Google Drive has enough space for temporary image uploads

## Script Configuration

You can modify the script to change:

- **Starting slide**: Change `START_SLIDE` variable (default: 105)
- **Presentation ID**: Change `PRESENTATION_ID` if using a different presentation
- **Image size/position**: Modify the `size` and `transform` parameters in `add_image_to_slide()`
- **Plots to include**: Modify `TASK_ORDERS` or `MYTH_TOPICS` lists

## Notes

- The script will skip any plots that don't exist
- Images are uploaded to your personal Google Drive
- The process may take several minutes depending on the number of plots
- Each plot file is uploaded separately, so expect ~24 uploads
