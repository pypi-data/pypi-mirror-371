#!/usr/bin/env python3
# pyright: reportMissingTypeStubs=false
"""Simple code search with embeddings."""

import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
import warnings
warnings.filterwarnings("ignore")

import asyncio
import pickle
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set

import numpy as np
import torch
import faiss  # type: ignore[reportMissingTypeStubs]
from sentence_transformers import SentenceTransformer
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from sklearn.cluster import DBSCAN  # type: ignore[reportMissingTypeStubs]

# Simple API
class Embeddings:
    def __init__(self, folder: str, supported_extensions: Optional[Set[str]] = None, ignore_file: Optional[str] = None, model: str = "all-MiniLM-L6-v2"):
        self.suite = EmbeddingsSuite(folder, supported_extensions, ignore_file, model)
        asyncio.run(self.suite.build_initial_index())
    
    def search(self, query: Optional[str] = None, negative_query: Optional[str] = None, files=None, top_n: int = 20, min_similarity: float = -1.0):
        results = self.suite.search_code(query, negative_query, top_n)
        if files:
            results = [r for r in results if r.file_path in files]
        results = [r for r in results if r.max_similarity >= min_similarity]
        return results


@dataclass
class CodeSection:
    """A section of code with context."""
    file_path: str
    start_line: int
    end_line: int
    lines: List[str]
    avg_similarity: float
    max_similarity: float

    def __str__(self) -> str:
        header = f"File: {self.file_path} (lines {self.start_line}-{self.end_line})\n"
        numbered = "\n".join(f"{i:4d}: {line}" for i, line in enumerate(self.lines, start=self.start_line))
        return header + numbered


class EmbeddingsIndexer:
    """Manages line-by-line code embeddings with FAISS."""

    MAX_LINES_PER_FILE = 10000
    DEFAULT_EXTENSIONS = {
        ".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".cpp", ".c", ".h",
        ".cs", ".go", ".rs", ".rb", ".php", ".swift", ".kt", ".scala",
        ".sh", ".bash", ".zsh", ".yaml", ".yml", ".json", ".xml", ".html",
        ".css", ".scss", ".sql", ".r", ".m", ".mm", ".md", ".txt"
    }

    def __init__(self, project_path: Path, model: str, supported_extensions: Optional[Set[str]] = None, ignore_file: Optional[str] = None):
        self.project_path = project_path.absolute()
        self.index_path = self.project_path / ".embeddings"
        self.index_path.mkdir(exist_ok=True)
        
        self.supported_extensions = supported_extensions or self.DEFAULT_EXTENSIONS
        self.ignore_patterns = self._load_ignore_patterns(ignore_file)

        # Choose device (MPS on Apple if available)
        device = "mps" if torch.backends.mps.is_available() else "cpu"
        self.model = SentenceTransformer(model, device=device)

        # Cosine similarity via inner product on normalized vectors
        self.dimension = self.model.get_sentence_embedding_dimension()
        self.index: faiss.Index = faiss.IndexFlatIP(self.dimension)

        # Reverse map: doc_id -> (file_path, line_num)
        self.id_to_meta: List[Tuple[str, int]] = []

        # Concurrency control
        self.lock = threading.RLock()

        self._load_index()
    
    def _load_ignore_patterns(self, ignore_file: Optional[str]) -> Set[str]:
        """Load ignore patterns from file, similar to .gitignore."""
        patterns = set()
        if ignore_file and Path(ignore_file).exists():
            with open(ignore_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        patterns.add(line)
        return patterns
    
    def _should_ignore(self, path: Path) -> bool:
        """Check if path should be ignored based on patterns."""
        path_str = str(path.relative_to(self.project_path))
        for pattern in self.ignore_patterns:
            if pattern in path_str or path.name == pattern:
                return True
            # Simple glob-like matching for extensions
            if pattern.startswith('*.') and path.suffix == pattern[1:]:
                return True
        return False


    def _load_index(self) -> None:
        index_file = self.index_path / "faiss_index.bin"
        meta_file = self.index_path / "id_to_meta.pkl"
        if index_file.exists() and meta_file.exists():
            self.index = faiss.read_index(str(index_file))
            with open(meta_file, "rb") as f:
                self.id_to_meta = pickle.load(f)
            print("✅ Loaded existing embeddings index")
        else:
            self.index = faiss.IndexFlatIP(self.dimension)
            self.id_to_meta = []

    def _atomic_write(self, path: Path, data: bytes) -> None:
        tmp = path.with_suffix(path.suffix + ".tmp")
        with open(tmp, "wb") as f:
            f.write(data)
        os.replace(tmp, path)

    def _save_index(self) -> None:
        index_file = self.index_path / "faiss_index.bin"
        meta_file = self.index_path / "id_to_meta.pkl"
        with self.lock:
            faiss.write_index(self.index, str(index_file))
            # pickle with atomic replace
            data = pickle.dumps(self.id_to_meta, protocol=pickle.HIGHEST_PROTOCOL)
            self._atomic_write(meta_file, data)


    async def build_index(self) -> None:
        """Build the embeddings index for all project files from scratch."""
        files = self._get_project_files()
        if not files:
            print("No supported files found in project")
            return

        print(f"Processing {len(files)} files…")
        all_lines: List[str] = []
        new_meta: List[Tuple[str, int]] = []

        for file_path in files:
            rel = str(file_path.relative_to(self.project_path))
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()[: self.MAX_LINES_PER_FILE]
            for i, line in enumerate(lines, start=1):
                text = line.rstrip("\n")
                if text.strip():  # skip blank-only lines
                    all_lines.append(text)
                    new_meta.append((rel, i))

        if not all_lines:
            print("No lines to index.")
            with self.lock:
                self.index = faiss.IndexFlatIP(self.dimension)
                self.id_to_meta = []
                self._save_index()
            return

        print(f"Building embeddings for {len(all_lines)} lines…")
        # Encode in batches
        embeddings = self.model.encode(all_lines, show_progress_bar=False, batch_size=64)
        embeddings = embeddings.astype("float32")
        faiss.normalize_L2(embeddings)  # crucial for cosine

        with self.lock:
            self.index = faiss.IndexFlatIP(self.dimension)  # reset
            self.index.add(embeddings)
            self.id_to_meta = new_meta
            self._save_index()
        print("✅ Embeddings created successfully!")

    async def update_file(self, _file_path: Path) -> None:
        """Simplest correct behavior: rebuild everything."""
        await self.build_index()

    def _get_project_files(self) -> List[Path]:
        files: List[Path] = []
        default_ignore_dirs = {
            ".git", ".svn", ".hg", "node_modules", "__pycache__",
            ".pytest_cache", ".mypy_cache", "venv", ".venv", "env", ".env",
            "build", "dist", ".embeddings", ".vscode", ".idea", "site-packages",
            ".tox", ".coverage", "htmlcov", ".egg-info", ".eggs"
        }
        for p in self.project_path.rglob("*"):
            if p.is_dir():
                continue
            if any(part in default_ignore_dirs for part in p.parts):
                continue
            if self._should_ignore(p):
                continue
            if p.suffix.lower() not in self.supported_extensions:
                continue
            files.append(p)
        return sorted(files)


    def search(self, query: Optional[str] = None, negative_query: Optional[str] = None, limit: int = 1000) -> List[Tuple[int, float]]:
        """Return list of (doc_id, score) with optional negative prompting.

        Scoring (single-pass, normalized):
        - Positive only:  p' = (cos_pos + 1) / 2
        - Negative only:  search with -neg_q, s = (cos_opp + 1) / 2
        - Both:           s = p' * (1 - n'), where n' = (cos_neg + 1) / 2 computed on the same ids
        """
        if not query and not negative_query:
            raise ValueError("Must provide either query or negative_query")

        with self.lock:
            if self.index.ntotal == 0:
                return []
            k = min(max(1, limit), self.index.ntotal)

        # Encode queries
        q: Optional[np.ndarray] = None
        if query:
            q = self.model.encode([query], show_progress_bar=False, batch_size=1).astype("float32")
            faiss.normalize_L2(q)

        neg_q: Optional[np.ndarray] = None
        if negative_query:
            neg_q = self.model.encode([negative_query], show_progress_bar=False, batch_size=1).astype("float32")
            faiss.normalize_L2(neg_q)

        # Positive-only or combined: get positive candidates first
        ids: np.ndarray
        pos_scores_norm: Optional[np.ndarray] = None
        if q is not None:
            with self.lock:
                pos_scores, pos_indices = self.index.search(q, k)
            ids = pos_indices[0]
            # Normalize cosine to [0,1]
            pos_scores_norm = (pos_scores[0] + 1.0) / 2.0
        else:
            ids = np.empty((0,), dtype=np.int64)

        results: List[Tuple[int, float]] = []

        if q is not None and neg_q is None:
            # Positive-only
            for did, s in zip(ids, pos_scores_norm if pos_scores_norm is not None else []):
                if 0 <= int(did) < len(self.id_to_meta):
                    results.append((int(did), float(s)))

        elif q is not None and neg_q is not None:
            # Combined: compute negative cosine for the same ids, then product
            neg_scores_norm_for_ids: List[float] = []
            with self.lock:
                for did in ids:
                    try:
                        vec = self.index.reconstruct(int(did))  # stored L2-normalized
                    except Exception:
                        # Fallback: skip if reconstruction fails
                        neg_scores_norm_for_ids.append(0.0)
                        continue
                    # cosine = dot(vec, neg_q[0]) since both normalized
                    cos_neg = float(np.dot(vec, neg_q[0]))
                    n_prime = (cos_neg + 1.0) / 2.0
                    neg_scores_norm_for_ids.append(n_prime)

            for did, p_prime, n_prime in zip(ids, pos_scores_norm if pos_scores_norm is not None else [], neg_scores_norm_for_ids):
                if 0 <= int(did) < len(self.id_to_meta):
                    s = float(p_prime * (1.0 - n_prime))
                    results.append((int(did), s))

        elif q is None and neg_q is not None:
            # Negative-only: search with the negated vector to get least-similar to negative
            negated = -neg_q
            with self.lock:
                opp_scores, opp_indices = self.index.search(negated, k)
            for did, cos_opp in zip(opp_indices[0], opp_scores[0]):
                if 0 <= int(did) < len(self.id_to_meta):
                    s = float((cos_opp + 1.0) / 2.0)
                    results.append((int(did), s))

        # Sort globally by score descending
        results.sort(key=lambda x: x[1], reverse=True)
        return results



class EmbeddingsSearch:
    """Uses ML algorithms for time series segmentation of code hits."""

    # ML algorithm parameters
    CONTEXT_WINDOW = 3             # Context around segments
    SEARCH_LIMIT = 1000            # Max candidates to process
    DEFAULT_TOP_N = 20             # Default number of results
    
    # DBSCAN clustering parameters (sensitivity controls)
    EPS = 1.33                     # Max distance between points (higher = less sensitive)
    MIN_SAMPLES = 1                # Min points to form cluster (higher = less sensitive)
    
    def __init__(self, indexer: EmbeddingsIndexer, eps: Optional[float] = None, min_samples: Optional[int] = None):
        self.indexer = indexer
        if eps is not None:
            self.EPS = eps
        if min_samples is not None:
            self.MIN_SAMPLES = min_samples

    def search(self, query: Optional[str] = None, negative_query: Optional[str] = None, top_n: Optional[int] = None) -> List[CodeSection]:
        if top_n is None:
            top_n = self.DEFAULT_TOP_N
        raw = self.indexer.search(query, negative_query, limit=self.SEARCH_LIMIT)
        if not raw:
            return []

        # Group hits by file (like grouping audio by track)
        file_results: Dict[str, Dict[int, float]] = {}
        for doc_id, score in raw:
            file_path, line_num = self.indexer.id_to_meta[doc_id]
            d = file_results.setdefault(file_path, {})
            prev = d.get(line_num)
            if prev is None or score > prev:
                d[line_num] = score

        # Group segments by file and sort files by best score
        file_segments: Dict[str, List[CodeSection]] = {}
        for file_path, line_to_score in file_results.items():
            sorted_hits = sorted(line_to_score.items(), key=lambda x: x[0])
            segments = self._segment_file(file_path, sorted_hits)
            if segments:
                file_segments[file_path] = segments
        
        # Sort files by their best segment score
        sorted_files = sorted(file_segments.keys(), 
                            key=lambda f: max(s.max_similarity for s in file_segments[f]), 
                            reverse=True)
        
        # Return segments in file order, maintaining natural order within each file
        all_segments = []
        for file_path in sorted_files:
            # Filter segments by similarity threshold
            good_segments = file_segments[file_path]
            all_segments.extend(good_segments)
        
        # Sort all segments by similarity and return top_n
        all_segments.sort(key=lambda s: s.max_similarity, reverse=True)
        return all_segments[:top_n]

    def set_sensitivity(self, eps: Optional[float] = None, min_samples: Optional[int] = None):
        """Adjust clustering sensitivity parameters."""
        if eps is not None:
            self.EPS = eps
        if min_samples is not None:
            self.MIN_SAMPLES = min_samples

    def _segment_file(self, file_path: str, line_scores: List[Tuple[int, float]]) -> List[CodeSection]:
        """DBSCAN clustering with blank line adjustment."""
        if not line_scores:
            return []
        
        # Adjust EPS for blank lines - increase tolerance
        adjusted_eps = self.EPS * 1.5  # More tolerant of gaps
        
        line_numbers = np.array([[line_num] for line_num, _ in line_scores])
        clustering = DBSCAN(eps=adjusted_eps, min_samples=self.MIN_SAMPLES)
        labels = clustering.fit_predict(line_numbers)
        
        sections = []
        for label in set(labels):
            if label == -1:
                continue
            cluster_mask = labels == label
            cluster_lines = line_numbers[cluster_mask].flatten()
            
            start, end = int(cluster_lines.min()), int(cluster_lines.max())
            ctx_start = max(1, start - self.CONTEXT_WINDOW)
            ctx_end = end + self.CONTEXT_WINDOW
            
            cluster_hits = [(line_num, score) for line_num, score in line_scores 
                           if start <= line_num <= end]
            
            section = self._create_section_from_span(file_path, ctx_start, ctx_end, cluster_hits)
            sections.append(section)
        
        return sections

    def _create_section_from_span(
        self,
        file_path: str,
        start_line: int,
        end_line: int,
        hit_scores: List[Tuple[int, float]],
    ) -> CodeSection:
        full = self.indexer.project_path / file_path
        with open(full, 'r', encoding='utf-8') as f:
            file_lines = f.readlines()
        max_line = len(file_lines)
        start = max(1, start_line)
        end = min(max_line, end_line)
        lines = [file_lines[i - 1].rstrip('\n') for i in range(start, end + 1)]
        scores = [score for ln, score in hit_scores if start <= ln <= end]
        avg = float(np.mean(scores)) if scores else 0.0
        max_score = float(np.max(scores)) if scores else 0.0
        return CodeSection(file_path=file_path, start_line=start, end_line=end, lines=lines, avg_similarity=avg, max_similarity=max_score)


class FileWatcher:
    """Watches for file changes and triggers index updates."""

    def __init__(self, project_path: Path, indexer: EmbeddingsIndexer):
        self.project_path = project_path
        self.indexer = indexer
        self.observer = Observer()
        self.handler = FileChangeHandler(self)
        self.running = False
        self.loop: Optional[asyncio.AbstractEventLoop] = None

    async def start(self) -> None:
        self.loop = asyncio.get_running_loop()
        self.observer.schedule(self.handler, str(self.project_path), recursive=True)
        self.observer.start()
        self.running = True
        print("File watcher started")

    async def stop(self) -> None:
        self.running = False
        self.observer.stop()
        self.observer.join()

    async def handle_file_change(self, file_path: Path) -> None:
        if file_path.suffix.lower() not in self.indexer.supported_extensions:
            return
        try:
            await self.indexer.update_file(file_path)
            rel = file_path.relative_to(self.project_path)
            print(f"Updated embeddings for: {rel}")
        except Exception as e:
            print(f"Error updating embeddings for {file_path}: {e}")


class FileChangeHandler(FileSystemEventHandler):
    """Batch and debounce file system events, then schedule async updates."""

    def __init__(self, watcher: FileWatcher):
        self.watcher = watcher
        self.pending_updates: Set[Path] = set()
        self.last_update_time = 0.0
        self.update_thread: Optional[threading.Thread] = None

    def on_modified(self, event):
        if not event.is_directory:
            self.pending_updates.add(Path(event.src_path))
            self._schedule_update()

    def on_created(self, event):
        if not event.is_directory:
            self.pending_updates.add(Path(event.src_path))
            self._schedule_update()

    def _schedule_update(self):
        self.last_update_time = time.time()
        if self.update_thread is None or not self.update_thread.is_alive():
            self.update_thread = threading.Thread(target=self._process_updates_thread, daemon=True)
            self.update_thread.start()

    def _process_updates_thread(self):
        # Simple debounce: wait ~1s after last event
        while True:
            time.sleep(1.0)
            if time.time() - self.last_update_time >= 1.0:
                break
        if not self.watcher.running:
            return

        files_to_update = list(self.pending_updates)
        self.pending_updates.clear()

        for file_path in files_to_update:
            try:
                rel = None
                try:
                    rel = file_path.relative_to(self.watcher.project_path)
                except Exception:
                    pass
                print(f"File changed: {rel or file_path}")
                if self.watcher.loop and self.watcher.running:
                    asyncio.run_coroutine_threadsafe(
                        self.watcher.handle_file_change(file_path),
                        self.watcher.loop,
                    )
            except Exception as e:
                print(f"Error scheduling update for {file_path}: {e}")



class EmbeddingsSuite:
    def __init__(self, project_path: str, supported_extensions: Optional[Set[str]] = None, ignore_file: Optional[str] = None, model: str = "all-MiniLM-L6-v2"):
        self.project_path = Path(project_path)
        self.indexer = EmbeddingsIndexer(self.project_path, model, supported_extensions, ignore_file)
        self.search = EmbeddingsSearch(self.indexer)
        self.watcher = FileWatcher(self.project_path, self.indexer)

    async def build_initial_index(self):
        await self.indexer.build_index()

    async def start_watching(self):
        await self.watcher.start()

    async def stop_watching(self):
        await self.watcher.stop()

    def search_code(self, query: Optional[str] = None, negative_query: Optional[str] = None, top_n: int = 10) -> List[CodeSection]:
        return self.search.search(query, negative_query, top_n)

    def get_stats(self) -> Dict[str, int]:
        # derive stats from id_to_meta
        with self.indexer.lock:
            total_lines = len(self.indexer.id_to_meta)
            total_files = len({fp for fp, _ in self.indexer.id_to_meta})
            index_size = int(self.indexer.index.ntotal)
        return {"total_files": total_files, "total_lines": total_lines, "index_size": index_size}


if __name__ == "__main__":
    print("This module is intended for use as a Python library. Import and use Embeddings/EmbeddingsSuite from your code.")

