"""Live streaming entry point for event camera inference.

Attempts to connect to a Prophesee (Metavision) camera first, then falls
back to a DAVIS device using `dv_processing`. Loads a ConvLSTM-based
model from checkpoint and visualizes predicted depth maps in real time.
"""

from eseg.models.ConvLSTM import EConvlstm
from eseg.config import checkpoint_path

import cv2
import torch

import sys
from typing import Optional
from eseg.utils.functions import _download_checkpoint
import argparse

# Mock URL for pretrained model (replace with real one later)
PRETRAINED_CHECKPOINT_URL = (
    "https://raw.githubusercontent.com/martinbarry59/eseg/main/src/checkpoints/CONVLSTM.pth"
)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def load_model():
    with torch.no_grad():

        network = "CONVLSTM"
        checkpoint_file: Optional[str] = None

        if checkpoint_path:
            checkpoint_file = f"{checkpoint_path}/CONVLSTM.pth"

            model = EConvlstm(model_type=network, skip_lstm=True)
            print(f"Loading checkpoint from {checkpoint_file}")
            try:
                model.load_state_dict(torch.load(checkpoint_file, map_location=device))
            except Exception:
                print("Checkpoint not found or failed to load.")
                # Ask user if they want to download the pretrained weights
                answer = input(
                    "Download pretrained checkpoint now? [y/N]: "
                ).strip().lower()
                if answer == "y":
                    if _download_checkpoint(PRETRAINED_CHECKPOINT_URL, checkpoint_file):
                        try:
                            model.load_state_dict(
                                torch.load(checkpoint_file, map_location=device)
                            )
                            print("Pretrained weights loaded.")
                        except Exception as e:
                            print(f"Downloaded file could not be loaded: {e}. Continuing uninitialized.")
                    else:
                        print("Download failed. Continuing with randomly initialized weights.")
                else:
                    print("Continuing without pretrained weights.")
        else:
            model = EConvlstm(model_type=network, skip_lstm=True)
    return model
model = load_model()
# Attempt dynamic camera backend selection


def parse_args():

    parser = argparse.ArgumentParser(
        description="Live event stream depth inference",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-i",
        "--input-event-file",
        default=None,
        help="Path to input event file (RAW or HDF5). If omitted, a live camera is used.",
    )
    parser.add_argument(
        "-s",
        "--slice-time-ms",
        type=int,
        default=100,
        help="Time window for each event slice in milliseconds.",
    )
    parser.add_argument(
        "-f",
        "--filter-size-ms",
        type=int,
        default=20,
        help="Size of the temporal noise filter in milliseconds.",
    )
    return parser.parse_args()

def run(input_event_file = None,slice_time_ms: int = 100, filter_size_ms: int = 20):
    
    # try:
    sys.path.append("/usr/lib/python3/dist-packages")

    from metavision_sdk_stream import Camera  # type: ignore
    if input_event_file:
        camera = Camera.from_file(input_event_file)
    else:
        camera = Camera.from_first_available()

    from .utils.dataviewers import dataviewerprophesee as dataviewer  # type: ignore
    # except Exception:
    #     try:
    #         import dv_processing as dv  # type: ignore

    #         camera = dv.io.camera.open()
    #         from .utils.dataviewers import dataviewerdavis as dataviewer  # type: ignore
    #     except Exception:
    #         print("Could not find any compatible event cameras.")
    #         sys.exit(1)
    viewer = dataviewer(camera, slice_time_ms=slice_time_ms, filter_size_ms=filter_size_ms)

    model.to(device)
    viewer.setModel(model)
    viewer.run()

    cv2.destroyAllWindows()


if __name__ == "__main__":
    args = parse_args()
    run(
        input_event_file=args.input_event_file,
        slice_time_ms=args.slice_time_ms,
        filter_size_ms=args.filter_size_ms
    )
