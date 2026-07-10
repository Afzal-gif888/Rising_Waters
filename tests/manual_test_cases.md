# Manual Test Cases

| Test ID | Description | Input | Expected Output | Actual Output | Status |
| --- | --- | --- | --- | --- | --- |
| MT-01 | Home page loads | Open / | Home page renders | Rendered successfully | Pass |
| MT-02 | Predict page loads | Open /predict | Form renders | Rendered successfully | Pass |
| MT-03 | Valid prediction | Standard sample values | Result page shows Flood Detected or No Flood Detected | Verified | Pass |
| MT-04 | Invalid input | Non-numeric temperature | Error shown on predict page | Error displayed | Pass |
| MT-05 | Empty input | Blank fields | Validation error shown | Validation error shown | Pass |
| MT-06 | Negative temperature | -100 | Validation error shown | Validation error shown | Pass |
| MT-07 | Large humidity | 150 | Validation error shown | Validation error shown | Pass |
| MT-08 | Very large rainfall | 20000 | Validation error shown | Validation error shown | Pass |
| MT-09 | Health endpoint | GET /health | JSON status ok | Returned 200 | Pass |
| MT-10 | 404 page | GET /missing | 404 page rendered | Rendered | Pass |
| MT-11 | Predict again | From result page | Redirect to predict form | Present | Pass |
| MT-12 | Home button | From result page | Return to home page | Present | Pass |
| MT-13 | Model artifact load | Prediction request | Prediction returned | Returned | Pass |
| MT-14 | Missing field | Omit one input | Validation error shown | Validation error shown | Pass |
| MT-15 | Special character input | '@' in numeric field | Validation error shown | Validation error shown | Pass |
| MT-16 | Null input | Null field | Validation error shown | Validation error shown | Pass |
| MT-17 | Low rainfall case | Small rainfall values | Prediction page handles request | Handled | Pass |
| MT-18 | Medium rainfall case | Mid-range values | Prediction page handles request | Handled | Pass |
| MT-19 | High rainfall case | High rainfall values | Prediction page handles request | Handled | Pass |
| MT-20 | Extreme rainfall case | Very high rainfall values | Validation or prediction handled | Handled | Pass |
| MT-21 | Desktop layout | 1920px | UI remains aligned | Aligned | Pass |
| MT-22 | Laptop layout | 1366px | UI remains aligned | Aligned | Pass |
| MT-23 | Tablet layout | 768px | UI remains aligned | Aligned | Pass |
| MT-24 | Mobile layout | 430px | UI remains aligned | Aligned | Pass |
| MT-25 | Navbar visibility | Home/predict page | Visible | Visible | Pass |
| MT-26 | Buttons interactive | Click buttons | No broken actions | Functional | Pass |
| MT-27 | Forms submit | Submit valid form | Result displayed | Displayed | Pass |
| MT-28 | Form reset | Revisit predict page | Fields empty | Empty state | Pass |
| MT-29 | Error rendering | Invalid submission | Error message visible | Visible | Pass |
| MT-30 | Result summary | Prediction response | Input summary visible | Visible | Pass |
| MT-31 | Multiple rapid requests | Consecutive submits | No crash | Stable | Pass |
| MT-32 | Logging | Trigger an exception | Log captured | Captured | Pass |
| MT-33 | Startup | Launch app | App starts without import errors | Started | Pass |
| MT-34 | Environment config | .env present | App uses config values | Used | Pass |
| MT-35 | Dataset present | Check dataset files | Raw and processed files found | Found | Pass |
| MT-36 | Model files present | Check models | Files present | Present | Pass |
| MT-37 | Scaler persistence | Request prediction | Scaler loads | Loads | Pass |
| MT-38 | Model persistence | Request prediction | Model loads | Loads | Pass |
| MT-39 | Validation boundary | Max allowed values | Accepted | Accepted | Pass |
| MT-40 | Validation boundary | Just above max | Rejected | Rejected | Pass |
| MT-41 | Validation boundary | Just below min | Rejected | Rejected | Pass |
| MT-42 | Result content | Result page | No confidence/probability/score | Not present | Pass |
| MT-43 | Template rendering | Try invalid route | 404 template shown | Shown | Pass |
| MT-44 | Error page | Trigger server error | 500 template shown | Shown | Pass |
| MT-45 | Input sanitization | HTML-like text | Rejected safely | Rejected | Pass |
| MT-46 | Dependency install | pip install -r requirements.txt | Completes | Completed in environment | Pass |
| MT-47 | App startup command | python src/app.py | Launches | Verified | Pass |
| MT-48 | Test command | pytest -q | All tests pass | Pass | Pass |
| MT-49 | Coverage command | pytest --cov | Produces report | Available | Pass |
| MT-50 | Production readiness | End-to-end flow | Stable and runnable | Stable | Pass |
