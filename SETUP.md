# GitHub Setup Instructions

## Step 1: Create GitHub Repository

1. Go to: https://github.com/new
2. Repository name: `fhir-healthcare-data-pipeline`
3. Description: `FHIR Healthcare Data Pipeline - Medallion Architecture with SCD2`
4. Visibility: **Public** (or Private if you prefer)
5. ✅ Initialize with README (will be replaced)
6. Click **Create repository**

## Step 2: Download This Folder from Databricks

The folder `fhir-healthcare-data-pipeline` is ready at:
```
/Workspace/Users/madasvenkatasivagoud@gmail.com/fhir-healthcare-data-pipeline/
```

### Option A: Download via Databricks UI
1. Navigate to Workspace → Users → madasvenkatasivagoud@gmail.com
2. Right-click `fhir-healthcare-data-pipeline` folder
3. Select "Export" → Download as folder

### Option B: Download via Databricks CLI
```bash
# Install Databricks CLI
pip install databricks-cli

# Configure authentication
databricks configure --token

# Download the folder
databricks workspace export_dir \
  /Users/madasvenkatasivagoud@gmail.com/fhir-healthcare-data-pipeline \
  ./fhir-healthcare-data-pipeline
```

## Step 3: Push to GitHub

### Using Git Command Line

```bash
# Clone your new repository
git clone https://github.com/madasvenkatasiva/fhir-healthcare-data-pipeline.git
cd fhir-healthcare-data-pipeline

# Copy exported files (adjust path as needed)
cp -r /path/to/downloaded/fhir-healthcare-data-pipeline/* .

# Add all files
git add .

# Commit
git commit -m "Initial commit: Complete FHIR data pipeline with Medallion architecture"

# Push to GitHub
git push origin main
```

### Using GitHub Desktop

1. Open GitHub Desktop
2. File → Clone Repository → `madasvenkatasiva/fhir-healthcare-data-pipeline`
3. Copy all files from downloaded folder to the cloned repository folder
4. GitHub Desktop will show all changes
5. Write commit message: "Initial commit: Complete FHIR data pipeline"
6. Click "Commit to main"
7. Click "Push origin"

## Step 4: Verify on GitHub

1. Go to: https://github.com/madasvenkatasiva/fhir-healthcare-data-pipeline
2. Verify all files are present:
   - README.md with badges and architecture
   - notebooks/ folder with 5 .ipynb files
   - docs/ folder with 3 .md files
   - .gitignore

## Step 5: Add Repository Topics (Optional)

On GitHub, add these topics to make your repo discoverable:
- `databricks`
- `fhir`
- `healthcare`
- `data-engineering`
- `medallion-architecture`
- `delta-lake`
- `pyspark`
- `etl-pipeline`

Go to repository → About (gear icon) → Topics

## Troubleshooting

### Issue: Git not installed
```bash
# macOS
brew install git

# Windows
winget install Git.Git

# Linux
sudo apt-get install git
```

### Issue: Authentication failed
Use Personal Access Token (PAT):
1. GitHub → Settings → Developer settings → Personal access tokens
2. Generate token with 'repo' scope
3. Use token as password when pushing

### Issue: Large files warning
The .gitignore is already configured to exclude large data files (.parquet, .delta, .csv, .json).
If you still get warnings, use Git LFS:
```bash
git lfs install
git lfs track "*.parquet"
git add .gitattributes
```

## Next Steps After Push

1. ✅ Add project to your resume/portfolio
2. ✅ Share repository URL with recruiters
3. ✅ Write a LinkedIn post about your project
4. ✅ Add to GitHub profile README
5. ✅ Enable GitHub Pages (Settings → Pages) to host docs

## Your Repository URL

🔗 https://github.com/madasvenkatasiva/fhir-healthcare-data-pipeline

---

Generated on: 2026-05-25 18:01:44