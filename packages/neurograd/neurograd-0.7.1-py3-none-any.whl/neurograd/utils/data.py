from neurograd import Tensor, float32
import math
import random
import os
import cv2
cv2.setNumThreads(1)
import numpy as np
from neurograd import xp
from typing import Optional
from concurrent.futures import ThreadPoolExecutor

class Dataset:
    def __init__(self, X, y, dtype = float32):
        assert len(X) == len(y), "Mismatched input and label lengths"
        self.X = Tensor(X, dtype=dtype)
        self.y = Tensor(y, dtype=dtype)
    def __len__(self):
        return len(self.X)
    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]
    def __iter__(self):
        for idx in range(len(self)):
            yield self[idx]
    def shuffle(self, seed: Optional[int] = None):
        indices = list(range(len(self)))
        rng = random.Random(seed) if seed is not None else random.Random()
        rng.shuffle(indices)
        self.X = self.X[indices]
        self.y = self.y[indices]
    def __repr__(self):
        return f"<Dataset: {len(self)} samples, dtype={self.X.data.dtype}>"
    def __str__(self):
        preview_x = self.X[:1]
        preview_y = self.y[:1]
        return (f"Dataset:\n"
                f"  Total samples: {len(self)}\n"
                f"  Input preview: {preview_x}\n"
                f"  Target preview: {preview_y}")
    


class DataLoader:
    def __init__(self, dataset: Dataset, batch_size: int = 32, 
                 shuffle: bool = True, seed: Optional[int] = None,
                 num_workers: Optional[int] = None):
        self.dataset = dataset
        self.batch_size = batch_size
        self.shuffle = shuffle
        self.seed = seed
        if num_workers is None:
            cores = os.cpu_count() or 2
            self.num_workers = max(1, min(8, cores - 1))
        else:
            self.num_workers = int(num_workers)
        self._executor: Optional[ThreadPoolExecutor] = None
    def __len__(self):
        return math.ceil(len(self.dataset) / self.batch_size)
    def __getitem__(self, idx):
        start = idx * self.batch_size
        end = min((idx + 1) * self.batch_size, len(self.dataset))
        if self.num_workers > 0:
            if self._executor is None:
                self._executor = ThreadPoolExecutor(max_workers=self.num_workers)
            futures = [self._executor.submit(self.dataset.__getitem__, i) for i in range(start, end)]
            batch = [f.result() for f in futures]
        else:
            batch = [self.dataset[i] for i in range(start, end)]  # int indices only
        Xs, ys = zip(*batch)
        X = Tensor(xp.stack([x.data for x in Xs], axis=0), dtype=Xs[0].dtype)
        y = Tensor(xp.stack([y.data for y in ys], axis=0), dtype=ys[0].dtype)
        return X, y
    def __iter__(self):
        if self.shuffle:
            self.dataset.shuffle(self.seed)
        for idx in range(len(self)):
            yield self[idx]
    def __repr__(self):
        return (f"<DataLoader: {len(self)} batches, "
            f"batch_size={self.batch_size}, "
            f"shuffle={self.shuffle}, seed={self.seed}, num_workers={self.num_workers}>")
    def __str__(self):
        return (f"DataLoader:\n"
                f"  Batches: {len(self)}\n"
                f"  Batch size: {self.batch_size}\n"
                f"  Shuffle: {self.shuffle}\n"
                f"  Seed: {self.seed}")

                     

IMG_EXTS = (
    '.png', '.jpg', '.jpeg', '.bmp', '.gif',
    '.tif', '.tiff', '.webp', '.jfif', '.avif',
    '.heif', '.heic'
)

class ImageFolder(Dataset):
    def __init__(
        self,
        root: str,
        img_shape: tuple = None,          # (H, W)
        img_mode: str = "RGB",            # "RGB", "L", etc.
        img_normalize: bool = True,              # /255 -> float
        img_transform: callable = None,   # after numpy conversion
        target_transform: callable = None,
        img_dtype=xp.float32,                    # handled by Tensor(...)
        target_dtype=xp.int64,                   # handled by Tensor(...)
        chw: bool = True                         # return CxHxW if True, else HxWxC
    ):
        self.root = root
        self.img_shape = img_shape
        self.img_mode = img_mode
        self.img_normalize = img_normalize
        self.img_transform = img_transform
        self.target_transform = target_transform
        self.img_dtype = img_dtype
        self.target_dtype = target_dtype
        self.chw = chw

        self.images: list[str] = []
        self.targets: list[str] = []
        self._collect_paths()

        # stable class mapping
        self.target_names = sorted(set(self.targets))
        self.target_mapping = {name: i for i, name in enumerate(self.target_names)}
        self.num_classes = len(self.target_names)

    def _collect_paths(self):
        for r, _, files in os.walk(self.root):
            for f in files:
                if f.lower().endswith(IMG_EXTS):
                    p = os.path.join(r, f)
                    cls = os.path.basename(os.path.dirname(p))
                    self.images.append(p)
                    self.targets.append(cls)

    def __len__(self):
        return len(self.images)
    
    def _apply_img_transform(self, arr: np.ndarray) -> np.ndarray:
        if self.img_transform is None:
            return arr
        # Try Albumentations-style call
        try:
            out = self.img_transform(image=arr)
            if isinstance(out, dict) and "image" in out:
                return out["image"]
        except TypeError:
            pass
        # Fallback: plain callable expecting ndarray
        return self.img_transform(arr)

    def _load_image(self, path: str) -> np.ndarray:
        # OpenCV-only fast decode/resize
        mode = (self.img_mode or "RGB").upper()
        if mode in ("L", "GRAY", "GREY", "GRAYSCALE"):
            flag = cv2.IMREAD_GRAYSCALE
        elif mode == "RGBA":
            flag = cv2.IMREAD_UNCHANGED  # preserve alpha if present
        else:
            flag = cv2.IMREAD_COLOR  # BGR
        # Avoid EXIF orientation work
        try:
            flag |= cv2.IMREAD_IGNORE_ORIENTATION
        except Exception:
            pass

        arr = cv2.imread(path, flag)
        if arr is None:
            raise ValueError(f"Failed to read image: {path}")

        # Convert channel order to match RGB/RGBA expectations
        if mode == "RGB" and arr.ndim == 3 and arr.shape[2] == 3:
            arr = cv2.cvtColor(arr, cv2.COLOR_BGR2RGB)
        elif mode == "RGBA" and arr.ndim == 3 and arr.shape[2] == 4:
            arr = cv2.cvtColor(arr, cv2.COLOR_BGRA2RGBA)

        # Resize if requested (cv2 expects (W,H))
        if self.img_shape is not None:
            h, w = self.img_shape
            arr = cv2.resize(arr, (int(w), int(h)), interpolation=cv2.INTER_LINEAR)
        if arr.ndim == 2:
            arr = arr[:, :, None]
        if self.img_transform:
            arr = self._apply_img_transform(arr)
        if self.chw:
            arr = np.transpose(arr, (2, 0, 1))  # C,H,W
        if self.img_normalize:
            arr = arr.astype(np.float32) / 255.0
        return arr

    def __getitem__(self, idx: int):
        img_path = self.images[idx]
        target_name = self.targets[idx]

        image = self._load_image(img_path)
        target = self.target_mapping[target_name]

        if self.target_transform:
            target = self.target_transform(target)

        # Convert to Tensor with dtype specified in init
        return Tensor(image, dtype=self.img_dtype), Tensor(target, dtype=self.target_dtype)

    def shuffle(self, seed: Optional[int] = None):
        rng = random.Random(seed) if seed is not None else random.Random()
        idxs = list(range(len(self)))
        rng.shuffle(idxs)
        self.images = [self.images[i] for i in idxs]
        self.targets = [self.targets[i] for i in idxs]

    def __repr__(self):
        shape = None
        if len(self) > 0:
            try:
                image, _ = self[0]
                shape = tuple(image.shape)
            except Exception:
                shape = None
        return (f"ImageFolder(root='{self.root}', samples={len(self)}, "
                f"classes={getattr(self, 'num_classes', 0)}, "
                f"shape={shape}, img_dtype={self.img_dtype}, target_dtype={self.target_dtype}, "
                f"mode='{self.img_mode}', normalize={self.img_normalize}, chw={self.chw})")

    def __iter__(self):
        for i in range(len(self)):
            yield self[i]
