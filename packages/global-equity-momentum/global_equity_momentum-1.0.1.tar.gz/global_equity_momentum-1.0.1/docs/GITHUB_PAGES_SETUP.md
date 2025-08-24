# GitHub Pages Setup

This repository is configured to automatically deploy analysis results to GitHub Pages.

## What it does

The workflow (`/.github/workflows/analysis.yml`) automatically:

1. Runs monthly momentum analysis on the 1st day of each month
2. Generates a PNG chart
3. Creates a beautiful HTML report
4. Deploys everything to GitHub Pages

## Setup Requirements

To enable this functionality, you need to:

### 1. Enable GitHub Pages in Repository Settings

1. Go to your repository on GitHub
2. Click on **Settings** tab
3. Scroll down to **Pages** section in the left sidebar
4. Under **Source**, select **GitHub Actions**
5. Click **Save**

### 2. Repository Permissions

The workflow requires these permissions:

- `contents: write` - to commit results
- `pages: write` - to deploy to GitHub Pages
- `id-token: write` - for authentication

These are already configured in the workflow file.

### 3. Environment Setup

The workflow uses a `github-pages` environment which should be automatically created when you enable GitHub Pages.

## How it works

1. **Schedule**: Runs automatically on the 1st day of every month at 6:00 AM UTC
2. **Manual Trigger**: You can also run it manually from the Actions tab
3. **Output**: Creates an `output/` directory with:
   - `monthly_momentum_analysis.png` - the analysis chart
   - `index.html` - a beautiful web page displaying the chart
4. **Deployment**: Automatically deploys to GitHub Pages

## Accessing Results

Once deployed, your analysis will be available at:
`https://[your-username].github.io/[repository-name]/`

## Customization

You can modify the HTML template in the workflow file to:

- Change the styling
- Add more information
- Include additional charts or data
- Customize the layout

## Troubleshooting

If the workflow fails:

1. Check the Actions tab for error details
2. Ensure GitHub Pages is enabled
3. Verify repository permissions
4. Check if the `output/` directory is being created properly
