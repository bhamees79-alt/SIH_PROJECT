
# HAR SYSTEM ISRO — Person 5 Prototype v2

A presentation-ready Streamlit dashboard for SIH26174.

## What this version represents

- The 117 videos are treated as **model-development recordings**, not as 117 selectable experiments.
- The operator-facing **Experiment Library** contains a prototype-ready Seed Handling Experiment plus clearly marked future modules.
- Seed Handling uses the six canonical activities:
  1. Retrieve cotton
  2. Place / arrange cotton
  3. Take seeds
  4. Place seeds on cotton
  5. Retrieve / use dropper
  6. Add water
- P2 is represented using the verified 32 x 206 feature contract.
- The exact P3 temporal model is intentionally **not fabricated or guessed**.
- `hgb_spatial_best.joblib` is not bundled/connected because it expects 320 features and has not been confirmed as the P3 temporal model.
- Person 4 validation is shown as pending.

## Run

```powershell
cd HAR_SYSTEM_ISRO
pip install -r requirements.txt
streamlit run app.py
```

Open the local URL shown by Streamlit, normally:
`http://localhost:8501`

## Camera

The Live HAR page includes Streamlit's built-in camera capture. It receives a real camera frame from the browser.

This is intentionally a camera-capture prototype rather than a continuous WebRTC stream. Once the actual P2/P3 inference code is confirmed, a continuous live pipeline can be added.

## Important

This dashboard does not pretend that P3 inference is live before the final P3 artifact is confirmed.
