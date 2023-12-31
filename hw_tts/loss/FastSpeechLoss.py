import torch
from torch import Tensor
from torch import nn


class FastSpeechLoss(nn.Module):
    def __init__(self):
        super().__init__()
        self.mse_loss = nn.MSELoss()
        self.l1_loss = nn.L1Loss()
        

    def forward(self, mel, duration_predicted, pitch_prediction, energy_prediction, mel_target, duration_predictor_target, pitch_target, energy_target):
        mel_loss = self.l1_loss(mel, mel_target)

        duration_predictor_loss = self.mse_loss(duration_predicted,
                                               torch.log1p(duration_predictor_target.float()))
        pitch_loss = self.mse_loss(pitch_prediction, torch.log1p(pitch_target))
        energy_loss = self.mse_loss(energy_prediction, torch.log1p(energy_target))
        return mel_loss, duration_predictor_loss, pitch_loss, energy_loss
