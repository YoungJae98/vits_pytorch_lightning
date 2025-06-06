#!/usr/bin/env python3
# train.py

import torch
import datetime
import pytorch_lightning as pl
from pytorch_lightning.strategies import DDPStrategy

from noise_pop import utils                # HParams 및 로거
from youngjae.vits_pl.src.noise_pop.noise_trainer_pop_ss import NoiseModule


def main():
    # ── 1. 하이퍼파라미터 & 로거 ─────────────────────────────
    hps    = utils.get_hparams()              # CLI 인자 → HParams
    logger = utils.get_logger(hps.model_dir)
    logger.info(hps)

    # 2. 모델 생성
    model = NoiseModule(hps, logger)

    # 3. DDP 전략 (멀티-GPU 사용 시)
    # gpu_count = torch.cuda.device_count()

    strategy = DDPStrategy(
        process_group_backend="nccl",
        timeout=datetime.timedelta(seconds=5400),
        find_unused_parameters=True,
        gradient_as_bucket_view=True,
    )

    # 4. Trainer 설정
    trainer = pl.Trainer(
        accelerator="gpu",
        devices=6,
        precision=16,                    # mixed precision
        max_epochs=hps.train.max_epochs,
        enable_checkpointing=False,
        strategy=strategy
    )

    # 5. 학습 시작
    trainer.fit(model)


if __name__ == "__main__":
    main()
