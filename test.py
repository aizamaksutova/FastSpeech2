import argparse
import json
import os
from pathlib import Path

import torch
from tqdm import tqdm

import hw_tts.synth.synth as synthesis
import hw_tts.model as module_model
from hw_tts.waveglow import get_WaveGlow
from hw_tts.utils import ROOT_PATH
import hw_tts.text as text
from hw_tts.utils.parse_config import ConfigParser

DEFAULT_CHECKPOINT_PATH = ROOT_PATH / "default_test_model" / "checkpoint.pth"


def main(config):
    logger = config.get_logger("test")

    # define cpu or gpu if possible
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # build model architecture
    model = config.init_obj(config["arch"], module_model)
    logger.info(model)

    logger.info("Loading checkpoint: {} ...".format(config.resume))
    checkpoint = torch.load(config.resume, map_location=device)
    state_dict = checkpoint["state_dict"]
    if config["n_gpu"] > 1:
        model = torch.nn.DataParallel(model)
    model.load_state_dict(state_dict)

    # prepare model for testing
    model = model.to(device)
    waveglow_model = get_WaveGlow().to(device)
    model.eval()

    # you can pass your test data as list of str

    test_data = []
    if args.text is not None:
        test_data.append(args.text)
    if args.file is not None:
        with open(args.file) as f:
            for test in f.readlines():
                test_data.append(test)

    test_data = list(text.text_to_sequence(test, ['english_cleaners']) for test in test_data)


    os.makedirs("results", exist_ok=True)
    with torch.no_grad():
        for i, phn in tqdm(enumerate(test_data)):
            synthesis.synth(model, device, waveglow_model, phn, path=f"results/wav_{i}_based.wav")

            # speed changes
            synthesis.synth(model, device, waveglow_model, phn, alpha=0.8,
                                          path=f"results/wav_{i}_speed=0_8.wav")
            synthesis.synth(model, device, waveglow_model, phn, alpha=1.2,
                                          path=f"results/wav_{i}_speed=1_2.wav")

            # energy changes
            synthesis.synth(model, device, waveglow_model, phn, e_alpha=0.8,
                                          path=f"results/wav_{i}_energy=0_8.wav")
            synthesis.synth(model, device, waveglow_model, phn, e_alpha=1.2,
                                          path=f"results/wav_{i}_energy=1_2.wav")

            # pitch changes
            synthesis.synth(model, device, waveglow_model, phn, p_alpha=0.8,
                                          path=f"results/wav_{i}_pitch=0_8.wav")
            synthesis.synth(model, device, waveglow_model, phn, p_alpha=1.2,
                                          path=f"results/wav_{i}_pitch=1_2.wav")

            # all together changes
            synthesis.synth(model, device, waveglow_model, phn,
                                          p_alpha=0.8, e_alpha=0.8, alpha=0.8,
                                          path=f"results/wav_{i}_together=0_8.wav")
            synthesis.synth(model, device, waveglow_model, phn,
                                          p_alpha=1.2, e_alpha=1.2, alpha=1.2,
                                          path=f"results/wav_{i}_together=1_2.wav")


if __name__ == "__main__":
    args = argparse.ArgumentParser(description="PyTorch Template")
    args.add_argument(
        "-c",
        "--config",
        default=None,
        type=str,
        help="config file path (default: None)",
    )
    args.add_argument(
        "-r",
        "--resume",
        default=str(DEFAULT_CHECKPOINT_PATH.absolute().resolve()),
        type=str,
        help="path to latest checkpoint (default: None)",
    )
    args.add_argument(
        "-d",
        "--device",
        default=None,
        type=str,
        help="indices of GPUs to enable (default: all)",
    )

    args.add_argument(
        "-f",
        "--file",
        default=None,
        type=str,
        help="the path to the file with texts for synthesis",
    )
    args.add_argument(
        "-t",
        "--text",
        default=None,
        type=str,
        help="text for synthesis",
    )


    args = args.parse_args()

    # set GPUs
    if args.device is not None:
        os.environ["CUDA_VISIBLE_DEVICES"] = args.device

    # first, we need to obtain config with model parameters
    # we assume it is located with checkpoint in the same folder
    model_config = Path(args.resume).parent / "config.json"
    with model_config.open() as f:
        config = ConfigParser(json.load(f), resume=args.resume)

    # update with addition configs from `args.config` if provided
    if args.config is not None:
        with Path(args.config).open() as f:
            config.config.update(json.load(f))

    main(config)
    
