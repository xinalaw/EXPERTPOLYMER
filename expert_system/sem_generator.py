
import os
import math
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import gaussian_filter

# ---------- GLOBAL CONFIG ----------
IMG_SIZE = 224
OUTPUT_ROOT = r"C:\temp\yolo_dataset2"
TOTAL_IMAGES = 500         # how many images to generate total
VAL_FRACTION = 0.2         # 20% go to val/, rest to train/
PARTICLES_PER_IMAGE_RANGE = (5, 15)

# class names — index in this list = YOLO class_id
CLASSES = ["dendritic", "fragmented", "spongy", "spherical", "teardrop"]
CLASS_TO_ID = {c: i for i, c in enumerate(CLASSES)}

# ---------- UTILITIES ----------

def perlin_like_noise(h, w, scale=20, octaves=4, seed=None):
    """Cheap multi-octave value noise (no external lib)."""
    rng = np.random.default_rng(seed)
    noise = np.zeros((h, w), dtype=np.float32)
    amplitude, total_amp = 1.0, 0.0
    for o in range(octaves):
        s = scale / (2 ** o)
        small = rng.random((max(2, int(h / s) + 2), max(2, int(w / s) + 2))).astype(np.float32)
        layer = np.array(
            Image.fromarray((small * 255).astype(np.uint8)).resize((w, h), Image.BILINEAR),
            dtype=np.float32,
        ) / 255.0
        noise += layer * amplitude
        total_amp += amplitude
        amplitude *= 0.5
    return noise / total_amp


def rough_edge(mask, roughness=1.0, seed=None):
    """Perturb the binary mask outline so it isn't perfectly clean."""
    rng = np.random.default_rng(seed)
    m = mask.astype(np.float32)
    edge_noise = gaussian_filter(rng.normal(0, 1, mask.shape), sigma=0.8)
    m = gaussian_filter(m, sigma=0.5) + edge_noise * 0.025 * roughness
    return m > 0.5


def apply_sem_lighting(particle_mask, height_map, light_dir=(-1, -1, 1.5)):
    """Lambertian shading + topographic edge boost (SEM secondary-electron look)."""
    gy, gx = np.gradient(height_map.astype(np.float32))
    nz = np.ones_like(gx)
    norm = np.sqrt(gx * gx + gy * gy + nz * nz) + 1e-8
    nx, ny, nz = -gx / norm, -gy / norm, nz / norm
    lx, ly, lz = light_dir
    L = math.sqrt(lx * lx + ly * ly + lz * lz)
    lx, ly, lz = lx / L, ly / L, lz / L
    lambert = np.clip(nx * lx + ny * ly + nz * lz, 0, 1)
    edge = np.sqrt(gx * gx + gy * gy)
    edge = np.clip(edge / (edge.max() + 1e-8), 0, 1)
    shade = 0.35 + 0.55 * lambert + 0.35 * edge
    shade = np.clip(shade, 0, 1)
    shade[~particle_mask] = 0
    return shade


def add_sem_background(shape, seed=None):
    rng = np.random.default_rng(seed)
    h, w = shape
    base = rng.normal(loc=18, scale=4, size=(h, w))
    yy, xx = np.mgrid[0:h, 0:w]
    base *= (1.0 - 0.15 * ((xx + yy) / (h + w)))
    base += rng.normal(0, 2.5, (h, w))
    return np.clip(base, 0, 60)


def composite_particle(canvas, particle, mask, cx, cy):
    h, w = canvas.shape
    ph, pw = particle.shape
    y0, x0 = int(cy - ph // 2), int(cx - pw // 2)
    y1, x1 = y0 + ph, x0 + pw
    sy0, sx0 = max(0, -y0), max(0, -x0)
    dy0, dx0 = max(0, y0), max(0, x0)
    dy1, dx1 = min(h, y1), min(w, x1)
    sy1, sx1 = sy0 + (dy1 - dy0), sx0 + (dx1 - dx0)
    if dy1 <= dy0 or dx1 <= dx0:
        return canvas
    sub_p = particle[sy0:sy1, sx0:sx1]
    sub_m = mask[sy0:sy1, sx0:sx1]
    region = canvas[dy0:dy1, dx0:dx1]
    region[sub_m] = sub_p[sub_m] * 255
    canvas[dy0:dy1, dx0:dx1] = region
    return canvas


def add_drop_shadow(canvas, mask, cx, cy, offset=(4, 4), strength=0.5):
    h, w = canvas.shape
    ph, pw = mask.shape
    shadow = gaussian_filter(mask.astype(np.float32), sigma=3)
    y0, x0 = int(cy - ph // 2) + offset[1], int(cx - pw // 2) + offset[0]
    y1, x1 = y0 + ph, x0 + pw
    sy0, sx0 = max(0, -y0), max(0, -x0)
    dy0, dx0 = max(0, y0), max(0, x0)
    dy1, dx1 = min(h, y1), min(w, x1)
    sy1, sx1 = sy0 + (dy1 - dy0), sx0 + (dx1 - dx0)
    if dy1 <= dy0 or dx1 <= dx0:
        return canvas
    sub = shadow[sy0:sy1, sx0:sx1]
    canvas[dy0:dy1, dx0:dx1] *= (1 - sub * strength)
    return canvas


# ---------- PARTICLE GENERATORS ----------

def make_spherical_particle(radius, seed=None):
    rng = np.random.default_rng(seed)
    pad = 6
    size = radius * 2 + pad * 2
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float32)
    cx, cy = size / 2, size / 2
    a = radius * rng.uniform(0.95, 1.05)
    b = radius * rng.uniform(0.95, 1.05)
    d = ((xx - cx) / a) ** 2 + ((yy - cy) / b) ** 2
    mask = d <= 1.0
    h = np.zeros_like(d)
    h[mask] = np.sqrt(np.clip(1 - d[mask], 0, 1)) * radius
    h += perlin_like_noise(size, size, scale=8, octaves=3,
                           seed=rng.integers(1e6)) * 0.6
    h[~mask] = 0

    # satellites
    n_sat = rng.integers(0, 4)
    for _ in range(n_sat):
        theta = rng.uniform(0, 2 * math.pi)
        sr = max(2, int(radius * rng.uniform(0.08, 0.22)))
        scx = int(cx + math.cos(theta) * (radius - sr * 0.4))
        scy = int(cy + math.sin(theta) * (radius - sr * 0.4))
        sy, sx = np.ogrid[-sr - 2:sr + 3, -sr - 2:sr + 3]
        sd = (sx * sx + sy * sy) / float(sr * sr)
        sm = sd <= 1
        if scy - sr - 2 < 0 or scx - sr - 2 < 0 or scy + sr + 3 > size or scx + sr + 3 > size:
            continue
        sh = np.zeros_like(sd, dtype=np.float32)
        sh[sm] = np.sqrt(np.clip(1 - sd[sm], 0, 1)) * sr
        region_h = h[scy - sr - 2:scy + sr + 3, scx - sr - 2:scx + sr + 3]
        region_m = mask[scy - sr - 2:scy + sr + 3, scx - sr - 2:scx + sr + 3]
        h[scy - sr - 2:scy + sr + 3, scx - sr - 2:scx + sr + 3] = np.maximum(region_h, sh)
        mask[scy - sr - 2:scy + sr + 3, scx - sr - 2:scx + sr + 3] = region_m | sm

    return apply_sem_lighting(mask, h), mask


def make_fragmented_particle(size_px, seed=None):
    """Angular polygon with jagged edges and tilted facets — crushed/milled."""
    rng = np.random.default_rng(seed)
    pad = 8
    cs = size_px + pad * 2
    cx, cy = cs / 2, cs / 2

    # base polygon vertices (irregular angles + radii)
    n_verts = rng.integers(5, 11)
    raw_angles = np.cumsum(rng.uniform(0.15, 2 * np.pi / n_verts * 1.9, n_verts))
    angles = raw_angles / raw_angles[-1] * 2 * np.pi
    base_r = size_px * 0.4
    radii = np.array([base_r * rng.uniform(0.30, 1.0) for _ in range(n_verts)])
    # pull a few vertices inward to make concavities
    n_concave = rng.integers(1, max(2, n_verts // 3))
    for i in rng.choice(n_verts, size=n_concave, replace=False):
        radii[i] *= rng.uniform(0.25, 0.55)

    vx = cx + radii * np.cos(angles)
    vy = cy + radii * np.sin(angles)

    # JAGGED EDGES — insert displaced mid-points between each pair
    vx_d, vy_d = [], []
    for i in range(n_verts):
        vx_d.append(vx[i]); vy_d.append(vy[i])
        ni = (i + 1) % n_verts
        n_mid = rng.integers(2, 5)
        for j in range(1, n_mid):
            t = j / n_mid
            mx = vx[i] + t * (vx[ni] - vx[i])
            my = vy[i] + t * (vy[ni] - vy[i])
            edge_len = math.hypot(vx[ni] - vx[i], vy[ni] - vy[i])
            # perpendicular unit vector
            px = -(vy[ni] - vy[i]) / (edge_len + 1e-8)
            py = (vx[ni] - vx[i]) / (edge_len + 1e-8)
            jag = rng.uniform(-edge_len * 0.18, edge_len * 0.18)
            vx_d.append(mx + px * jag)
            vy_d.append(my + py * jag)

    # rasterize polygon with Pillow
    pts = list(zip(vx_d, vy_d))
    img = Image.new("L", (cs, cs), 0)
    ImageDraw.Draw(img).polygon(pts, fill=255)
    mask = np.array(img) > 128
    mask = rough_edge(mask, roughness=1.5, seed=rng.integers(1e6))

    # HEIGHT MAP: tilted plane + facet steps from discretized noise (crack-like)
    yy, xx = np.mgrid[0:cs, 0:cs].astype(np.float32)
    tilt_x = rng.uniform(-0.012, 0.012)
    tilt_y = rng.uniform(-0.012, 0.012)
    base_h = (rng.uniform(0.45, 0.75) + (xx - cx) * tilt_x + (yy - cy) * tilt_y) * size_px * 0.4

    # multi-facet: stepwise heights from quantized smooth noise (crack/cleavage planes)
    crack = gaussian_filter(rng.normal(0, 1, (cs, cs)), sigma=5)
    facet_steps = np.floor(crack * 3.5) / 12.0
    h = base_h + facet_steps * size_px * 0.18

    # tiny surface grain
    h += perlin_like_noise(cs, cs, scale=4, octaves=3,
                           seed=rng.integers(1e6)) * 1.2
    h[~mask] = 0
    h = np.clip(h, 0, None)

    return apply_sem_lighting(mask, h), mask


def make_dendritic_particle(size_px, seed=None):
    rng = np.random.default_rng(seed)
    pad = 10
    cs = size_px + pad * 2
    mask = np.zeros((cs, cs), dtype=bool)
    h = np.zeros((cs, cs), dtype=np.float32)
    main_angle = rng.uniform(0, 2 * math.pi)
    cx, cy = cs / 2, cs / 2

    def draw_branch(x, y, angle, length, thickness, depth):
        if depth > 3 or length < 3:
            return
        steps = int(length * 3)
        cur_angle = angle
        for i in range(steps):
            t = i / max(1, steps - 1)
            cur_angle += rng.normal(0, 0.015)
            px = x + math.cos(cur_angle) * (i / 3.0)
            py = y + math.sin(cur_angle) * (i / 3.0)
            r = max(1, int(thickness * (1 - 0.55 * t)))
            ix, iy = int(round(px)), int(round(py))
            if ix - r < 0 or iy - r < 0 or ix + r >= cs or iy + r >= cs:
                return
            yy, xx = np.ogrid[-r:r + 1, -r:r + 1]
            disk = xx * xx + yy * yy <= r * r
            local_m = mask[iy - r:iy + r + 1, ix - r:ix + r + 1]
            local_h = h[iy - r:iy + r + 1, ix - r:ix + r + 1]
            local_m |= disk
            mask[iy - r:iy + r + 1, ix - r:ix + r + 1] = local_m
            new_h = np.zeros_like(disk, dtype=np.float32)
            new_h[disk] = np.sqrt(np.clip(r * r - (xx * xx + yy * yy)[disk], 0, None))
            h[iy - r:iy + r + 1, ix - r:ix + r + 1] = np.maximum(local_h, new_h)
            if depth < 3 and rng.random() < 0.04 and i > 6:
                side_angle = cur_angle + rng.choice([-1, 1]) * rng.uniform(0.55, 1.0)
                side_len = length * rng.uniform(0.35, 0.65)
                side_thick = max(1, thickness * rng.uniform(0.55, 0.78))
                draw_branch(px, py, side_angle, side_len, side_thick, depth + 1)

    n_trunks = rng.integers(2, 5)
    base_thickness = max(2, size_px // 14)
    base_length = size_px * 0.45
    for k in range(n_trunks):
        a = main_angle + k * (2 * math.pi / n_trunks) + rng.normal(0, 0.2)
        draw_branch(cx, cy, a, base_length * rng.uniform(0.7, 1.1),
                    base_thickness * rng.uniform(0.85, 1.15), 0)

    h += perlin_like_noise(cs, cs, scale=5, octaves=3,
                           seed=rng.integers(1e6)) * 2.0
    h[~mask] = 0
    return apply_sem_lighting(mask, h), mask


def make_spongy_particle(radius, seed=None):
    rng = np.random.default_rng(seed)
    pad = 6
    size = radius * 2 + pad * 2
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float32)
    cx, cy = size / 2, size / 2
    a = radius * rng.uniform(0.9, 1.1)
    b = radius * rng.uniform(0.9, 1.1)
    d = np.sqrt(((xx - cx) / a) ** 2 + ((yy - cy) / b) ** 2)
    warp = perlin_like_noise(size, size, scale=radius * 0.6, octaves=3,
                             seed=rng.integers(1e6))
    mask = (d + (warp - 0.5) * 0.4) < 1.0
    mask = rough_edge(mask, roughness=1.2, seed=rng.integers(1e6))

    h = np.zeros_like(d)
    h[mask] = np.sqrt(np.clip(1 - d[mask] ** 2, 0, 1)) * radius * 0.8

    n_pores = int(radius * radius * 0.05)
    for _ in range(n_pores):
        for _ in range(10):
            px = rng.integers(2, size - 2)
            py = rng.integers(2, size - 2)
            if mask[py, px]:
                break
        else:
            continue
        pr = rng.integers(1, max(2, radius // 8))
        depth = rng.uniform(0.4, 0.95) * radius * 0.5
        sy, sx = np.ogrid[-pr - 1:pr + 2, -pr - 1:pr + 2]
        dist = sx * sx + sy * sy
        pore_mask = dist <= pr * pr
        if py - pr - 1 < 0 or px - pr - 1 < 0 or py + pr + 2 > size or px + pr + 2 > size:
            continue
        falloff = np.exp(-dist / (pr * pr * 0.5))
        h[py - pr - 1:py + pr + 2, px - pr - 1:px + pr + 2] -= depth * falloff * pore_mask

    h += perlin_like_noise(size, size, scale=4, octaves=3,
                           seed=rng.integers(1e6)) * 2.0
    h[~mask] = 0
    return apply_sem_lighting(mask, h), mask


def make_teardrop_particle(length_px, seed=None):
    """
    Ovoid / spheroidal / egg-shaped particle with small surface deformations.
    Both ends are rounded (no sharp tip). One end can be slightly fatter than
    the other (egg-like). Surface has subtle dimples, bumps, and silhouette
    waviness typical of partially solidified atomized droplets.
    """
    rng = np.random.default_rng(seed)
    pad = 10
    aspect = rng.uniform(1.2, 1.9)
    semi_a = length_px / 2
    semi_b = semi_a / aspect
    cs = int(length_px) + pad * 2
    cx, cy = cs / 2, cs / 2

    yy, xx = np.mgrid[0:cs, 0:cs].astype(np.float32)
    angle = rng.uniform(0, 2 * math.pi)
    ca, sa = math.cos(angle), math.sin(angle)
    xr = (xx - cx) * ca + (yy - cy) * sa
    yr = -(xx - cx) * sa + (yy - cy) * ca

    # base egg silhouette
    asym = rng.uniform(0.10, 0.28) * rng.choice([-1, 1])
    x_norm = xr / semi_a
    inside_x = np.abs(x_norm) <= 1.0
    half_width = np.zeros_like(xr)
    half_width[inside_x] = semi_b * np.sqrt(np.clip(1 - x_norm[inside_x] ** 2, 0, 1)) \
                                  * (1.0 + asym * x_norm[inside_x])

    # SILHOUETTE WAVINESS: perturb the half-width with low-frequency noise along x
    # so the outline isn't a perfect smooth curve.
    wave_seed = rng.integers(1e6)
    wave_1d = perlin_like_noise(1, cs, scale=cs / 6.0, octaves=3, seed=wave_seed)[0]
    wave_1d = (wave_1d - wave_1d.mean()) * 2.0  # zero-mean
    # apply per-column waviness amplitude (~6-12% of local half_width)
    wave_strength = rng.uniform(0.06, 0.12)
    half_width *= (1.0 + wave_strength * wave_1d[None, :])
    # Note: indexing wave_1d by column (xx coord); after rotation this gives
    # ripples along the *canvas* x-axis. To make them follow the *particle*
    # major axis, project x_norm to a 1D index:
    col_idx = np.clip(((x_norm + 1) * 0.5 * (cs - 1)).astype(np.int32), 0, cs - 1)
    half_width_pert = half_width / (1.0 + wave_strength * wave_1d[None, :])  # undo
    half_width = half_width_pert * (1.0 + wave_strength * wave_1d[col_idx])

    mask = inside_x & (np.abs(yr) < half_width)
    mask = rough_edge(mask, roughness=0.7, seed=rng.integers(1e6))

    # base 3D height: spheroidal cross-section
    h = np.zeros_like(xr)
    valid = mask & (half_width > 1e-3)
    ratio = np.zeros_like(xr)
    ratio[valid] = yr[valid] / half_width[valid]
    h[valid] = np.sqrt(np.clip(1 - ratio[valid] ** 2, 0, 1)) * half_width[valid]

    # SURFACE DEFORMATIONS: random dimples and bumps across the particle body.
    # Each is a smooth gaussian "dent" or "bulge" in the height map.
    n_deforms = rng.integers(2, 6)
    for _ in range(n_deforms):
        # pick a random point INSIDE the particle (not too close to the edge)
        for _try in range(15):
            tx = rng.uniform(-0.75, 0.75) * semi_a
            ty_max = semi_b * math.sqrt(max(0, 1 - (tx / semi_a) ** 2)) \
                     * (1 + asym * tx / semi_a) * 0.6
            ty = rng.uniform(-ty_max, ty_max) if ty_max > 0 else 0
            # back to canvas coords
            dcx = cx + tx * ca - ty * sa
            dcy = cy + tx * sa + ty * ca
            if pad < dcx < cs - pad and pad < dcy < cs - pad:
                break
        else:
            continue
        # deformation size and sign
        dr = max(3, int(semi_b * rng.uniform(0.15, 0.32)))
        sign = rng.choice([-1.0, 1.0])  # equal dents and bumps
        amp = rng.uniform(0.08, 0.22) * semi_b * 0.4 * sign
        y0, y1 = int(dcy) - dr * 2, int(dcy) + dr * 2 + 1
        x0, x1 = int(dcx) - dr * 2, int(dcx) + dr * 2 + 1
        if y0 < 0 or x0 < 0 or y1 > cs or x1 > cs:
            continue
        sub_yy, sub_xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
        dist2 = (sub_xx - dcx) ** 2 + (sub_yy - dcy) ** 2
        bump = amp * np.exp(-dist2 / (dr * dr * 0.6))
        sub_mask = mask[y0:y1, x0:x1]
        sub_h = h[y0:y1, x0:x1]
        new_h = sub_h + bump * sub_mask
        new_h = np.maximum(new_h, sub_h * 0.3 * sub_mask + (~sub_mask) * sub_h)
        h[y0:y1, x0:x1] = new_h

    # FLATTENED SPOT: with some probability, add a slight flat region as if the
    # droplet contacted another particle while still soft.
    if rng.random() < 0.35:
        # pick a point on the surface
        fx = rng.uniform(-0.6, 0.6) * semi_a
        fy_max = semi_b * math.sqrt(max(0, 1 - (fx / semi_a) ** 2)) \
                 * (1 + asym * fx / semi_a)
        fy = rng.choice([-1, 1]) * fy_max * rng.uniform(0.75, 0.95)
        fcx = cx + fx * ca - fy * sa
        fcy = cy + fx * sa + fy * ca
        fr = int(semi_b * rng.uniform(0.20, 0.35))
        y0, y1 = max(0, int(fcy) - fr * 2), min(cs, int(fcy) + fr * 2 + 1)
        x0, x1 = max(0, int(fcx) - fr * 2), min(cs, int(fcx) + fr * 2 + 1)
        if y1 > y0 and x1 > x0:
            sub_yy, sub_xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
            dist2 = (sub_xx - fcx) ** 2 + (sub_yy - fcy) ** 2
            falloff = np.exp(-dist2 / (fr * fr * 0.7))
            # compress height by up to 35% in this region
            sub_h = h[y0:y1, x0:x1]
            sub_mask = mask[y0:y1, x0:x1]
            compress = 1.0 - 0.35 * falloff * sub_mask
            h[y0:y1, x0:x1] = sub_h * compress

    # micro surface texture (very fine grain)
    h += perlin_like_noise(cs, cs, scale=8, octaves=3,
                           seed=rng.integers(1e6)) * 0.7
    # tiny high-frequency noise — like SEM micro-roughness
    h += perlin_like_noise(cs, cs, scale=2.5, octaves=2,
                           seed=rng.integers(1e6)) * 0.25
    h[~mask] = 0
    h = np.clip(h, 0, None)

    # optional satellite (kept from previous version, slightly lower probability)
    if rng.random() < 0.35:
        sign_fat = 1 if asym > 0 else -1
        sx_norm = sign_fat * rng.uniform(0.45, 0.85)
        hw = semi_b * math.sqrt(max(0, 1 - sx_norm ** 2)) * (1 + asym * sx_norm)
        sy_norm = rng.choice([-1, 1]) * rng.uniform(0.5, 0.95) * hw
        sx_local = sx_norm * semi_a
        sy_local = sy_norm
        scx = int(cx + sx_local * ca - sy_local * sa)
        scy = int(cy + sx_local * sa + sy_local * ca)
        sr = max(2, int(semi_b * rng.uniform(0.12, 0.22)))
        if sr + 2 < scx < cs - sr - 2 and sr + 2 < scy < cs - sr - 2:
            sy, sxk = np.ogrid[-sr - 1:sr + 2, -sr - 1:sr + 2]
            sd = (sxk * sxk + sy * sy) / float(sr * sr)
            sm = sd <= 1.0
            sh = np.zeros_like(sd, dtype=np.float32)
            sh[sm] = np.sqrt(np.clip(1 - sd[sm], 0, 1)) * sr
            region_h = h[scy - sr - 1:scy + sr + 2, scx - sr - 1:scx + sr + 2]
            region_m = mask[scy - sr - 1:scy + sr + 2, scx - sr - 1:scx + sr + 2]
            h[scy - sr - 1:scy + sr + 2, scx - sr - 1:scx + sr + 2] = np.maximum(region_h, sh)
            mask[scy - sr - 1:scy + sr + 2, scx - sr - 1:scx + sr + 2] = region_m | sm

    return apply_sem_lighting(mask, h), mask


# ---------- SCENE ASSEMBLY ----------

# All factories accept the SAME parameter `D` = target real bbox diameter (px).
# Internal multipliers compensate for each shape's inherent "size shrinkage":
# the measured ratio (real_bbox / requested_size) is ~0.57 for fragmented (a
# polygon doesn't fill its bounding circle), ~0.85 for teardrop (oblate),
# ~0.93 for dendritic (branches don't reach the full sweep radius), and ~1.0
# for spherical and spongy. We invert those ratios here so that asking for
# D=80 actually yields a particle whose bounding box is ~80 px across, for
# EVERY class. This is the fix for the "fragmented always smaller" bias.
PARTICLE_FACTORIES = {
    "dendritic":  lambda D, s: make_dendritic_particle(int(D * 1.07), s),
    "fragmented": lambda D, s: make_fragmented_particle(int(D * 1.75), s),
    "spongy":     lambda D, s: make_spongy_particle(D // 2, s),
    "spherical":  lambda D, s: make_spherical_particle(D // 2, s),
    "teardrop":   lambda D, s: make_teardrop_particle(int(D * 1.18), s),
}


def _mask_bbox_on_canvas(mask, cx, cy, canvas_h, canvas_w):
    """
    Given a particle mask of shape (ph, pw) that will be pasted with its center
    at (cx, cy) on a canvas, return the bounding box of the actually-visible
    foreground pixels in canvas coordinates: (x0, y0, x1, y1).

    Returns None if the mask projects entirely outside the canvas.
    """
    ph, pw = mask.shape
    # mask-local coords of foreground pixels
    ys, xs = np.where(mask)
    if len(ys) == 0:
        return None
    # convert local -> canvas coords (paste places mask center at cx, cy)
    x_canvas = xs + (cx - pw // 2)
    y_canvas = ys + (cy - ph // 2)
    # clip to canvas bounds
    x_canvas = np.clip(x_canvas, 0, canvas_w - 1)
    y_canvas = np.clip(y_canvas, 0, canvas_h - 1)
    x0, x1 = int(x_canvas.min()), int(x_canvas.max())
    y0, y1 = int(y_canvas.min()), int(y_canvas.max())
    if x1 <= x0 or y1 <= y0:
        return None
    return x0, y0, x1, y1


def _mask_to_polygon(mask, cx, cy, canvas_h, canvas_w, max_points=80):
    """
    Convert a particle's local mask (placed with its center at (cx, cy) on the
    canvas) to a normalized polygon in YOLO-seg format.

    Steps:
      1. Project the mask onto a full-canvas binary image.
      2. Trace the outline with OpenCV findContours (largest contour wins).
      3. Simplify with approxPolyDP so the polygon has at most max_points points.
      4. Normalize coords to [0, 1] relative to the canvas.

    Returns a flat list [x1, y1, x2, y2, ...] in YOLO-seg order, or None if
    the mask is empty / fully clipped.
    """
    import cv2  # local import so the rest of the script runs without cv2 if no seg needed
    ph, pw = mask.shape
    full = np.zeros((canvas_h, canvas_w), dtype=np.uint8)
    y0 = cy - ph // 2
    x0 = cx - pw // 2
    sy0, sx0 = max(0, -y0), max(0, -x0)
    dy0, dx0 = max(0, y0), max(0, x0)
    dy1, dx1 = min(canvas_h, y0 + ph), min(canvas_w, x0 + pw)
    sy1, sx1 = sy0 + (dy1 - dy0), sx0 + (dx1 - dx0)
    if dy1 <= dy0 or dx1 <= dx0:
        return None
    full[dy0:dy1, dx0:dx1] = mask[sy0:sy1, sx0:sx1].astype(np.uint8) * 255
    if full.sum() == 0:
        return None
    contours, _ = cv2.findContours(full, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    if not contours:
        return None
    # use the largest contour (in case the mask has stray detached pixels)
    cnt = max(contours, key=cv2.contourArea)
    if cv2.contourArea(cnt) < 4:
        return None
    # adaptive epsilon: smaller for big shapes, larger for tiny ones
    peri = cv2.arcLength(cnt, True)
    eps = max(0.5, peri * 0.005)
    approx = cv2.approxPolyDP(cnt, eps, True).reshape(-1, 2)
    # cap point count
    if len(approx) > max_points:
        # uniform downsample
        idx = np.linspace(0, len(approx) - 1, max_points).astype(int)
        approx = approx[idx]
    if len(approx) < 3:
        return None
    # normalize and flatten
    poly = []
    for x, y in approx:
        poly.append(float(x) / canvas_w)
        poly.append(float(y) / canvas_h)
    return poly


def generate_yolo_scene(seed=None, classes_pool=None):
    """
    Generate one mixed-class image with both bbox and polygon annotations.

    Returns:
        pil_image: 8-bit grayscale PIL Image
        boxes:     list of (class_id, cx_n, cy_n, w_n, h_n)             — YOLO det
        polys:     list of (class_id, [x1_n, y1_n, x2_n, y2_n, ...])    — YOLO seg
    """
    if classes_pool is None:
        classes_pool = CLASSES
    rng = np.random.default_rng(seed)
    canvas = add_sem_background((IMG_SIZE, IMG_SIZE), seed=rng.integers(1e6))
    n_particles = rng.integers(*PARTICLES_PER_IMAGE_RANGE)

    placed = []      # (cx, cy, half_size) — for overlap rejection
    boxes = []
    polys = []

    # Sample particle diameters from a WIDE distribution shared across all
    # classes. This is the key fix: each diameter is drawn independently of
    # which class it gets assigned to, so every class is represented at every
    # size (from 25 px tiny to 140 px large in a 512-px image).
    DIAM_MIN, DIAM_MAX = 25, 140

    attempts = 0
    while len(placed) < n_particles and attempts < n_particles * 25:
        attempts += 1
        cls = str(rng.choice(classes_pool))
        cls_id = CLASS_TO_ID[cls]
        # log-uniform diameter so small and large are both well-represented
        D = int(math.exp(rng.uniform(math.log(DIAM_MIN), math.log(DIAM_MAX))))
        half = D // 2 + 6
        cx = int(rng.uniform(half, IMG_SIZE - half))
        cy = int(rng.uniform(half, IMG_SIZE - half))
        if any(math.hypot(px - cx, py - cy) < (ps + half) * 0.75
               for px, py, ps in placed):
            continue
        factory = PARTICLE_FACTORIES[cls]
        shade, mask = factory(D, rng.integers(1e9))
        canvas = add_drop_shadow(canvas, mask, cx, cy, offset=(4, 4), strength=0.5)
        canvas = composite_particle(canvas, shade, mask, cx, cy)

        # BBOX from real mask
        bb = _mask_bbox_on_canvas(mask, cx, cy, IMG_SIZE, IMG_SIZE)
        if bb is None:
            placed.append((cx, cy, half))
            continue
        x0, y0, x1, y1 = bb
        w = x1 - x0 + 1
        h = y1 - y0 + 1
        boxes.append((
            cls_id,
            (x0 + x1) / 2.0 / IMG_SIZE,
            (y0 + y1) / 2.0 / IMG_SIZE,
            w / IMG_SIZE,
            h / IMG_SIZE,
        ))

        # POLYGON for segmentation
        poly = _mask_to_polygon(mask, cx, cy, IMG_SIZE, IMG_SIZE)
        if poly is not None:
            polys.append((cls_id, poly))

        placed.append((cx, cy, half))

    # SEM post-processing
    img = canvas.astype(np.float32)
    img = gaussian_filter(img, sigma=0.6)
    img += np.random.normal(0, 4.0, img.shape)
    scan = np.sin(np.linspace(0, IMG_SIZE * 0.5, IMG_SIZE)) * 1.5
    img += scan[:, None]
    img = np.clip(img, 0, 255)
    img = 255 * ((img / 255) ** 0.95)
    img = np.clip(img, 0, 255).astype(np.uint8)
    return Image.fromarray(img, mode="L"), boxes, polys


def write_yolo_det_label(label_path, boxes):
    """YOLO detection: one line per box -> 'class_id cx cy w h'."""
    with open(label_path, "w") as f:
        for cls_id, cx, cy, w, h in boxes:
            f.write(f"{cls_id} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}\n")


def write_yolo_seg_label(label_path, polys):
    """YOLO segmentation: one line per polygon -> 'class_id x1 y1 x2 y2 ...'."""
    with open(label_path, "w") as f:
        for cls_id, poly in polys:
            coords = " ".join(f"{v:.6f}" for v in poly)
            f.write(f"{cls_id} {coords}\n")


def write_data_yaml(root, task="detect"):
    """
    Write Ultralytics data.yaml. For detection use task='detect'; for
    instance segmentation use task='segment' (Ultralytics reads both from
    the same yaml — only the model/training command differs).
    """
    yaml_path = os.path.join(root, "data.yaml")
    with open(yaml_path, "w") as f:
        f.write(f"# Auto-generated by SEM synthetic dataset generator\n")
        f.write(f"# task: {task}\n")
        f.write(f"path: {os.path.abspath(root)}\n")
        f.write(f"train: images/train\n")
        f.write(f"val: images/val\n\n")
        f.write(f"nc: {len(CLASSES)}\n")
        f.write(f"names:\n")
        for i, c in enumerate(CLASSES):
            f.write(f"  {i}: {c}\n")


def main():
    """
    Generates TWO sibling datasets, both in standard Ultralytics layout:

      OUTPUT_ROOT/
        detect/                 ← train YOLO-detect models here
          data.yaml
          images/{train,val}/*.png
          labels/{train,val}/*.txt   (bbox format)
        segment/                ← train YOLO-seg models here
          data.yaml
          images/{train,val}/*.png   (same images, hard-linked to save space)
          labels/{train,val}/*.txt   (polygon format)

    Both datasets share the same images, so they describe exactly the
    same particles — only the annotation format differs.
    """
    det_root = os.path.join(OUTPUT_ROOT, "detect")
    seg_root = os.path.join(OUTPUT_ROOT, "segment")
    subdirs = {}
    for root in (det_root, seg_root):
        subdirs[root] = {}
        for split in ("train", "val"):
            for kind in ("images", "labels"):
                d = os.path.join(root, kind, split)
                os.makedirs(d, exist_ok=True)
                subdirs[root][(kind, split)] = d

    random.seed(42)
    master = 12345
    n_val = max(1, int(TOTAL_IMAGES * VAL_FRACTION))
    n_train = TOTAL_IMAGES - n_val

    def _gen_and_save(i, seed, split):
        img, boxes, polys = generate_yolo_scene(seed=seed)
        name = f"img_{i:05d}"
        # save image once into the detect dataset
        det_img_path = os.path.join(subdirs[det_root][("images", split)], name + ".png")
        img.save(det_img_path)
        # mirror it into the segment dataset (try hard link, fall back to copy)
        seg_img_path = os.path.join(subdirs[seg_root][("images", split)], name + ".png")
        try:
            if os.path.exists(seg_img_path):
                os.remove(seg_img_path)
            os.link(det_img_path, seg_img_path)
        except OSError:
            import shutil
            shutil.copyfile(det_img_path, seg_img_path)
        # labels
        write_yolo_det_label(
            os.path.join(subdirs[det_root][("labels", split)], name + ".txt"),
            boxes,
        )
        write_yolo_seg_label(
            os.path.join(subdirs[seg_root][("labels", split)], name + ".txt"),
            polys,
        )

    for i in range(n_train):
        _gen_and_save(i, master + i, "train")
    for i in range(n_val):
        _gen_and_save(i, master + 10_000_000 + i, "val")

    write_data_yaml(det_root, task="detect")
    write_data_yaml(seg_root, task="segment")

    print(f"YOLO datasets ready in: {OUTPUT_ROOT}")
    print(f"  detect/  : {n_train} train + {n_val} val  (bbox labels)")
    print(f"  segment/ : {n_train} train + {n_val} val  (polygon labels)")
    print(f"  classes ({len(CLASSES)}): {CLASSES}")


if __name__ == "__main__":
    main()