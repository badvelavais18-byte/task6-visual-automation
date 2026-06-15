# Task 6 — Visual Automation

Visual regression testing using **Selenium WebDriver** + **pixel-level screenshot comparison**.  
Every test calls `time.sleep()` to ensure browser renders are stable before capture.

---

## Project Structure

```
task6_visual_automation/
├── config.py               # Viewports, pages, sleep durations, diff thresholds
├── screenshot_manager.py   # WebDriver factory, navigate, resize, capture
├── visual_comparator.py    # NumPy pixel-diff engine + diff overlay image
├── report_generator.py     # Self-contained HTML report with inline images
├── run_tests.py            # CLI entry point (baseline | regression | both)
├── requirements.txt
└── tests/
    └── test_visual_regression.py   # All test classes
        ├── TestBaselineCapture     # Phase 1 — capture reference screenshots
        └── TestVisualRegression    # Phase 2 — compare actual vs baseline
```

**Screenshot output folders** (auto-created):

| Folder                      | Contents                              |
|-----------------------------|---------------------------------------|
| `screenshots/baselines/`    | Reference screenshots (source of truth) |
| `screenshots/actual/`       | Screenshots captured during regression run |
| `screenshots/diffs/`        | Red-overlay diff images for any failures |
| `reports/`                  | Generated HTML report                 |

---

## Setup

```bash
# 1. Clone / copy this folder
cd task6_visual_automation

# 2. Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Ensure Chrome is installed (or Firefox — see config.py → BROWSER)
#    Selenium Manager handles the driver binary automatically.
```

---

## Usage

### Step 1 — Capture Baselines (run once)
```bash
python run_tests.py --mode baseline
```
Baselines are saved to `screenshots/baselines/`.  
Re-run after intentional, approved UI changes to update the reference set.

### Step 2 — Run Regression Tests
```bash
python run_tests.py --mode regression
```
Compares fresh captures against baselines.  
Generates `reports/visual_report.html` automatically.

### Full Pipeline (baseline + regression + report)
```bash
python run_tests.py
```

### Skip HTML report
```bash
python run_tests.py --mode regression --no-report
```

### Exit Codes (CI / CD integration)
| Code | Meaning              | Merge gate         |
|------|----------------------|--------------------|
| `0`  | All checks passed    | ✅ Merge approved  |
| `1`  | One or more failed   | ❌ Merge blocked   |

---

## Viewports Tested

| Label            | Width  | Height | Device              |
|------------------|--------|--------|---------------------|
| `mobile_375`     | 375 px | 667 px | iPhone SE / 13 mini |
| `mobile_414`     | 414 px | 896 px | iPhone XR / 11      |
| `tablet_768`     | 768 px | 1024 px| iPad portrait        |
| `laptop_1280`    | 1280 px| 800 px | Standard laptop      |
| `desktop_1920`   | 1920 px| 1080 px| Full HD desktop      |

---

## Pages Tested

| ID       | URL                                              |
|----------|--------------------------------------------------|
| `home`   | `https://demo.opencart.com/`                     |
| `search` | Search results for "camera"                      |
| `login`  | Account login page                               |

Change these in `config.py → PAGES`.

---

## sleep() Strategy

`time.sleep()` is called at **every significant step** of every test to prevent
flaky results caused by page-load timing, CSS transitions, or lazy-loading:

| Sleep key           | When it fires                                | Default |
|---------------------|----------------------------------------------|---------|
| `startup`           | Before browser launch                        | 2.0 s   |
| `page_load`         | After `driver.get(url)`                      | 2.5 s   |
| `after_resize`      | After `set_window_size()`                    | 1.0 s   |
| `after_scroll`      | After `window.scrollTo()`                    | 0.5 s   |
| `after_capture`     | After `save_screenshot()`                    | 1.0 s   |
| `after_compare`     | After pixel-diff computation                 | 0.5 s   |
| `between_tests`     | `setUp()` / `tearDown()` gap                 | 2.0 s   |
| `suite_teardown`    | After `tearDownClass()`                       | 2.0 s   |

Tune all values centrally in `config.py → SLEEP`.

---

## Visual Diff Algorithm

1. Load `baseline.png` and `actual.png` as RGB NumPy arrays.
2. Compute absolute per-channel difference: `|baseline − actual|`.
3. Flag pixels where the max channel delta exceeds `PIXEL_DIFF_SENSITIVITY` (default 10/255).
4. Calculate `diff_pct = changed_pixels / total_pixels × 100`.
5. **Pass** if `diff_pct ≤ DIFF_THRESHOLD_PCT` (default **5 %**).
6. Save a red-overlay diff image to `screenshots/diffs/`.

Tune thresholds in `config.py`:
```python
PIXEL_DIFF_SENSITIVITY = 10    # raise to ignore minor anti-aliasing
DIFF_THRESHOLD_PCT     = 5.0   # raise to tolerate more dynamic content
```

---

## HTML Report

`reports/visual_report.html` is **self-contained** (images embedded as base64).  
Open it in any browser — no server required.

**Columns:** Page · Viewport · Status · Pixel Diff bar · Baseline · Actual · Diff Overlay

**Header banner:** `✅ MERGE APPROVED` or `❌ MERGE BLOCKED`

---

## Customisation

| What to change             | Where                    |
|----------------------------|--------------------------|
| Target URLs / page IDs     | `config.py → PAGES`      |
| Viewport breakpoints       | `config.py → VIEWPORTS`  |
| Diff tolerance             | `config.py → DIFF_THRESHOLD_PCT` |
| Sleep durations            | `config.py → SLEEP`      |
| Browser (Chrome / Firefox) | `config.py → BROWSER`    |
| Headless mode              | `config.py → HEADLESS`   |

---

## Learning Outcomes (Task 6)

- ✅ Visual testing strategy — baseline capture + pixel-level regression
- ✅ Screenshot comparison — NumPy diff + Pillow overlay images
- ✅ Responsive / cross-breakpoint checks — 5 device viewports per page
- ✅ Merge gate — CI exit code 1 blocks the PR on any visual failure
- ✅ `time.sleep()` used at every browser action for stable captures
