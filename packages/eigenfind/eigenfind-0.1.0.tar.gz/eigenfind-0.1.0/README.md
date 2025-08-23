# 📌 About `eigenfind`

**`eigenfind`** is a lightweight Python library that allows you to compute **eigenvectors from known eigenvalues** of a square matrix — a task commonly needed in theoretical mathematics, linear algebra education, and symbolic or numerical analysis.

While most libraries like NumPy and SciPy compute eigenvalues and eigenvectors together, `eigenfind` fills a specific niche: solving the **eigenvalue problem in reverse** — finding eigenvectors **when you already know one or more eigenvalues**.

This is achieved by solving the homogeneous linear system:

$$
(A - \lambda I)\mathbf{v} = 0
$$

…which defines the eigenspace for a given eigenvalue `λ` of matrix `A`.

---

## ✅ Key Features

* 🔍 Find eigenvectors corresponding to a **given eigenvalue**
* 📐 Works with both **numeric** (NumPy/SciPy) and **symbolic** (SymPy) matrices
* 📚 Educational use: ideal for students, educators, and math enthusiasts
* 🧠 Supports defective matrices (partial functionality)
* 🧪 Easy to test and integrate into other math tools

---

## 🚧 Use Cases

* Teaching or learning linear algebra
* Verifying results from numerical solvers
* Debugging or inspecting eigenvalue computations
* Symbolic math derivations
* Building introspection tools for PCA or matrix decompositions
