from __future__ import annotations

import hashlib
import os
import sys
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Tuple, Union

import librosa
import numpy as np
import math
import torch
import torchaudio
import warnings
from tqdm import tqdm

from .band_split_roformer import BSRoformer


@dataclass
class SeparationConfig:
    # 推論関連
    target_sample_rate: int = 44100
    device_preference: Optional[str] = None  # "cuda" / "cpu" / "mps"
    use_half_precision: bool = False

    chunk_size: int = 588_800  # 約 13.35 秒 @ 44.1kHz
    hop_size: Optional[int] = None  # 既定: chunk_size // 2（50% overlap）
    window_type: str = "hann"  # "hann" 推奨

    stem_names: Tuple[str, ...] = (
        "bass",
        "drums",
        "other",
        "vocals",
        "guitar",
        "piano",
    )

    model_name: str = "bs_roformer"
    hf_repo_id: Optional[str] = None
    hf_filename: Optional[str] = None
    hf_revision: str = "main"
    expected_sha256: Optional[str] = None  # 任意：完全性検証に使用

    # キャッシュ先（未指定ならユーザホーム配下）
    cache_dir: Optional[Path] = None


# モデル名→Hugging Face 上の既定情報（必要に応じて上書き）
MODEL_REGISTRY: Dict[str, Dict[str, str]] = {
    "bs_roformer": {
        "repo_id": "anime-song/stem-splitter",
        "filename": "stem_splitter.pt",
        "revision": "main",
    }
}


def _save_wav_no_warning(out_path: Path, samples: torch.Tensor, sample_rate: int) -> None:
    """
    警告を出さずに WAV 保存する。
    優先度: TorchCodec > torchaudio.save_with_torchcodec > torchaudio.save(最後の手段)
    入力: samples (C, T), float32 [-1, 1] 推奨
    """
    if samples.device.type != "cpu":
        samples = samples.cpu()
    samples = samples.contiguous().to(torch.float32)

    # 可能なら TorchCodec を直接使用（推奨）
    try:
        from torchcodec.encoders import AudioEncoder  # pip install torchcodec

        AudioEncoder(samples, sample_rate=sample_rate).to_file(str(out_path))
        return
    except Exception:
        pass

    # torchaudio の TorchCodec 経由 API（存在する場合）
    if hasattr(torchaudio, "save_with_torchcodec"):
        torchaudio.save_with_torchcodec(str(out_path), samples, sample_rate, channels_first=True)
        return

    warnings.filterwarnings(
        "ignore",
        message="In 2.9, this function's implementation will be changed to use torchaudio.save_with_torchcodec",
        category=UserWarning,
        module=r"torchaudio\._backend\.utils",
    )
    warnings.filterwarnings(
        "ignore",
        message="StreamWriter has been deprecated",
        category=UserWarning,
        module=r"torchaudio\._backend\.ffmpeg",
    )
    torchaudio.save(str(out_path), samples, sample_rate)


def resolve_device(device_preference: Optional[str]) -> torch.device:
    if device_preference is not None:
        return torch.device(device_preference)
    if torch.cuda.is_available():
        return torch.device("cuda")
    if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def default_cache_dir() -> Path:
    return Path(os.environ.get("STEM_SPLITTER_CACHE", Path.home() / ".cache" / "stem_splitter" / "weights"))


def get_model_info(config: SeparationConfig) -> Tuple[str, str, str]:
    """
    config から Hugging Face の repo / filename / revision を解決。
    未指定なら MODEL_REGISTRY を参照。
    """
    repo_id = config.hf_repo_id
    filename = config.hf_filename
    revision = config.hf_revision

    if (repo_id is None or filename is None) and config.model_name in MODEL_REGISTRY:
        fallback = MODEL_REGISTRY[config.model_name]
        repo_id = repo_id or fallback["repo_id"]
        filename = filename or fallback["filename"]
        revision = revision or fallback.get("revision", "main")

    if repo_id is None or filename is None:
        raise ValueError(
            "Hugging Face の重みファイル情報が不足しています。"
            " SeparationConfig(hf_repo_id=..., hf_filename=...) を指定するか、MODEL_REGISTRY を更新してください。"
        )
    return repo_id, filename, revision


def build_weight_path(config: SeparationConfig, filename: str) -> Path:
    cache_root = config.cache_dir or default_cache_dir()
    cache_root.mkdir(parents=True, exist_ok=True)
    return cache_root / filename


def sha256sum(file_path: Path) -> str:
    h = hashlib.sha256()
    with file_path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def download_from_huggingface(
    repo_id: str,
    filename: str,
    revision: str,
    destination: Path,
) -> None:
    base_url = f"https://huggingface.co/{repo_id}/resolve/{revision}/{filename}?download=true"

    with urllib.request.urlopen(base_url) as response:
        total_size = int(response.headers.get("Content-Length", "0"))
        block_size = 1024 * 1024  # 1MB
        tmp_path = destination.with_suffix(".tmp")

        with (
            tmp_path.open("wb") as out_file,
            tqdm(
                total=total_size if total_size > 0 else None,
                unit="B",
                unit_scale=True,
                desc=f"Downloading {filename}",
            ) as progress_bar,
        ):
            while True:
                data = response.read(block_size)
                if not data:
                    break
                out_file.write(data)
                progress_bar.update(len(data))

        tmp_path.replace(destination)


def ensure_weight_file(config: SeparationConfig) -> Path:
    repo_id, filename, revision = get_model_info(config)
    weight_path = build_weight_path(config, filename)

    if weight_path.exists():
        if config.expected_sha256:
            actual = sha256sum(weight_path)
            if actual.lower() != config.expected_sha256.lower():
                print(
                    f"[WARN] 既存の重みファイルの SHA256 が一致しません。再取得します。\n"
                    f"  expected={config.expected_sha256}\n  actual  ={actual}"
                )
                weight_path.unlink(missing_ok=True)
        else:
            # 検証なしでそのまま使用
            return weight_path

    # ダウンロード
    print(f"[INFO] 重みファイルが見つかりません。Hugging Face から取得します: {repo_id}/{filename}@{revision}")
    download_from_huggingface(repo_id, filename, revision, weight_path)

    if config.expected_sha256:
        actual = sha256sum(weight_path)
        if actual.lower() != config.expected_sha256.lower():
            weight_path.unlink(missing_ok=True)
            raise RuntimeError("ダウンロードした重みファイルの SHA256 が一致しません。")

    return weight_path


def load_state_dict_flex(path: Path) -> Dict[str, torch.Tensor]:
    """
    checkpoint 形式の違いに寛容なロード（state_dict 直/ラップの両対応）。
    """
    try:
        checkpoint = torch.load(str(path), map_location="cpu", weights_only=False)
    except TypeError:
        # PyTorch の引数差異対策（古い/新しい両対応）
        checkpoint = torch.load(str(path), map_location="cpu")

    if isinstance(checkpoint, dict):
        # 典型例: {"state_dict": ..., ...} / {"model": ..., ...} / そのまま state_dict
        for key in ("state_dict", "model", "ema_state_dict"):
            if key in checkpoint and isinstance(checkpoint[key], dict):
                return checkpoint[key]
        return checkpoint  # そのまま state_dict とみなす
    raise RuntimeError("未知のチェックポイント形式です。dict ではありません。")


def load_mss_model(config: SeparationConfig, device: torch.device) -> torch.nn.Module:
    """
    BSRoformer を作成し、重みを読み込んで返します。
    """
    weight_path = ensure_weight_file(config)

    model = BSRoformer(
        dim=256,
        num_layers=12,
        sample_rate=config.target_sample_rate,
        num_channels=2,
        head_dim=64,
        num_heads=8,
        n_fft=2048,
        hop_length=512,
        num_stems=len(config.stem_names),
    )

    # 重みを読み込み
    state_dict = load_state_dict_flex(weight_path)
    missing, unexpected = model.load_state_dict(state_dict, strict=False)
    if missing:
        print(f"[WARN] 欠落している重みキー: {sorted(missing)[:5]}{' ...' if len(missing) > 5 else ''}")
    if unexpected:
        print(f"[WARN] 予期しない重みキー: {sorted(unexpected)[:5]}{' ...' if len(unexpected) > 5 else ''}")

    model.to(device)
    if config.use_half_precision and device.type == "cuda":
        model.half()
    model.eval()
    return model


def _separate_one_file(
    input_wav_path: Path,
    output_directory: Path,
    config: SeparationConfig,
    model: torch.nn.Module,
    device: torch.device,
    dtype: torch.dtype,
) -> Dict[str, Path]:
    """
    単一の WAV を処理し、ステムごとの出力パスを返す。
    入力: (C, T) / モデル入出力: (B, C, T) -> (B, N, C, T)
    OLA: chunk_size, hop_size, Hann 窓（sum-of-windows 正規化）
    """
    # 読み込み -> (C, T) に正規化
    y, _ = librosa.load(str(input_wav_path), sr=config.target_sample_rate, mono=False)
    if y.ndim == 1:
        y = y[None, :]  # (1, T)
    elif y.ndim == 2 and y.shape[0] > y.shape[1]:
        # librosa は (T, C) を返すことがあるので (C, T) へ
        y = y.T
    y = y.astype(np.float32, copy=False)  # (C, T)

    channels, total_length = y.shape

    # チャンク条件
    chunk_size = int(config.chunk_size)
    hop_size = int(config.hop_size) if config.hop_size is not None else chunk_size // 2
    if hop_size <= 0 or hop_size > chunk_size:
        raise ValueError("hop_size は 1..chunk_size の範囲で指定してください")

    # padding 後の長さ（最後が半端でも必ず 1 チャンクぶん確保）
    if total_length <= chunk_size:
        padded_length = chunk_size
    else:
        steps = math.ceil((total_length - chunk_size) / hop_size)
        padded_length = steps * hop_size + chunk_size

    if padded_length > total_length:
        pad_amount = padded_length - total_length
        y = np.pad(y, ((0, 0), (0, pad_amount)), mode="constant")

    # 窓・蓄積（sum-of-windows で正規化）
    if config.window_type.lower() != "hann":
        raise ValueError(f"未対応の window_type: {config.window_type}")
    base_window = torch.hann_window(chunk_size, periodic=False, dtype=dtype, device=device)

    num_stems = len(config.stem_names)
    accum = np.zeros((num_stems, channels, padded_length), dtype=np.float32)
    weight_sum = np.zeros(padded_length, dtype=np.float32)  # ← 窓の和を積む

    # チャンク推論ループ
    for start in range(0, padded_length - chunk_size + 1, hop_size):
        end = start + chunk_size

        # 末尾の短い区間はここでゼロパディング（上の pad と二重になっても影響なし）
        input_chunk_np = y[:, start:end]
        if input_chunk_np.shape[1] < chunk_size:
            pad = chunk_size - input_chunk_np.shape[1]
            input_chunk_np = np.pad(input_chunk_np, ((0, 0), (0, pad)), mode="constant")

        # (1, C, T)
        input_chunk = torch.from_numpy(input_chunk_np).to(device=device, dtype=dtype).unsqueeze(0)

        with torch.no_grad():
            output_chunk = model(input_chunk)  # (1, N, C, T_out)

        if not isinstance(output_chunk, torch.Tensor) or output_chunk.ndim != 4:
            raise RuntimeError("モデル出力は (B, N, C, T) の Tensor を想定しています。")

        _, _, _, t_out = output_chunk.shape
        window = (
            base_window if t_out == chunk_size else torch.hann_window(t_out, periodic=False, dtype=dtype, device=device)
        )

        # 出力に 1 回だけ窓掛け → 合成は窓の「和」で割る
        windowed = (output_chunk * window.view(1, 1, 1, -1)).squeeze(0)  # (N, C, T)
        out_np = windowed.to(torch.float32).cpu().numpy()

        accum[:, :, start : start + t_out] += out_np
        weight_sum[start : start + t_out] += window.to(torch.float32).cpu().numpy()

        del input_chunk, output_chunk, windowed  # メモリ節約

    # sum-of-windows で正規化（端も自然に補正される）
    eps = 1e-8
    weight_sum = np.maximum(weight_sum, eps)
    accum /= weight_sum[None, None, :]

    # 元の長さにトリムして保存
    trim_length = total_length
    base_name = input_wav_path.stem
    saved_paths: Dict[str, Path] = {}

    for i, stem_name in enumerate(config.stem_names):
        stem_array = accum[i, :, :trim_length]  # (C, T)
        stem_tensor = torch.from_numpy(stem_array)  # float32
        out_path = output_directory / base_name / f"{base_name}_{stem_name}.wav"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        _save_wav_no_warning(out_path, stem_tensor, config.target_sample_rate)
        saved_paths[stem_name] = out_path

    return saved_paths


def separate_stems(
    input_audio_path: Union[str, Path],
    output_directory: Union[str, Path],
    config: Optional[SeparationConfig] = None,
) -> Union[Dict[str, Path], Dict[Path, Dict[str, Path]]]:
    if config is None:
        config = SeparationConfig()

    input_path = Path(input_audio_path)
    output_dir = Path(output_directory)
    output_dir.mkdir(parents=True, exist_ok=True)

    # デバイス・dtype・モデルはここで1回だけ
    device = resolve_device(config.device_preference)
    dtype = torch.float16 if (config.use_half_precision and device.type == "cuda") else torch.float32
    model = load_mss_model(config, device=device)

    if input_path.is_file():
        if input_path.suffix.lower() != ".wav":
            raise ValueError("WAV 以外は許可していません。入力は .wav にしてください。")
        return _separate_one_file(input_path, output_dir, config, model, device, dtype)

    if input_path.is_dir():
        wav_files = sorted([p for p in input_path.rglob("*") if p.is_file() and p.suffix.lower() == ".wav"])
        if not wav_files:
            raise FileNotFoundError("指定ディレクトリに .wav ファイルが見つかりません。")

        results: Dict[Path, Dict[str, Path]] = {}
        for wav_path in wav_files:
            current_out_dir = output_dir  # フラットに保存する場合はこちら
            result = _separate_one_file(wav_path, current_out_dir, config, model, device, dtype)
            results[wav_path] = result
        return results

    raise FileNotFoundError(f"入力パスが存在しません: {input_path}")


def _build_arg_parser():
    import argparse

    parser = argparse.ArgumentParser(description="Stem Splitter Inference (BSRoformer, OLA)")
    parser.add_argument("input_audio_path", type=Path, help="入力音声ファイルのパス")
    parser.add_argument("--out-dir", type=Path, required=True, help="出力ディレクトリ")
    parser.add_argument("--device", default=None, help="cuda / cpu / mps（未指定で自動判定）")
    parser.add_argument("--sr", type=int, default=44100, help="サンプルレート")
    parser.add_argument("--no-half", action="store_true", help="半精度を無効化（既定はCUDA上で有効）")

    parser.add_argument("--chunk-size", type=int, default=588_800, help="チャンク長（サンプル数）")
    parser.add_argument("--hop-size", type=int, default=None, help="ホップ長（未指定で chunk_size//2）")
    parser.add_argument("--window", type=str, default="hann", help="ウィンドウ種別（hann のみ対応）")

    # 重み指定の上書き
    parser.add_argument("--model-name", default="bs_roformer", help="MODEL_REGISTRY のキー")
    parser.add_argument("--hf-repo", default=None, help="Hugging Face repo_id")
    parser.add_argument("--hf-file", default=None, help="Hugging Face ファイル名")
    parser.add_argument("--hf-rev", default="main", help="Hugging Face リビジョン")
    parser.add_argument("--weights-cache", type=Path, default=None, help="重みキャッシュディレクトリ")
    parser.add_argument("--sha256", default=None, help="重みファイル SHA256（任意）")
    return parser


def main():
    parser = _build_arg_parser()
    args = parser.parse_args()

    config = SeparationConfig(
        target_sample_rate=args.sr,
        device_preference=args.device,
        use_half_precision=not args.no_half,
        chunk_size=args.chunk_size,
        hop_size=args.hop_size,
        window_type=args.window,
        model_name=args.model_name,
        hf_repo_id=args.hf_repo,
        hf_filename=args.hf_file,
        hf_revision=args.hf_rev,
        expected_sha256=args.sha256,
        cache_dir=args.weights_cache,
    )

    try:
        result = separate_stems(args.input_audio_path, args.out_dir, config)
    except Exception as exc:
        print(f"[ERROR] 推論に失敗しました: {exc}", file=sys.stderr)
        sys.exit(1)

    # 表示
    if isinstance(result, dict) and result and isinstance(next(iter(result.values())), Path):
        # 単一ファイルケース: {stem: path}
        for stem_name, out_path in result.items():
            print(f"{stem_name}: {out_path}")
    else:
        # ディレクトリケース: {input_wav: {stem: path}}
        for input_wav, stems_dict in result.items():
            print(f"[{input_wav}]")
            for stem_name, out_path in stems_dict.items():
                print(f"  {stem_name}: {out_path}")


if __name__ == "__main__":
    main()
