
import os
import tempfile
import subprocess
import gradio as gr

def create_video(photos, song, progress=gr.Progress()):
    if not photos:
        raise gr.Error("Banza ushyiremo nibura ifoto imwe.")
    if not song:
        raise gr.Error("Banza ushyiremo indirimbo.")

    output_dir = tempfile.mkdtemp()
    output = os.path.join(output_dir, "REBA_AI_VIDEO.mp4")
    photos = photos if isinstance(photos, list) else [photos]

    try:
        duration_result = subprocess.run(
            [
                "ffprobe", "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                song
            ],
            capture_output=True, text=True, check=True
        )
        duration = float(duration_result.stdout.strip())
    except Exception:
        raise gr.Error("REBA ntiyashoboye gusoma uburebure bw'indirimbo.")

    if duration <= 0:
        raise gr.Error("Indirimbo ntisomeka neza.")

    # Kora video y'igihe kingana n'indirimbo.
    photo_duration = duration / len(photos)
    filters = []
    inputs = []

    for photo in photos:
        inputs.extend(["-loop", "1", "-t", str(photo_duration),
                       "-i", photo])

    inputs.extend(["-i", song])

    for i in range(len(photos)):
        filters.append(
            f"[{i}:v]scale=1280:720:force_original_aspect_ratio=decrease,"
            f"pad=1280:720:(ow-iw)/2:(oh-ih)/2,"
            f"setsar=1,fps=25,format=yuv420p[v{i}]"
        )

    joined = "".join(f"[v{i}]" for i in range(len(photos)))
    filters.append(f"{joined}concat=n={len(photos)}:v=1:a=0[vout]")

    command = [
        "ffmpeg", "-y", *inputs,
        "-filter_complex", ";".join(filters),
        "-map", "[vout]", "-map", f"{len(photos)}:a",
        "-c:v", "libx264", "-preset", "ultrafast",
        "-c:a", "aac", "-b:a", "192k",
        "-t", str(duration), "-shortest",
        "-movflags", "+faststart", output
    ]

    result = subprocess.run(
        command, capture_output=True, text=True
    )

    if result.returncode != 0 or not os.path.exists(output):
        raise gr.Error(
            "Video ntiyakozwe. Reba niba Space ifite FFmpeg."
        )

    return output


with gr.Blocks(title="REBA AI VIDEO ENGINE") as demo:
    gr.Markdown(
        "# 🌖 REBA AI VIDEO ENGINE\n"
        "### Shyiramo amafoto n'indirimbo, ukore music video."
    )

    photos = gr.File(
        label="Amafoto — hitamo menshi",
        file_count="multiple",
        file_types=["image"],
        type="filepath"
    )

    song = gr.Audio(
        label="Indirimbo yawe",
        type="filepath",
        sources=["upload"]
    )

    create = gr.Button("KORA VIDEO", variant="primary")
    result = gr.Video(label="Video ya REBA")

    create.click(
        fn=create_video,
        inputs=[photos, song],
        outputs=[result]
    )

demo.launch()
