# classiloom

CLI trainer for image classification. Gemini proposes hyperparameters. Keras backbones (MobileNetV2, EfficientNetB0, ResNet50) or a compact CNN. No database. Artifacts and metrics saved under `runs/`.

## Commands

- `classiloom set gemini_api <token>`
- `classiloom set gemini_model <name>`
- `classiloom scan <dataset_dir> --out runs`
- `classiloom suggest <scan_json> --trials 8 --out runs`
- `classiloom train <dataset_dir> <configs_json> --idx 0 --out runs [--mixed-precision] [--fine-tune]`
- `classiloom predict <image_path> <model_dir>`
