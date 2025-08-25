# ChartBot Pro — Refined (One-File EXE, English OCR)

Simple desktop app that reads **stock chart images** and suggests:
- Bias (long / short / neutral from on-chart words)
- Entry / Take Profit / Stop Loss (heuristics from OCR numbers)

> Educational only. Not financial advice.

## Run immediately (after CI build)
- Download the **ChartBot.exe** from your repo **Releases**.

## GitHub build (recommended, zero setup)
1. Create a repo and push these files.
2. Go to **Actions** → enable.
3. The workflow downloads portable Tesseract (ENG), bundles it, and publishes **one-file `ChartBot.exe`** to **Releases**.

## Local build (optional)
1. Place **portable Tesseract** at:
   - `tess/tesseract.exe`
   - `tess/tessdata/eng.traineddata`
   (CI does this automatically; locally you can copy from a Tesseract install.)
2. Double-click `auto_build.bat` → `dist/ChartBot.exe`

## Dev run (from source)
```bash
pip install -r requirements.txt
python chartbot.py
```
