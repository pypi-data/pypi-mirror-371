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
import threading, queue  # prefetching

# ---------- helpers ----------
def _to_numpy_cpu(x, dtype=None):
    """Convert CuPy / neurograd.Tensor / scalar to NumPy on CPU (no implicit device copies)."""
    # neurograd.Tensor
    if hasattr(x, "data"):
        buf = x.data
        if hasattr(buf, "get"):
            buf = buf.get()
        arr = np.asarray(buf)
    # CuPy array (or any object exposing .get to pull to host)
    elif hasattr(x, "get"):
        arr = x.get()
    else:
        arr = np.asarray(x)
    if dtype is not None and arr.dtype != dtype:
        arr = arr.astype(dtype)
    return arr

# ---------- core dataset/dataloader ----------
class Dataset:
    def __init__(self, X, y, dtype=float32):
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
                f" Total samples: {len(self)}\n"
                f" Input preview: {preview_x}\n"
                f" Target preview: {preview_y}")

class DataLoader:
    def __init__(self, dataset: Dataset, batch_size: int = 32, shuffle: bool = True,
                 seed: Optional[int] = None, num_workers: Optional[int] = None,
                 prefetch_batches: int = 8):
        self.dataset = dataset
        self.batch_size = batch_size
        self.shuffle = shuffle
        self.seed = seed
        if num_workers is None:
            cores = os.cpu_count() or 2
            self.num_workers = max(1, min(8, cores - 1))
        else:
            self.num_workers = int(num_workers)
        self.prefetch_batches = int(prefetch_batches)
        self._executor: Optional[ThreadPoolExecutor] = None

    def __len__(self):
        return math.ceil(len(self.dataset) / self.batch_size)

    def __getitem__(self, idx):
        # Return CPU numpy batches (so the queue stays CPU-only)
        start = idx * self.batch_size
        end = min((idx + 1) * self.batch_size, len(self.dataset))
        if self.num_workers > 0:
            if self._executor is None:
                self._executor = ThreadPoolExecutor(max_workers=self.num_workers)
            futures = [self._executor.submit(self.dataset.__getitem__, i) for i in range(start, end)]
            batch = [f.result() for f in futures]
        else:
            batch = [self.dataset[i] for i in range(start, end)]

        Xs, ys = zip(*batch)

        # Stack with NumPy (CPU)
        X = np.stack([x if isinstance(x, np.ndarray) else _to_numpy_cpu(x) for x in Xs], axis=0)
        if isinstance(ys[0], (np.ndarray, list, tuple)):
            y = np.stack([_to_numpy_cpu(y) for y in ys], axis=0)
        else:
            y = _to_numpy_cpu(ys)
        return X, y  # CPU

    def __iter__(self):
        if self.shuffle:
            self.dataset.shuffle(self.seed)

        q = queue.Queue(max(1, self.prefetch_batches))
        STOP = object()

        def producer():
            try:
                for idx in range(len(self)):
                    # Enqueue CPU numpy batches
                    q.put(self[idx], block=True)
            finally:
                q.put(STOP)

        threading.Thread(target=producer, daemon=True).start()

        while True:
            item = q.get()
            if item is STOP:
                break
            # Convert ONE dequeued batch to Tensors (GPU if xp=CuPy)
            X_np, y_np = item
            X = Tensor(xp.asarray(X_np), dtype=getattr(self.dataset, "img_dtype", None))
            y = Tensor(xp.asarray(y_np), dtype=getattr(self.dataset, "target_dtype", None))
            yield X, y

    def __repr__(self):
        return (f"<DataLoader: {len(self)} batches, "
                f"batch_size={self.batch_size}, "
                f"shuffle={self.shuffle}, seed={self.seed}, num_workers={self.num_workers}>")

    def __str__(self):
        return (f"DataLoader:\n"
                f" Batches: {len(self)}\n"
                f" Batch size: {self.batch_size}\n"
                f" Shuffle: {self.shuffle}\n"
                f" Seed: {self.seed}")

IMG_EXTS = (
    '.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tif', '.tiff', '.webp', '.jfif', '.avif', '.heif', '.heic'
)

class ImageFolder(Dataset):
    def __init__(
        self,
        root: str,
        img_shape: tuple = None,        # (H, W)
        img_mode: str = "RGB",          # "RGB", "L", etc.
        img_normalize: bool = True,     # /255 -> float
        img_transform: callable = None, # after numpy conversion
        target_transform: callable = None,
        img_dtype=xp.float32,           # used when yielding tensors
        target_dtype=xp.int64,          # used when yielding tensors
        chw: bool = True                # return CxHxW if True, else HxWxC
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
                    # filter unreadable exotica if cv2 lacks codec
                    if hasattr(cv2, "haveImageReader") and not cv2.haveImageReader(p):
                        continue
                    cls = os.path.basename(os.path.dirname(p))
                    self.images.append(p)
                    self.targets.append(cls)

    def __len__(self):
        return len(self.images)

    def _apply_img_transform(self, arr: np.ndarray) -> np.ndarray:
        if self.img_transform is None:
            return arr
        # Albumentations-style
        try:
            out = self.img_transform(image=arr)
            if isinstance(out, dict) and "image" in out:
                return out["image"]
        except TypeError:
            pass
        # Fallback: plain callable
        return self.img_transform(arr)

    # OpenCV fast path using imdecode (+ reduced decode for downscaling)
    def _load_image(self, path: str) -> np.ndarray:
        mode = (self.img_mode or "RGB").upper()

        # Reduced decode only when downscaling a lot; disabled for larger targets like 227+
        reduce = 0
        if self.img_shape is not None:
            h, w = self.img_shape
            max_side = max(int(h), int(w))
            if max_side <= 128:
                reduce = 4
            elif max_side <= 160:
                reduce = 2

        def _reduced_flag():
            if mode in ("L", "GRAY", "GREY", "GRAYSCALE"):
                if reduce == 4: return cv2.IMREAD_REDUCED_GRAYSCALE_4
                if reduce == 2: return cv2.IMREAD_REDUCED_GRAYSCALE_2
                return cv2.IMREAD_GRAYSCALE
            elif mode == "RGBA":
                return cv2.IMREAD_UNCHANGED
            else:
                if reduce == 4: return cv2.IMREAD_REDUCED_COLOR_4
                if reduce == 2: return cv2.IMREAD_REDUCED_COLOR_2
                return cv2.IMREAD_COLOR

        flag = _reduced_flag()
        try:
            flag |= cv2.IMREAD_IGNORE_ORIENTATION
        except Exception:
            pass

        data = np.fromfile(path, dtype=np.uint8)
        arr = cv2.imdecode(data, flag)
        if arr is None:
            arr = cv2.imread(path, cv2.IMREAD_UNCHANGED)
            if arr is None:
                raise ValueError(f"Failed to read image: {path}")

        # Convert channel order
        if mode == "RGB" and arr.ndim == 3 and arr.shape[2] == 3:
            arr = cv2.cvtColor(arr, cv2.COLOR_BGR2RGB)
        elif mode == "RGBA" and arr.ndim == 3 and arr.shape[2] == 4:
            arr = cv2.cvtColor(arr, cv2.COLOR_BGRA2RGBA)
        elif mode in ("L", "GRAY", "GREY", "GRAYSCALE") and arr.ndim == 2:
            pass
        elif arr.ndim == 2:
            arr = arr[:, :, None]

        # Resize to target
        if self.img_shape is not None:
            h, w = self.img_shape
            arr = cv2.resize(arr, (int(w), int(h)), interpolation=cv2.INTER_LINEAR)

        if arr.ndim == 2:
            arr = arr[:, :, None]

        if self.img_transform:
            arr = self._apply_img_transform(arr)

        if self.chw and arr.ndim == 3:
            arr = np.transpose(arr, (2, 0, 1))  # C,H,W

        if self.img_normalize:
            arr = arr.astype(np.float32) / 255.0

        return arr  # NumPy

    def __getitem__(self, idx: int):
        img_path = self.images[idx]
        target_name = self.targets[idx]

        image = self._load_image(img_path)   # NumPy
        target = self.target_mapping[target_name]

        if self.target_transform:
            target = self.target_transform(target)

        # Ensure target is CPU NumPy (handles CuPy/Tensor/scalars)
        target = _to_numpy_cpu(target)

        return image, target  # both CPU NumPy

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
