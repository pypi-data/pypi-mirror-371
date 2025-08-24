# src/geneuler/mesh.py
from __future__ import annotations

import os
import warnings
from dataclasses import dataclass
from typing import Dict, Tuple, Optional, List, Sequence, Union

import numpy as np
import gmsh
import meshio
from collections import Counter

# Default units: millimeters
DEFAULT_BBOX = {"x": (-50.0, 50.0), "y": (0.0, 130.0), "z": (-130.0, 130.0)}

@dataclass
class Mesh:
    points: np.ndarray                # (N, 3) float
    tets: np.ndarray                  # (M, 4) int (can be empty)
    tris: Optional[np.ndarray] = None # (K, 3) int (outer surface triangles, optional)

    # ---------- Read existing .msh ----------
    @classmethod
    def from_msh(cls, path: str) -> "Mesh":
        m = meshio.read(path)
        pts = np.asarray(m.points, dtype=float)
        tets = _cells_of_type(m, "tetra")
        tris = _cells_of_type(m, "triangle")
        if tets.size == 0 and (tris is None or tris.size == 0):
            raise ValueError(f"No cells found in {path}")
        return cls(points=pts, tets=tets, tris=(tris if tris.size else None))

    # ---------- Generate from bounding box (free h) ----------
    @classmethod
    def from_bbox(
        cls,
        bbox: Dict[str, Tuple[float, float]] | tuple | list = DEFAULT_BBOX,
        *,
        h: float = 4.0,
        refine_ball_center: Optional[Tuple[float, float, float]] = None,
        refine_ball_radius: float = 15.0,
        refine_factor: float = 0.25,
        msh_path: Optional[str] = "out/box.msh",
    ) -> "Mesh":
        if h <= 0:
            raise ValueError("h must be positive.")
        bbox = _normalize_bbox(bbox)

        _gmsh_init()
        gmsh.option.setNumber("Mesh.MshFileVersion", 2.2)
        gmsh.option.setNumber("Mesh.Binary", 0)
        gmsh.option.setNumber("General.Terminal", 1)

        gmsh.model.add("box")
        x0, x1 = bbox["x"]; y0, y1 = bbox["y"]; z0, z1 = bbox["z"]

        def P(x, y, z): return gmsh.model.geo.addPoint(x, y, z, h)
        p000 = P(x0, y0, z0); p100 = P(x1, y0, z0); p110 = P(x1, y1, z0); p010 = P(x0, y1, z0)
        p001 = P(x0, y0, z1); p101 = P(x1, y0, z1); p111 = P(x1, y1, z1); p011 = P(x0, y1, z1)

        def L(a, b): return gmsh.model.geo.addLine(a, b)
        l = []
        l += [L(p000, p100), L(p100, p110), L(p110, p010), L(p010, p000)]
        l += [L(p001, p101), L(p101, p111), L(p111, p011), L(p011, p001)]
        l += [L(p000, p001), L(p100, p101), L(p110, p111), L(p010, p011)]

        def loop(ids): return gmsh.model.geo.addCurveLoop(ids)
        faces = [
            loop([l[0],  l[9],  -l[4],  -l[8]]),
            loop([l[1],  l[10], -l[5],  -l[9]]),
            loop([l[2],  l[11], -l[6],  -l[10]]),
            loop([l[3],  l[8],  -l[7],  -l[11]]),
            loop([l[0],  l[1],  l[2],   l[3]]),
            loop([l[4],  l[5],  l[6],   l[7]]),
        ]
        surf = [gmsh.model.geo.addPlaneSurface([f]) for f in faces]
        sl = gmsh.model.geo.addSurfaceLoop(surf)
        gmsh.model.geo.addVolume([sl])
        gmsh.model.geo.synchronize()

        if refine_ball_center is not None:
            cx, cy, cz = refine_ball_center
            gmsh.model.mesh.field.add("Ball", 1)
            gmsh.model.mesh.field.setNumber(1, "XCenter", cx)
            gmsh.model.mesh.field.setNumber(1, "YCenter", cy)
            gmsh.model.mesh.field.setNumber(1, "ZCenter", cz)
            gmsh.model.mesh.field.setNumber(1, "Radius", refine_ball_radius)
            gmsh.model.mesh.field.setNumber(1, "VIn",   max(h * refine_factor, 1e-6))
            gmsh.model.mesh.field.setNumber(1, "VOut",  h)
            gmsh.model.mesh.field.setAsBackgroundMesh(1)

        gmsh.model.mesh.generate(3)

        _, node_coords, _ = gmsh.model.mesh.getNodes()
        pts_arr = np.array(node_coords, dtype=float).reshape(-1, 3)

        et3, _, en3 = gmsh.model.mesh.getElements(dim=3)
        tets = np.empty((0, 4), dtype=np.int64)
        if 4 in et3:
            tetra_block = list(et3).index(4)
            tets = np.array(en3[tetra_block], dtype=np.int64).reshape(-1, 4) - 1

        tris_arr = None
        et2, _, en2 = gmsh.model.mesh.getElements(dim=2)
        if 2 in et2:
            tri_block = list(et2).index(2)
            tris_arr = np.array(en2[tri_block], dtype=np.int64).reshape(-1, 3) - 1

        _gmsh_finalize()

        mesh_obj = cls(points=pts_arr, tets=tets, tris=tris_arr)
        if msh_path:
            mesh_obj.save_msh(msh_path)
        return mesh_obj

    # ---------- Import OBJ/STL/STEP and build shell/volume (robust) ----------
    @classmethod
    def from_surface(
        cls,
        path: str,
        *,
        h: float = 4.0,
        reconstruct_volume: bool = True,
        angle_deg: float = 40.0,
        include_boundary: bool = True,
        force_parametrization: bool = False,
        curve_angle_deg: float = 180.0,
        msh_path: Optional[str] = "out/surface.msh",
        allow_shell_fallback: bool = True,
    ) -> "Mesh":
        if h <= 0:
            raise ValueError("h must be positive.")
        ext = os.path.splitext(path)[1].lower()
    
        _gmsh_init()
        gmsh.option.setNumber("Mesh.MshFileVersion", 2.2)
        gmsh.option.setNumber("Mesh.Binary", 0)
        gmsh.option.setNumber("General.Terminal", 1)
        gmsh.option.setNumber("Mesh.CharacteristicLengthMin", float(h))
        gmsh.option.setNumber("Mesh.CharacteristicLengthMax", float(h))
        gmsh.model.add("import")
    
        def _collect() -> tuple[np.ndarray, Optional[np.ndarray], np.ndarray]:
            _, node_coords, _ = gmsh.model.mesh.getNodes()
            pts = np.array(node_coords, dtype=float).reshape(-1, 3)
    
            tris = None
            et2, _, en2 = gmsh.model.mesh.getElements(dim=2)
            if 2 in et2:
                tri_block = list(et2).index(2)
                tris = np.array(en2[tri_block], dtype=np.int64).reshape(-1, 3) - 1
    
            tets = np.empty((0, 4), dtype=np.int64)
            et3, _, en3 = gmsh.model.mesh.getElements(dim=3)
            if 4 in et3:
                tet_block = list(et3).index(4)
                tets = np.array(en3[tet_block], dtype=np.int64).reshape(-1, 4) - 1
            return pts, tris, tets
    
        def _mesh_2d_or_raise():
            gmsh.model.mesh.generate(2)
            et2, _, _ = gmsh.model.mesh.getElements(dim=2)
            if 2 not in et2:
                raise RuntimeError("No 2D elements produced on surfaces.")
    
        def _parametrize_or_raise(a_deg, include_b, force_param, c_deg):
            gmsh.model.mesh.classifySurfaces(
                np.deg2rad(a_deg), include_b, force_param, np.deg2rad(c_deg),
            )
            gmsh.model.mesh.createGeometry()
            gmsh.model.geo.synchronize()
    
        try:
            if ext in [".stl", ".obj", ".ply"]:
                # --- Preflight: skip volume path for non-watertight shells ---
                info = _preflight_watertight(path)
                if reconstruct_volume and not _is_watertight(info):
                    import warnings
                    warnings.warn(
                        f"Input is not watertight (boundary_edges={info and info.get('boundary_edges')}, "
                        f"nonmanifold_edges={info and info.get('nonmanifold_edges')}). "
                        "Skipping parametrization/volume; meshing shell only."
                    )
                    gmsh.merge(path)
                    try: gmsh.model.mesh.removeDuplicateNodes()
                    except Exception: pass
                    try: gmsh.model.mesh.removeDuplicateElements()
                    except Exception: pass
                    gmsh.model.mesh.generate(2)
                    pts_arr, tris_arr, tets = _collect()
                    mesh_obj = cls(points=pts_arr, tets=tets, tris=tris_arr)
                    if msh_path: mesh_obj.save_msh(msh_path)
                    return mesh_obj
    
                # Otherwise proceed with your robust pipeline (as you already had):
                gmsh.merge(path)
                try: gmsh.model.mesh.removeDuplicateNodes()
                except Exception: pass
                try: gmsh.model.mesh.removeDuplicateElements()
                except Exception: pass
    
                try:
                    _parametrize_or_raise(angle_deg, include_boundary, force_parametrization, curve_angle_deg)
                except Exception as e1:
                    if not allow_shell_fallback:
                        raise
                    import warnings
                    warnings.warn(
                        f"Parametrization failed ({e1}). Retrying with include_boundary=False, "
                        "force_parametrization=True and larger angle."
                    )
                    gmsh.clear()
                    _gmsh_finalize()
                    _gmsh_init()
                    gmsh.option.setNumber("Mesh.MshFileVersion", 2.2)
                    gmsh.option.setNumber("Mesh.Binary", 0)
                    gmsh.option.setNumber("General.Terminal", 1)
                    gmsh.option.setNumber("Mesh.CharacteristicLengthMin", float(h))
                    gmsh.option.setNumber("Mesh.CharacteristicLengthMax", float(h))
                    gmsh.model.add("import_retry")
                    gmsh.merge(path)
                    try: gmsh.model.mesh.removeDuplicateNodes()
                    except Exception: pass
                    try: gmsh.model.mesh.removeDuplicateElements()
                    except Exception: pass
                    try:
                        _parametrize_or_raise(max(angle_deg, 75.0), False, True, 180.0)
                    except Exception as e2:
                        warnings.warn(
                            f"Parametrization still failed ({e2}). Falling back to shell-only meshing."
                        )
                        gmsh.clear()
                        _gmsh_finalize()
                        _gmsh_init()
                        gmsh.option.setNumber("Mesh.MshFileVersion", 2.2)
                        gmsh.option.setNumber("Mesh.Binary", 0)
                        gmsh.option.setNumber("General.Terminal", 1)
                        gmsh.option.setNumber("Mesh.CharacteristicLengthMin", float(h))
                        gmsh.option.setNumber("Mesh.CharacteristicLengthMax", float(h))
                        gmsh.model.add("direct_shell")
                        gmsh.merge(path)
                        try: gmsh.model.mesh.removeDuplicateNodes()
                        except Exception: pass
                        try: gmsh.model.mesh.removeDuplicateElements()
                        except Exception: pass
                        gmsh.model.mesh.generate(2)
                        pts_arr, tris_arr, tets = _collect()
                        mesh_obj = cls(points=pts_arr, tets=tets, tris=tris_arr)
                        if msh_path: mesh_obj.save_msh(msh_path)
                        return mesh_obj
    
                # Parametrization ok → try volume or shell:
                if reconstruct_volume:
                    try:
                        surfs = gmsh.model.getEntities(2)
                        if not surfs:
                            raise RuntimeError("No surfaces detected after classification.")
                        sl = gmsh.model.geo.addSurfaceLoop([s[1] for s in surfs])
                        gmsh.model.geo.addVolume([sl])
                        gmsh.model.geo.synchronize()
                        gmsh.model.mesh.generate(3)
                    except Exception as e3:
                        import warnings
                        warnings.warn(f"Volume meshing failed ({e3}). Returning shell-only instead.")
                        gmsh.model.mesh.generate(2)
                else:
                    _mesh_2d_or_raise()
    
            elif ext in [".step", ".stp", ".iges", ".igs"]:
                gmsh.model.occ.importShapes(path)
                gmsh.model.occ.synchronize()
                vols = gmsh.model.getEntities(3)
                if reconstruct_volume and vols:
                    gmsh.model.mesh.generate(3)
                else:
                    gmsh.model.mesh.generate(2)
    
            else:
                raise ValueError(
                    f"Unsupported extension '{ext}'. Use .obj, .stl, .ply, .step/.stp, .iges/.igs"
                )
    
            pts_arr, tris_arr, tets = _collect()
        finally:
            _gmsh_finalize()
    
        mesh_obj = cls(points=pts_arr, tets=tets, tris=tris_arr)
        if msh_path:
            mesh_obj.save_msh(msh_path)
        return mesh_obj


    # ---------- Saving ----------
    def save_msh(self, path: str) -> None:
        cells: List[tuple] = []
        if self.tets is not None and self.tets.size:
            cells.append(("tetra", self.tets))
        if self.tris is not None and self.tris.size:
            cells.append(("triangle", self.tris))
        if not cells:
            raise ValueError("No cells to write (no triangles or tetrahedra).")
        m = meshio.Mesh(self.points, cells)
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        meshio.write(path, m)

    def save_xdmf(self, path_without_ext: str) -> tuple[str, str]:
        xdmf_path = f"{path_without_ext}.xdmf"
        cells: List[tuple] = []
        if self.tets is not None and self.tets.size:
            cells.append(("tetra", self.tets))
        if self.tris is not None and self.tris.size:
            cells.append(("triangle", self.tris))
        if not cells:
            raise ValueError("No cells to write (no triangles or tetrahedra).")
        m = meshio.Mesh(self.points, cells)

        os.makedirs(os.path.dirname(xdmf_path) or ".", exist_ok=True)
        meshio.write(xdmf_path, m)
        h5_path = xdmf_path.replace(".xdmf", ".h5")
        return xdmf_path, (h5_path if os.path.exists(h5_path) else "")

    # ---------- Boundary helpers ----------
    def boundary_nodes(self, bbox: Dict[str, Tuple[float, float]] = DEFAULT_BBOX, tol=1e-6) -> np.ndarray:
        x0, x1 = bbox["x"]; y0, y1 = bbox["y"]; z0, z1 = bbox["z"]
        x = self.points[:, 0]; y = self.points[:, 1]; z = self.points[:, 2]
        mask = (
            np.isclose(x, x0, atol=tol) | np.isclose(x, x1, atol=tol) |
            np.isclose(y, y0, atol=tol) | np.isclose(y, y1, atol=tol) |
            np.isclose(z, z0, atol=tol) | np.isclose(z, z1, atol=tol)
        )
        return np.where(mask)[0]

    def floor_nodes(self, y: Optional[float] = 0.0, tol: float = 1e-6) -> np.ndarray:
        Y = self.points[:, 1]
        if y is not None:
            return np.where(np.isclose(Y, float(y), atol=tol))[0]
        y_min = float(np.min(Y))
        return np.where(np.isclose(Y, y_min, atol=max(tol, 1e-6)))[0]

    def attachment_nodes(
        self,
        attachments: Optional[
            Sequence[Union[Tuple[Tuple[float, float, float], float], Tuple[float, float, float]]]
        ] = None,
        *,
        default_radius: float = 5.0,
        return_groups: bool = False,
    ):
        if not attachments:
            return np.array([], dtype=int) if not return_groups else {}
        groups: Dict[int, np.ndarray] = {}
        P = self.points
        for i, item in enumerate(attachments):
            if isinstance(item, (list, tuple)) and len(item) == 2 and isinstance(item[1], (int, float)):
                center, rad = item
            else:
                center, rad = item, default_radius
            c = np.asarray(center, dtype=float).reshape(1, 3)
            d = np.linalg.norm(P - c, axis=1)
            groups[i] = np.where(d <= float(rad))[0]
        return groups if return_groups else (np.unique(np.concatenate(list(groups.values()))) if groups else np.array([], dtype=int))


# ---------- helpers ----------
def _cells_of_type(m: meshio.Mesh, name: str) -> np.ndarray:
    blocks = [c.data for c in m.cells if c.type == name]
    if not blocks:
        return np.empty((0, 4 if name == "tetra" else 3), dtype=int)
    return np.concatenate(blocks, axis=0)

def _normalize_bbox(bbox):
    if isinstance(bbox, (list, tuple)) and len(bbox) == 6:
        x0, x1, y0, y1, z0, z1 = map(float, bbox)
        return {"x": (x0, x1), "y": (y0, y1), "z": (z0, z1)}
    return {
        "x": (float(bbox["x"][0]), float(bbox["x"][1])),
        "y": (float(bbox["y"][0]), float(bbox["y"][1])),
        "z": (float(bbox["z"][0]), float(bbox["z"][1])),
    }

_gmsh_initialized = False
def _gmsh_init():
    global _gmsh_initialized
    if not _gmsh_initialized:
        try:
            gmsh.initialize()
        except Exception as e:
            if "signal only works in main thread" not in str(e):
                raise
        _gmsh_initialized = True

def _gmsh_finalize():
    global _gmsh_initialized
    if _gmsh_initialized:
        try:
            gmsh.finalize()
        finally:
            _gmsh_initialized = False

def _preflight_watertight(path: str) -> Optional[dict]:
    """
    Quick watertight check using meshio.
    Returns dict with 'boundary_edges' and 'nonmanifold_edges' (or None if not checkable).
    """
    try:
        m = meshio.read(path)
        tris_blocks = [c.data for c in m.cells if c.type in ("triangle", "tri")]
        if not tris_blocks:
            return None  # can’t tell (e.g., STEP)
        F = np.ascontiguousarray(np.vstack(tris_blocks))
        # Build undirected edges
        E = np.vstack([F[:, [0, 1]], F[:, [1, 2]], F[:, [2, 0]]])
        E = np.sort(E, axis=1)
        counts = Counter(map(tuple, E))
        boundary = sum(1 for k, v in counts.items() if v == 1)
        nonmanifold = sum(1 for k, v in counts.items() if v > 2)
        return {"boundary_edges": boundary, "nonmanifold_edges": nonmanifold}
    except Exception:
        return None

def _is_watertight(info: Optional[dict]) -> bool:
    return bool(info) and info.get("boundary_edges", 1) == 0 and info.get("nonmanifold_edges", 1) == 0
