import os
import json
import uuid
import subprocess
from django.conf import settings
from django.utils.dateparse import parse_datetime
from django.core.files import File
from .models import DumpingEvent, Camera, LegalDumpingLocation


def convert_to_webm(input_path, output_path):
    """
    Convert video to WebM using FFmpeg
    """
    command = [
        "ffmpeg",
        "-y",
        "-i", input_path,
        "-c:v", "libvpx-vp9",
        "-crf", "30",
        "-b:v", "0",
        "-pix_fmt", "yuv420p",
        "-c:a", "libopus",
        output_path
    ]

    subprocess.run(command, check=True)


def sync_and_list_events(camera_id=None):
    base_dir = settings.EVIDENCE_ROOT
    cameras = [camera_id] if camera_id else os.listdir(base_dir)

    for cam_id in cameras:
        cam_path = os.path.join(base_dir, cam_id)
        if not os.path.isdir(cam_path):
            continue

        camera, _ = Camera.objects.get_or_create(camera_id=cam_id)

        for event_folder in os.listdir(cam_path):
            event_path = os.path.join(cam_path, event_folder)
            json_file = os.path.join(event_path, "event.json")
            if not os.path.exists(json_file):
                continue

            with open(json_file, "r") as f:
                data = json.load(f)

            event_id = data.get("event_id") or str(uuid.uuid4())
            if DumpingEvent.objects.filter(event_id=event_id).exists():
                continue

            timestamp = parse_datetime(data.get("timestamp"))
            actor_name = data.get("actor", "")

            dumping_event = DumpingEvent(
                event_id=event_id,
                camera=camera,
                timestamp=timestamp,
                actor=actor_name
            )

            # location
            location_name = data.get("location")
            if location_name:
                dumping_event.location = LegalDumpingLocation.objects.filter(
                    name=location_name
                ).first()

            # ---- VIDEO HANDLING (MP4 → WEBM) ----
            input_video_name = data.get("dumping_video") or "dumping.mp4"
            input_video_path = os.path.join(event_path, input_video_name)

            if os.path.exists(input_video_path):
                output_video_name = "dumping.webm"
                media_subpath = f"dumping_videos/{cam_id}/{event_id}/{output_video_name}"
                full_media_path = os.path.join(settings.MEDIA_ROOT, media_subpath)
                os.makedirs(os.path.dirname(full_media_path), exist_ok=True)

                try:
                    convert_to_webm(input_video_path, full_media_path)

                    with open(full_media_path, "rb") as f:
                        dumping_event.dumping_video.save(
                            media_subpath, File(f), save=False
                        )

                except subprocess.CalledProcessError as e:
                    print(f"FFmpeg failed for {input_video_path}: {e}")
                    continue

            dumping_event.save()

    # Return events
    if camera_id:
        camera = Camera.objects.filter(camera_id=camera_id).first()
        if not camera:
            return []
        return DumpingEvent.objects.filter(camera=camera).order_by("-timestamp")

    return DumpingEvent.objects.all().order_by("-timestamp")
