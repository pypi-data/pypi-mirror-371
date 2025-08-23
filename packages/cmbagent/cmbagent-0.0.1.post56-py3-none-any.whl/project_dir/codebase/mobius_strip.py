# filename: codebase/mobius_strip.py
import os
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import datetime

def generate_mobius_strip(radius=1.0, half_width=0.4, num_u=400, num_v=80):
    """
    Generate the parametric coordinates of a Möbius strip.

    Parameters
    ----------
    radius : float
        Radius R of the central circle of the strip [arbitrary unit].
        This defines the major radius around which the strip winds.
    half_width : float
        Half-width w of the strip [arbitrary unit].
        The full width is 2 * w.
    num_u : int
        Number of samples along the angular direction u [dimensionless].
        u spans from 0 to 2*pi radians.
    num_v : int
        Number of samples along the width direction v [dimensionless].
        v spans from -w to +w.

    Returns
    -------
    X : numpy.ndarray
        2D array of x coordinates [arbitrary unit] with shape (num_v, num_u).
    Y : numpy.ndarray
        2D array of y coordinates [arbitrary unit] with shape (num_v, num_u).
    Z : numpy.ndarray
        2D array of z coordinates [arbitrary unit] with shape (num_v, num_u).
    U : numpy.ndarray
        2D array of the angular parameter u [radian] with shape (num_v, num_u).
        Useful for coloring or further analysis.
    V : numpy.ndarray
        2D array of the width parameter v [arbitrary unit] with shape (num_v, num_u).

    Notes
    -----
    The Möbius strip is parameterized by:
        x(u, v) = (R + v * cos(u/2)) * cos(u)
        y(u, v) = (R + v * cos(u/2)) * sin(u)
        z(u, v) = v * sin(u/2)

    with u in [0, 2*pi], v in [-w, w]. All geometric quantities are dimensionless
    or expressed in arbitrary units (a.u.), suitable for visualization.
    """
    # Parameters (units: a.u. for length, radians for angles)
    R = float(radius)
    w = float(half_width)
    nu = int(num_u)
    nv = int(num_v)

    # Parameter grids
    u = np.linspace(0.0, 2.0 * np.pi, nu, dtype=float)
    v = np.linspace(-w, w, nv, dtype=float)

    # Create meshgrid: U, V shapes are (nv, nu)
    U, V = np.meshgrid(u, v, indexing="xy")

    # Parametric equations of the Möbius strip (vectorized, no loops)
    cos_u = np.cos(U)
    sin_u = np.sin(U)
    cos_half_u = np.cos(0.5 * U)
    sin_half_u = np.sin(0.5 * U)

    radial = R + V * cos_half_u  # a.u.
    X = radial * cos_u           # a.u.
    Y = radial * sin_u           # a.u.
    Z = V * sin_half_u           # a.u.

    return X, Y, Z, U, V


def save_mobius_data(X, Y, Z, U, V, radius, half_width, num_u, num_v, timestamp, save_dir="data"):
    """
    Save Möbius strip data arrays and parameters to a compressed NPZ file.

    Parameters
    ----------
    X, Y, Z : numpy.ndarray
        2D arrays of coordinates [arbitrary unit], each of shape (num_v, num_u).
    U : numpy.ndarray
        2D array of angular parameter u [radian], shape (num_v, num_u).
    V : numpy.ndarray
        2D array of width parameter v [arbitrary unit], shape (num_v, num_u).
    radius : float
        Radius R [arbitrary unit].
    half_width : float
        Half-width w [arbitrary unit].
    num_u : int
        Number of u samples [dimensionless].
    num_v : int
        Number of v samples [dimensionless].
    timestamp : str
        Timestamp string used in filename.
    save_dir : str
        Directory to save the NPZ file.

    Returns
    -------
    data_path : str
        Full path to the saved NPZ file.

    Notes
    -----
    The saved file includes:
    - X, Y, Z coordinate arrays
    - U, V parameter grids
    - Parameters: radius, half_width, num_u, num_v
    All quantities for coordinates are in arbitrary units (a.u.), u is in radians.
    """
    if not os.path.isdir(save_dir):
        os.makedirs(save_dir, exist_ok=True)

    data_filename = "mobius_strip_data_1_" + timestamp + ".npz"
    data_path = os.path.join(save_dir, data_filename)
    np.savez(
        data_path,
        X=X,
        Y=Y,
        Z=Z,
        U=U,
        V=V,
        radius=float(radius),
        half_width=float(half_width),
        num_u=int(num_u),
        num_v=int(num_v)
    )
    return data_path


def plot_and_save_mobius(X, Y, Z, U, timestamp, save_dir="data"):
    """
    Create a 3D plot of the Möbius strip and save it as a high-resolution PNG.

    Parameters
    ----------
    X, Y, Z : numpy.ndarray
        2D arrays of coordinates [arbitrary unit], each of shape (num_v, num_u).
    U : numpy.ndarray
        2D array of angular parameter u [radian], used to color the surface.
    timestamp : str
        Timestamp string used in filename, to ensure uniqueness.
    save_dir : str
        Directory to save the plot file.

    Returns
    -------
    plot_path : str
        Full path to the saved PNG file.

    Notes
    -----
    - The plot uses a colormap based on u to show the twist.
    - Labels include units (a.u. for lengths).
    - Grid lines are enabled.
    - The plot is saved at 300 dpi.
    - LaTeX rendering is disabled to ensure compatibility.
    """
    if not os.path.isdir(save_dir):
        os.makedirs(save_dir, exist_ok=True)

    # Ensure LaTeX rendering is disabled
    mpl.rcParams["text.usetex"] = False

    # Normalize U for coloring (avoid divide-by-zero with tiny epsilon)
    u_min = np.min(U)
    u_max = np.max(U)
    denom = u_max - u_min
    if denom == 0.0:
        denom = 1.0  # fallback to avoid division by zero though it should not happen
    U_norm = (U - u_min) / denom
    colors = plt.cm.viridis(U_norm)

    # Create figure and 3D axis
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection="3d")

    # Plot the surface
    ax.plot_surface(
        X, Y, Z,
        rstride=1, cstride=1,
        facecolors=colors,
        linewidth=0,
        antialiased=True,
        shade=False
    )

    # Labels and title with units
    ax.set_title("Möbius strip", pad=14)
    ax.set_xlabel("x (a.u.)")
    ax.set_ylabel("y (a.u.)")
    ax.set_zlabel("z (a.u.)")
    ax.grid(True)

    # Set equal aspect ratio to avoid distortion
    x_min, x_max = np.min(X), np.max(X)
    y_min, y_max = np.min(Y), np.max(Y)
    z_min, z_max = np.min(Z), np.max(Z)
    ax.set_box_aspect((x_max - x_min, y_max - y_min, z_max - z_min))

    # Layout to avoid overlap
    plt.tight_layout()

    # Save high-resolution PNG
    plot_filename = "mobius_strip_1_" + timestamp + ".png"
    plot_path = os.path.join(save_dir, plot_filename)
    fig.savefig(plot_path, dpi=300, bbox_inches="tight")
    plt.close(fig)

    return plot_path


def main():
    """
    Main execution function to generate, save, and report on a 3D Möbius strip.

    Workflow
    --------
    1. Generate the Möbius strip coordinates using a vectorized parametric form.
    2. Save the underlying data (X, Y, Z, U, V, parameters) to an NPZ file.
    3. Plot the strip in 3D, color by u, and save a high-resolution PNG.
    4. Print concise details including file paths, parameter ranges, and extents.

    Units
    -----
    - Length-like quantities (X, Y, Z, radius, half_width, V) are in arbitrary units (a.u.).
    - Angular quantity U is in radians.
    - num_u and num_v are dimensionless sample counts.
    """
    # Configuration (all lengths in a.u., angles in radians)
    radius = 1.0      # a.u.
    half_width = 0.4  # a.u.
    num_u = 400       # samples along u
    num_v = 80        # samples along v

    # Single timestamp for consistent filenames
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    # Generate data
    X, Y, Z, U, V = generate_mobius_strip(
        radius=radius,
        half_width=half_width,
        num_u=num_u,
        num_v=num_v
    )

    # Save data
    data_dir = "data"
    data_path = save_mobius_data(
        X, Y, Z, U, V,
        radius=radius,
        half_width=half_width,
        num_u=num_u,
        num_v=num_v,
        timestamp=timestamp,
        save_dir=data_dir
    )

    # Plot and save
    plot_path = plot_and_save_mobius(
        X, Y, Z, U,
        timestamp=timestamp,
        save_dir=data_dir
    )

    # Compute extents for reporting
    x_min, x_max = np.min(X), np.max(X)
    y_min, y_max = np.min(Y), np.max(Y)
    z_min, z_max = np.min(Z), np.max(Z)

    # Print detailed, concise report
    print("Saved 3D Möbius strip plot to: " + plot_path)
    print("Saved Möbius data to: " + data_path)
    print("\nMöbius strip parameters and grid:")
    print("  Radius R (a.u.): " + str(radius))
    print("  Half-width w (a.u.): " + str(half_width))
    print("  Samples: num_u = " + str(num_u) + ", num_v = " + str(num_v))
    print("  U range (rad): [" + str(float(np.min(U))) + ", " + str(float(np.max(U))) + "]")
    print("  V range (a.u.): [" + str(float(np.min(V))) + ", " + str(float(np.max(V))) + "]")
    print("\nArray shapes:")
    print("  X, Y, Z shape: " + str(X.shape))
    print("  U, V shape: " + str(U.shape))
    print("\nBounding box extents (a.u.):")
    print("  x in [" + str(float(x_min)) + ", " + str(float(x_max)) + "]")
    print("  y in [" + str(float(y_min)) + ", " + str(float(y_max)) + "]")
    print("  z in [" + str(float(z_min)) + ", " + str(float(z_max)) + "]")
    print("\nPlot description:")
    print("  3D Möbius strip surface colored by the angular parameter u, with grid lines and equal aspect ratio.")


if __name__ == "__main__":
    main()