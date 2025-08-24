from __future__ import annotations
import numpy as np
import ufl
from mpi4py import MPI
from petsc4py import PETSc
from dolfinx import mesh as dmesh, fem
from dolfinx.io import XDMFFile

class Fem:
    """
    Minimal linear elasticity on a tetra mesh.
    - Load mesh from XDMF
    - Tag boundaries geometrically (floor, outer shell) or consume provided meshtags
    - Apply Dirichlet on floor; traction on attachment
    - Solve, write results
    """
    def __init__(self, xdmf_mesh_path: str):
        self.comm = MPI.COMM_WORLD
        with XDMFFile(self.comm, xdmf_mesh_path, "r") as xdmf:
            self.mesh = xdmf.read_mesh(name="mesh")

        # function space (vector, 3 dof/node)
        self.V = fem.functionspace(self.mesh, ("CG", 1, (3,)))

        # defaults
        self._floor_atol = 1e-10
        self._attachment_pts = []
        self._attachment_radius = 0.01
        self._traction = np.array([0.0, 0.0, 0.0])
        self._E = 210e9
        self._nu = 0.30

    # -------- configuration --------
    def set_material(self, E: float, nu: float = 0.30):
        self._E, self._nu = float(E), float(nu)

    def set_floor_tolerance(self, atol: float):
        self._floor_atol = float(atol)

    def set_attachment(self, points, radius: float, traction_vector):
        self._attachment_pts = [np.asarray(p, float) for p in points]
        self._attachment_radius = float(radius)
        self._traction = np.asarray(traction_vector, float)

    # -------- boundary helpers --------
    def _locate_floor_facets(self):
        y = self.mesh.geometry.x[:,1]
        y_min = float(y.min())
        return dmesh.locate_entities_boundary(
            self.mesh, self.mesh.topology.dim - 1,
            lambda X: np.isclose(X[1], y_min, atol=self._floor_atol)
        )

    def _locate_attachment_facets(self):
        pts = np.stack(self._attachment_pts) if self._attachment_pts else None
        r = self._attachment_radius
        if pts is None:
            return np.array([], dtype=np.int32)

        def is_attach(X):
            # X is (3, num_points) array
            P = X.T  # (N,3)
            for q in pts:
                if np.any(np.sum((P - q)**2, axis=1) <= r*r):
                    return True
            return False

        return dmesh.locate_entities_boundary(
            self.mesh, self.mesh.topology.dim - 1, is_attach
        )

    # -------- solve --------
    def run(self, results_stem: str = "results") -> dict:
        # Mark facets
        floor_facets = self._locate_floor_facets()
        attach_facets = self._locate_attachment_facets()

        # Meshtags for ds
        all_facets = np.concatenate([floor_facets, attach_facets]).astype(np.int32)
        if all_facets.size == 0:
            raise RuntimeError("No boundary facets located (floor/attachment).")
        tags = np.concatenate([np.full(len(floor_facets), 1, dtype=np.int32),
                               np.full(len(attach_facets), 2, dtype=np.int32)])
        mt = dmesh.meshtags(self.mesh, self.mesh.topology.dim - 1, all_facets, tags)

        # Elasticity
        E, nu = self._E, self._nu
        mu = E/(2*(1+nu))
        lmbda = E*nu/((1+nu)*(1-2*nu))
        def eps(u): return ufl.sym(ufl.grad(u))
        def sig(u): return lmbda*ufl.tr(eps(u))*ufl.Identity(3) + 2*mu*eps(u)

        u = ufl.TrialFunction(self.V)
        v = ufl.TestFunction(self.V)
        a = ufl.inner(sig(u), eps(v))*ufl.dx

        ds = ufl.Measure("ds", domain=self.mesh, subdomain_data=mt)
        traction = fem.Constant(self.mesh, self._traction)
        L = ufl.dot(traction, v)*ds(2)  # apply only on attachment facets

        # Dirichlet on floor: u = 0
        u0 = fem.Constant(self.mesh, np.array([0.0, 0.0, 0.0], dtype=np.float64))
        floor_dofs = fem.locate_dofs_topological(self.V, self.mesh.topology.dim - 1, floor_facets)
        bc_floor = fem.dirichletbc(u0, floor_dofs, self.V)

        # Assemble
        A = fem.petsc.assemble_matrix(fem.form(a), bcs=[bc_floor]); A.assemble()
        b = fem.petsc.assemble_vector(fem.form(L)); fem.petsc.apply_lifting(b, [fem.form(a)], bcs=[[bc_floor]])
        b.ghostUpdate(addv=PETSc.InsertMode.ADD_VALUES, mode=PETSc.ScatterMode.REVERSE)
        fem.petsc.set_bc(b, [bc_floor])

        # Solve
        ksp = PETSc.KSP().create(self.comm)
        ksp.setOperators(A)
        ksp.setType("cg")
        ksp.getPC().setType("hypre")
        ksp.setTolerances(rtol=1e-8, max_it=2000)
        ksp.setFromOptions()

        x = A.createVecRight()
        ksp.solve(b, x)

        u_h = fem.Function(self.V)
        u_h.x.array[:] = x.getArray(readonly=True)

        # Write results
        with XDMFFile(self.comm, f"{results_stem}.xdmf", "w") as xf:
            xf.write_mesh(self.mesh)
            xf.write_function(u_h, 0.0)

        return {
            "xdmf": f"{results_stem}.xdmf",
            "max_disp": float(np.abs(u_h.x.array).max()),
            "iters": int(ksp.getIterationNumber()),
            "converged": bool(ksp.getConvergedReason() > 0),
        }
