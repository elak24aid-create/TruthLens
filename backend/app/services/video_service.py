import os
import tempfile
import logging
import cv2
from typing import Dict, Any
from app.services.ocr_service import extract_text_from_image

logger = logging.getLogger(__name__)

async def extract_text_from_video(video_bytes: bytes, max_frames: int = 5) -> Dict[str, Any]:
    """
    Safely extracts frames from a video and runs OCR on them.
    Returns combined text and metadata.
    """
    temp_fd, temp_path = tempfile.mkstemp(suffix=".mp4")
    try:
        with os.fdopen(temp_fd, 'wb') as f:
            f.write(video_bytes)

        cap = cv2.VideoCapture(temp_path)
        if not cap.isOpened():
            raise ValueError("Unable to decode video format.")

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        duration = total_frames / fps if fps and fps > 0 else 0.0

        if total_frames <= 0:
            raise ValueError("Video contains no readable frames.")

        # Determine frame indices to sample
        step = max(1, total_frames // max_frames)
        frame_indices = [i * step for i in range(max_frames) if i * step < total_frames]
        
        extracted_text_blocks = []
        timestamps = []
        
        for idx in frame_indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ret, frame = cap.read()
            if not ret:
                continue
                
            # Calculate timestamp
            ts_sec = idx / fps if fps and fps > 0 else 0
            mins = int(ts_sec // 60)
            secs = int(ts_sec % 60)
            ts_str = f"[{mins:02d}:{secs:02d}]"
            
            # Encode frame to memory
            success, buffer = cv2.imencode(".png", frame)
            if not success:
                continue
                
            frame_bytes = buffer.tobytes()
            
            try:
                # Use existing OCR
                text = await extract_text_from_image(frame_bytes)
                if text and len(text.strip()) > 3:
                    # Basic dedup: skip if this text is very similar to the last one
                    if not extracted_text_blocks or text.strip() not in extracted_text_blocks[-1]:
                        extracted_text_blocks.append(f"{ts_str}\n{text.strip()}")
                        timestamps.append(ts_str)
            except Exception as e:
                logger.warning(f"OCR failed on frame {idx}: {e}")

        cap.release()

        combined_text = "\n\n".join(extracted_text_blocks)
        
        return {
            "text": combined_text,
            "duration_sec": duration,
            "frames_sampled": len(frame_indices),
            "timestamps": timestamps
        }

    except Exception as e:
        logger.error(f"Error processing video: {e}")
        raise
    finally:
        try:
            os.remove(temp_path)
        except OSError:
            pass
