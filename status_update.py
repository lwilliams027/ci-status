"""Read the AI batch job's state and push a status.json to the GitHub Pages status site."""
import json, subprocess, pathlib, datetime

AI = pathlib.Path(r"C:\Users\adapt\OneDrive\Desktop\combo-intelligence-ai")
HERE = pathlib.Path(__file__).parent


def build():
    log = ""
    p = AI / "batch_log.txt"
    if p.exists():
        log = p.read_text(errors="ignore")
    cut = log.count("added cropped labeled clips") or log.count("added")
    done = "BATCH_DONE" in log
    result = None
    rp = AI / "batch_result.json"
    if rp.exists():
        try:
            result = json.loads(rp.read_text())
        except Exception:
            pass
    if done and result:
        phase = "✅ Done"
        detail = "All 10 matches processed, model retrained, benchmark re-measured."
    elif cut >= 10 or "retrain" in log.lower():
        phase = "Retraining model"
        detail = "All 10 matches cut & cropped — now retraining and re-measuring the benchmark."
    else:
        phase = "Processing matches"
        detail = f"Cutting & detector-cropping match {min(cut+1,10)} of 10."
    return {
        "updated": datetime.datetime.utcnow().strftime("%H:%M UTC, %b %d"),
        "phase": phase, "detail": detail, "matches_cut": cut,
        "done": done, "result": result,
    }


def main():
    (HERE / "status.json").write_text(json.dumps(build(), indent=2))
    subprocess.run(["git", "-C", str(HERE), "add", "status.json"], capture_output=True)
    subprocess.run(["git", "-C", str(HERE), "commit", "-m", "update status"], capture_output=True)
    subprocess.run(["git", "-C", str(HERE), "push", "-q", "origin", "main"], capture_output=True)


if __name__ == "__main__":
    main()
