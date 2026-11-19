#!/usr/bin/env python3

import argparse
import cv2
import numpy as np


# ============================================================
# USER PARAMETERS
# ============================================================

DURATION = 1800.0               # seconds
FPS = 30                      # frames per second
WIDTH = 640
HEIGHT = 480

N_AGENTS = 4
AGENT_DIAMETER = 50           # pixels

LOW_SPEED = 1.0               # px / frame
HIGH_SPEED = 10.0              # px / frame

CHASE_PROBABILITY = 1 / 50    # probability per frame
CHASE_DURATION = 7.5         # seconds

OUTPUT_FILE = "agents.mp4"


# ============================================================
# OTHER SIMULATION PARAMETERS
# ============================================================

TURN_SD = 0.20                # radians/frame
SPEED_CHANGE_SD = 0.12        # px/frame
ESCAPE_TURN_SD = 0.60         # radians/frame

NOISE_SCALE = 90.0

AGENT_COLOR = (45, 145, 150)    # BGR dark gray

# Number of collision-resolution passes per frame.
# Multiple passes help when several agents are touching.
COLLISION_ITERATIONS = 4


# ============================================================
# STATIC PERLIN BACKGROUND
# ============================================================

def fade(t):
    return t * t * t * (t * (t * 6 - 15) + 10)


def generate_gradient_grid(grid_h, grid_w, rng):
    angles = rng.uniform(
        0,
        2 * np.pi,
        size=(grid_h, grid_w),
    )

    return np.stack(
        (np.cos(angles), np.sin(angles)),
        axis=-1,
    )


def perlin_2d(width, height, scale, gradients):
    x = np.arange(width, dtype=np.float32) / scale
    y = np.arange(height, dtype=np.float32) / scale

    xx, yy = np.meshgrid(x, y)

    x0 = np.floor(xx).astype(int)
    y0 = np.floor(yy).astype(int)

    xf = xx - x0
    yf = yy - y0

    x1 = x0 + 1
    y1 = y0 + 1

    g00 = gradients[y0, x0]
    g10 = gradients[y0, x1]
    g01 = gradients[y1, x0]
    g11 = gradients[y1, x1]

    n00 = g00[..., 0] * xf + g00[..., 1] * yf
    n10 = g10[..., 0] * (xf - 1) + g10[..., 1] * yf
    n01 = g01[..., 0] * xf + g01[..., 1] * (yf - 1)
    n11 = g11[..., 0] * (xf - 1) + g11[..., 1] * (yf - 1)

    u = fade(xf)
    v = fade(yf)

    nx0 = n00 * (1 - u) + n10 * u
    nx1 = n01 * (1 - u) + n11 * u

    return nx0 * (1 - v) + nx1 * v


def generate_background(seed=12345):
    """Generate one static colourful Perlin-noise background."""

    rng = np.random.default_rng(seed)

    grid_w = int(np.ceil(WIDTH / NOISE_SCALE)) + 2
    grid_h = int(np.ceil(HEIGHT / NOISE_SCALE)) + 2

    channels = []

    for _ in range(3):
        gradients = generate_gradient_grid(
            grid_h,
            grid_w,
            rng,
        )

        noise = perlin_2d(
            WIDTH,
            HEIGHT,
            NOISE_SCALE,
            gradients,
        )

        channels.append(noise)

    img = np.stack(channels, axis=-1)

    img = np.clip(
        img * 0.65 + 0.55,
        0,
        1,
    )

    img = 80 + img * 175

    return img.astype(np.uint8)


# ============================================================
# INITIAL POSITIONS
# ============================================================

def generate_initial_positions(rng):
    """
    Place agents randomly without overlap.
    """

    radius = AGENT_DIAMETER / 2
    positions = []

    max_attempts = 10000

    for _ in range(N_AGENTS):

        for _ in range(max_attempts):

            candidate = np.array([
                rng.uniform(radius, WIDTH - radius),
                rng.uniform(radius, HEIGHT - radius),
            ])

            if all(
                np.linalg.norm(candidate - p) >= AGENT_DIAMETER
                for p in positions
            ):
                positions.append(candidate)
                break

        else:
            raise RuntimeError(
                "Could not place all agents without overlap. "
                "Reduce N_AGENTS or AGENT_DIAMETER."
            )

    return np.array(positions, dtype=float)


# ============================================================
# BOUNDARIES
# ============================================================

def resolve_boundaries(positions, velocities):
    """
    Reflect agents from the rectangular boundaries.
    """

    radius = AGENT_DIAMETER / 2

    for i in range(len(positions)):

        # Left
        if positions[i, 0] < radius:
            positions[i, 0] = radius
            velocities[i, 0] = abs(velocities[i, 0])

        # Right
        elif positions[i, 0] > WIDTH - radius:
            positions[i, 0] = WIDTH - radius
            velocities[i, 0] = -abs(velocities[i, 0])

        # Top
        if positions[i, 1] < radius:
            positions[i, 1] = radius
            velocities[i, 1] = abs(velocities[i, 1])

        # Bottom
        elif positions[i, 1] > HEIGHT - radius:
            positions[i, 1] = HEIGHT - radius
            velocities[i, 1] = -abs(velocities[i, 1])


# ============================================================
# AGENT COLLISIONS
# ============================================================

def resolve_collisions(positions, velocities, rng):
    """
    Resolve collisions between circular agents.

    Agents are treated as equal-mass discs.

    For each overlapping pair:
        1. Move them apart so they no longer overlap.
        2. Exchange their velocity components along the
           collision normal.

    Tangential velocity is unchanged.
    """

    min_distance = float(AGENT_DIAMETER)

    for _ in range(COLLISION_ITERATIONS):

        collision_found = False

        for i in range(N_AGENTS):
            for j in range(i + 1, N_AGENTS):

                delta = positions[j] - positions[i]
                distance = np.linalg.norm(delta)

                if distance >= min_distance:
                    continue

                collision_found = True

                # Extremely unlikely, but avoid division by zero
                # if two centres are exactly coincident.
                if distance < 1e-8:
                    angle = rng.uniform(0, 2 * np.pi)

                    normal = np.array([
                        np.cos(angle),
                        np.sin(angle),
                    ])

                    distance = 0.0

                else:
                    normal = delta / distance

                # ------------------------------------------------
                # Separate the overlapping circles
                # ------------------------------------------------

                overlap = min_distance - distance

                correction = normal * (
                    overlap / 2 + 1e-3
                )

                positions[i] -= correction
                positions[j] += correction

                # ------------------------------------------------
                # Collision response
                # ------------------------------------------------

                relative_velocity = (
                    velocities[j] - velocities[i]
                )

                relative_normal_speed = np.dot(
                    relative_velocity,
                    normal,
                )

                # Only bounce if they are moving toward
                # one another.
                if relative_normal_speed < 0:

                    # Equal-mass elastic collision:
                    # exchange normal components.
                    impulse = relative_normal_speed * normal

                    velocities[i] += impulse
                    velocities[j] -= impulse

        # Collisions near walls can push an agent outside.
        resolve_boundaries(
            positions,
            velocities,
        )

        if not collision_found:
            break


# ============================================================
# TRAJECTORY GENERATION
# ============================================================

def generate_trajectories(
    duration,
    fps,
    chase_probability,
    seed=None,
):
    """
    Generate all agent trajectories before rendering.

    Returns
    -------
    trajectories : ndarray
        Shape:
            (N_AGENTS, 2, N_FRAMES)
    """

    rng = np.random.default_rng(seed)

    n_frames = int(duration * fps)
    chase_frames = int(CHASE_DURATION * fps)

    trajectories = np.empty(
        (N_AGENTS, 2, n_frames),
        dtype=np.float32,
    )

    # --------------------------------------------------------
    # Initial conditions
    # --------------------------------------------------------

    positions = generate_initial_positions(rng)

    angles = rng.uniform(
        0,
        2 * np.pi,
        N_AGENTS,
    )

    speeds = rng.uniform(
        LOW_SPEED,
        HIGH_SPEED,
        N_AGENTS,
    )

    velocities = np.column_stack([
        np.cos(angles),
        np.sin(angles),
    ])

    velocities *= speeds[:, None]

    trajectories[:, :, 0] = positions

    chase = None

    # --------------------------------------------------------
    # Simulation
    # --------------------------------------------------------

    for frame_i in range(1, n_frames):

        # ----------------------------------------------------
        # Convert current velocity back into angle/speed
        #
        # This matters because collisions may have changed
        # velocity direction during the previous frame.
        # ----------------------------------------------------

        angles = np.arctan2(
            velocities[:, 1],
            velocities[:, 0],
        )

        speeds = np.linalg.norm(
            velocities,
            axis=1,
        )

        # ----------------------------------------------------
        # Chase management
        # ----------------------------------------------------

        if chase is None:

            if rng.random() < chase_probability:

                chaser_i, chased_i = rng.choice(
                    N_AGENTS,
                    size=2,
                    replace=False,
                )

                chase = {
                    "chaser": chaser_i,
                    "chased": chased_i,
                    "remaining": chase_frames,
                }

        else:

            chase["remaining"] -= 1

            if chase["remaining"] <= 0:
                chase = None

        # ----------------------------------------------------
        # Normal correlated random walk
        # ----------------------------------------------------

        angles += rng.normal(
            0,
            TURN_SD,
            N_AGENTS,
        )

        speeds += rng.normal(
            0,
            SPEED_CHANGE_SD,
            N_AGENTS,
        )

        speeds = np.clip(
            speeds,
            LOW_SPEED,
            HIGH_SPEED,
        )

        # ----------------------------------------------------
        # Chase behaviour
        # ----------------------------------------------------

        if chase is not None:

            chaser_i = chase["chaser"]
            chased_i = chase["chased"]

            delta = (
                positions[chased_i]
                - positions[chaser_i]
            )

            chase_angle = np.arctan2(
                delta[1],
                delta[0],
            )

            # Chaser moves directly toward target.
            angles[chaser_i] = chase_angle
            speeds[chaser_i] = HIGH_SPEED

            # Target moves approximately directly away,
            # with extra random turning.
            angles[chased_i] = (
                chase_angle
                + rng.normal(
                    0,
                    ESCAPE_TURN_SD,
                )
            )

            speeds[chased_i] = HIGH_SPEED

        # ----------------------------------------------------
        # Construct velocities
        # ----------------------------------------------------

        velocities[:, 0] = (
            np.cos(angles) * speeds
        )

        velocities[:, 1] = (
            np.sin(angles) * speeds
        )

        # ----------------------------------------------------
        # Move
        # ----------------------------------------------------

        positions += velocities

        # ----------------------------------------------------
        # Walls
        # ----------------------------------------------------

        resolve_boundaries(
            positions,
            velocities,
        )

        # ----------------------------------------------------
        # Agent-agent collisions
        # ----------------------------------------------------

        resolve_collisions(
            positions,
            velocities,
            rng,
        )

        # ----------------------------------------------------
        # Save positions
        # ----------------------------------------------------

        trajectories[:, :, frame_i] = positions

    return trajectories


# ============================================================
# VIDEO RENDERING
# ============================================================

def render_video(
    trajectories,
    output,
    fps,
    background_seed=12345,
):
    """
    Render previously generated trajectories.
    """

    n_frames = trajectories.shape[2]

    print("Generating background...")

    background = generate_background(
        background_seed
    )

    fourcc = cv2.VideoWriter_fourcc(
        *"mp4v"
    )

    writer = cv2.VideoWriter(
        output,
        fourcc,
        fps,
        (WIDTH, HEIGHT),
    )

    if not writer.isOpened():
        raise RuntimeError(
            f"Could not open video writer: {output}"
        )

    for frame_i in range(n_frames):

        frame = background.copy()

        for pos in trajectories[:, :, frame_i]:

            centre = tuple(
                np.round(pos).astype(int)
            )

            cv2.circle(
                frame,
                centre,
                AGENT_DIAMETER // 2,
                AGENT_COLOR,
                thickness=-1,
                lineType=cv2.LINE_AA,
            )

        writer.write(frame)

        if frame_i % fps == 0:

            print(
                f"\rRendering: "
                f"{frame_i / fps:.1f}/"
                f"{n_frames / fps:.1f} s",
                end="",
                flush=True,
            )

    writer.release()

    print(f"\nSaved: {output}")


# ============================================================
# MAIN
# ============================================================

def main():

    parser = argparse.ArgumentParser(
        description=(
            "Generate a video of simulated moving agents."
        )
    )

    parser.add_argument(
        "-o",
        "--output",
        default=OUTPUT_FILE,
        help=(
            f"Output video file "
            f"(default: {OUTPUT_FILE})"
        ),
    )

    parser.add_argument(
        "-d",
        "--duration",
        type=float,
        default=DURATION,
        help=(
            f"Duration in seconds "
            f"(default: {DURATION})"
        ),
    )

    parser.add_argument(
        "--fps",
        type=int,
        default=FPS,
        help=(
            f"Frames per second "
            f"(default: {FPS})"
        ),
    )

    parser.add_argument(
        "--chase-probability",
        type=float,
        default=CHASE_PROBABILITY,
        help=(
            "Probability of starting a chase "
            "on each frame "
            f"(default: {CHASE_PROBABILITY})"
        ),
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducibility.",
    )

    args = parser.parse_args()

    # --------------------------------------------------------
    # Generate trajectories
    # --------------------------------------------------------

    print("Generating trajectories...")

    trajectories = generate_trajectories(
        duration=args.duration,
        fps=args.fps,
        chase_probability=args.chase_probability,
        seed=args.seed,
    )

    print(
        f"Trajectory array: "
        f"{trajectories.shape}"
    )

    # --------------------------------------------------------
    # Render video
    # --------------------------------------------------------

    print("Rendering video...")

    render_video(
        trajectories=trajectories,
        output=args.output,
        fps=args.fps,
    )


if __name__ == "__main__":
    main()
