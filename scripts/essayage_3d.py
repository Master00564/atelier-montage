#!/usr/bin/env python3
"""Camera light-fitting app: the manufacturer's 3D file of a product (an OBJ in millimetres, Y up, as CAD tools
export it) becomes the model a phone browser draws in the camera picture (GLB, metres).

    python scripts/essayage_3d.py LOT_DIR        (see main(); run after essayage_modele.py assemble)

Nothing is typed per product. A manufacturer's file has the true shape and no true colours, so:
- the camera of the shop's photo n.1 is found by fitting the model's outline to the photo's cut-out (the cable or
  rods of a hanging fitting are often shortened on a photo: their length is one of the things the fit finds);
- every part of the model takes the colour the unlit photo shows where that part is seen; a part the photo hides
  takes its twin's colour;
- the light sources are where the lit photo is the brightest, placed in the model between its surfaces;
- the light profile (how much light leaves in each direction) is measured on the model from those sources.
Writes <nom>.glb (nodes "haut", "tige", "bas": what stays at the ceiling, the cable, what hangs), <nom>.json
(size, sources, profile, cable, proof numbers) and <nom>-preuve.jpg (photo | model drawn from the found camera).
A model whose outline does not fit its photo is refused: it is not that product's file."""
import io
import json
import os
import struct
import subprocess
import sys
import urllib.request
import zipfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy.optimize import minimize
from scipy.ndimage import binary_fill_holes, label, maximum_filter
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components

ROOT = Path(__file__).resolve().parent.parent
RNG = np.random.default_rng(7)
GLTF_TOOL = "@gltf-transform/cli@4.1.0"
MOST_TRIANGLES = 300_000    # above: the phone's file is thinned to about this many
MOST_BYTES = 150_000_000    # a manufacturer's archive larger than this is refused
FIT_SIDE, SEEN_SIDE = 160, 320
MIN_OUTLINE = 0.72          # outlines overlapping less than this, and not side by side either (MIN_NEAR): the
MIN_NEAR, NEAR = 0.90, 2    # model is not the photo's product (or its up axis is not Y)
STARTS = 12                 # best rough poses refined; six left a disc-and-globe wall light on a wrong pose
FLAT_MIN, PLATE = 300.0, 0.35  # wall side of a plate: least flat surface that counts (mm2); its depth over its width
BASE_MIN, BASE_LONG = 25.0, 4.0  # wall side otherwise: a base is at least this wide (mm) and no longer than this times its width
LYING = 0.05                # a file is drawn lying when a pose from any side fits its photo this much better than an upright one
MIN_WHOLE = 0.85            # last resort: overlap of the two outer outlines, holes filled
GLOW_GAIN = 0.22            # a part this much brighter in the lit photo (0..1) glows
SAME_COLOUR = 26.0          # parts closer than this (RGB distance) share one material
SLICES, CELLS = 16, 256      # light profile: slices kept, cells of directions per half turn when measuring
PROFILE_POINTS = 2_500_000  # surface samples for the profile (a few per square millimetre of a fitting)
BULB = 70.0                 # mm around a source that are its bulb and socket
BULB_LIGHT = (255.0, 222.0, 178.0)   # colour of a lit bulb the photo hides (warm white)
CORE_SHARE = 0.85          # a light source: glowing pixels at least this bright, against the brightest one
LIT_GAIN = 0.05             # a pixel this much brighter in the lit photo is lit by the fitting
CREASE = 40.0               # degrees: two triangles meeting at more than this are two faces
GLASS_COVER = 0.90          # a part that hides at least this share of a source's bright patch, which the photo shows all the same, is clear glass
VEIL_SHARE = 0.15           # bright over more than this share of its seen surface: a lit veil, not clear glass
GLASS_ALPHA = 0.32          # how much of a clear glass shows (the rest is what stands behind it)
SOFT_THROUGH = 0.5          # share of light the body of a fitting lets through when the photos show no bright spot
SAME_SOURCE = 100.0         # two bright patches closer than this (model units, mm) are one source


class Refused(Exception):
    """This product gets no 3D model, for the reason given."""


UNITS = {"millimeters": 1.0, "centimeters": 10.0, "meters": 1000.0, "inches": 25.4, "feet": 304.8}


def load_obj(path, size_mm=None):
    """-> positions in millimetres (n,3), normals (m,3), corners (t,3,2) [vertex, normal], part id per triangle,
    parts [{group, mtl, definition}]. The file's unit is read in its header ("File units = meters") and checked
    against the product's known size when there is one: the unit that brings the model's width closest to it wins.
    A part is one solid: the faces of one group and material that touch each other."""
    pos, nor, corners, tri_part, parts = [], [], [], [], []
    group, mtl, current, unit = "", "", {}, "millimeters"
    for line in open(path, errors="ignore"):
        head = line[:2]
        if head == "# " and "units" in line.lower():
            named = line.split("=")[-1].strip().lower()
            unit = named if named in UNITS else unit
        elif head == "v ":
            p = line.split(); pos.append((float(p[1]), float(p[2]), float(p[3])))
        elif head == "vn":
            p = line.split(); nor.append((float(p[1]), float(p[2]), float(p[3])))
        elif head == "g ":
            group = line[2:].strip()
        elif line.startswith("usemtl"):
            mtl = line.split(None, 1)[1].strip()
        elif head == "f ":
            key = (group, mtl)
            if key not in current:
                current[key] = len(parts)
                tokens = group.split()
                definition = tokens[1].rsplit("_", 1)[0] if len(tokens) > 1 else ""
                parts.append({"group": group, "mtl": mtl, "definition": definition})
            part = current[key]
            face = []
            for token in line.split()[1:]:
                bits = token.split("/")
                v = int(bits[0]); n = int(bits[2]) if len(bits) > 2 and bits[2] else 0
                face.append((v - 1 if v > 0 else len(pos) + v, n - 1 if n > 0 else (len(nor) + n if n < 0 else -1)))
            for k in range(1, len(face) - 1):
                corners.append((face[0], face[k], face[k + 1])); tri_part.append(part)
    pos, corners, tri_part = np.array(pos), np.array(corners, dtype=np.int64), np.array(tri_part)
    width = max(np.ptp(pos[:, 0]), np.ptp(pos[:, 2]))
    if size_mm and not 0.6 < width * UNITS[unit] / size_mm < 1.6:
        unit = min(UNITS, key=lambda u: abs(np.log(width * UNITS[u] / size_mm)))
    pos = pos * UNITS[unit]
    tri_part, parts = solids(pos, corners[:, :, 0], tri_part, parts)
    return pos, np.array(nor) if nor else np.zeros((0, 3)), corners, tri_part, parts, unit


def solids(pos, tris, tri_part, parts):
    """Split every part into its smooth faces: triangles that share an edge and meet at less than CREASE degrees
    (corners welded at 0.01 mm). A drum shade exported as one block then has its side, its bottom diffuser, its
    cable and its ceiling cup as separate parts, and each can take its own colour and its own way with light.
    Faces too small to matter (under 0.05 % of the surface: the wall of each hole of a perforated sheet) stay
    together, per part."""
    _, welded = np.unique(np.round(pos, 2), axis=0, return_inverse=True)
    t = welded.reshape(-1)[tris]
    a, b, c = pos[tris[:, 0]], pos[tris[:, 1]], pos[tris[:, 2]]
    normal = np.cross(b - a, c - a)
    area = np.linalg.norm(normal, axis=1)
    normal = normal / np.maximum(area, 1e-12)[:, None]
    count = int(t.max()) + 1
    edges = np.stack([t[:, [0, 1]], t[:, [1, 2]], t[:, [2, 0]]], axis=1).reshape(-1, 2)
    keys = edges.min(1) * count + edges.max(1)
    owner = np.repeat(np.arange(len(t)), 3)
    order = np.argsort(keys, kind="stable")
    same = keys[order][1:] == keys[order][:-1]
    one, other = owner[order][:-1][same], owner[order][1:][same]
    smooth = np.abs((normal[one] * normal[other]).sum(1)) > np.cos(np.radians(CREASE))
    graph = coo_matrix((np.ones(smooth.sum()), (one[smooth], other[smooth])), shape=(len(t), len(t)))
    _, face = connected_components(graph, directed=False)
    surface = np.bincount(face, weights=area)
    face = np.where(surface[face] < 0.0005 * area.sum(), -1, face)
    kept, new_part = np.unique(np.stack([tri_part, face], axis=1), axis=0, return_inverse=True)
    return new_part.reshape(-1), [dict(parts[k[0]]) for k in kept]


def sample(pos, tris, tri_part, count):
    a, b, c = pos[tris[:, 0]], pos[tris[:, 1]], pos[tris[:, 2]]
    area = np.linalg.norm(np.cross(b - a, c - a), axis=1) / 2
    pick = RNG.choice(len(tris), size=count, p=area / area.sum())
    u, v = RNG.random(count), RNG.random(count)
    flip = u + v > 1
    u[flip], v[flip] = 1 - u[flip], 1 - v[flip]
    return a[pick] + (b[pick] - a[pick]) * u[:, None] + (c[pick] - a[pick]) * v[:, None], tri_part[pick], area


def rotation(yaw, pitch, roll):
    cy, sy, cp, sp, cr, sr = np.cos(yaw), np.sin(yaw), np.cos(pitch), np.sin(pitch), np.cos(roll), np.sin(roll)
    ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    rx = np.array([[1, 0, 0], [0, cp, -sp], [0, sp, cp]])
    rz = np.array([[cr, -sr, 0], [sr, cr, 0], [0, 0, 1]])
    return rz @ rx @ ry


def cable_zone(points, area_share=0.12, least=0.15):
    """The stretch of height where a hanging fitting is only its cable or rods (photos often show it shortened):
    the longest run of thin horizontal slices between two thicker ends. -> (low, high) heights or None"""
    y = points[:, 1]
    edges = np.linspace(y.min(), y.max(), 121)
    slices = np.histogram(y, edges)[0].astype(float)
    thin = slices < area_share * np.percentile(slices, 92)
    best, start = None, None
    for i, flag in enumerate(list(thin) + [False]):
        if flag and start is None:
            start = i
        elif not flag and start is not None:
            if 0 < start and i < len(thin) and (best is None or i - start > best[1] - best[0]):
                best = (start, i)
            start = None
    if best is None or (best[1] - best[0]) / len(thin) < least:
        return None
    return float(edges[best[0]]), float(edges[best[1]])


def shorten(points, zone, keep):
    """The same points with the cable zone kept at `keep` of its length (what is below moves up)."""
    if zone is None:
        return points
    low, high = zone
    moved = points.copy()
    y = points[:, 1]
    inside = (y >= low) & (y <= high)
    moved[inside, 1] = high - (high - y[inside]) * keep
    moved[y < low, 1] += (high - low) * (1 - keep)
    return moved


class Camera:
    """Photo camera: looks at the model's centre from `distance` radii away; the picture is the cut-out's frame."""

    def __init__(self, points, centre, radius, zone=None):
        self.points, self.centre, self.radius, self.zone = points, centre, radius, zone
        self.keep = None
        self.cable(1.0)

    def cable(self, keep):
        keep = float(np.clip(keep, 0.05, 1.0))
        if keep != self.keep:
            self.keep = keep
            self.q = (shorten(self.points, self.zone, keep) - self.centre) / self.radius

    def other(self, points):
        return (shorten(points, self.zone, self.keep) - self.centre) / self.radius

    def view(self, params, width, height, q=None):
        yaw, pitch, roll, logd = params[:4]
        if q is None and len(params) > 4:
            self.cable(params[4])
        p = (self.q if q is None else q) @ rotation(yaw, pitch, roll).T
        d = np.exp(logd)
        w = d / (d - p[:, 2])
        x, y = p[:, 0] * w, -p[:, 1] * w
        if q is None:
            self.frame = (x.min(), x.max(), y.min(), y.max())
        x0, x1, y0, y1 = self.frame
        scale = 0.5 * (width / (x1 - x0) + height / (y1 - y0))
        return ((x - (x0 + x1) / 2) * scale + width / 2, (y - (y0 + y1) / 2) * scale + height / 2, p[:, 2])


def outline_score(camera, params, target, whole=False):
    """Overlap of the model's outline and the photo's, 0 to 1. `whole`: both taken with their holes filled (the
    caller fills the photo's): what is left to compare when the photo's cut-out lost the inside of the fitting."""
    h, w = target.shape
    x, y, _ = camera.view(params, w, h)
    ix, iy = np.clip(x.astype(int), 0, w - 1), np.clip(y.astype(int), 0, h - 1)
    inside = (x >= -1) & (x <= w) & (y >= -1) & (y <= h)
    mask = np.zeros((h, w), bool)
    mask[iy[inside], ix[inside]] = True
    mask = maximum_filter(mask, 3)
    if whole:
        mask = binary_fill_holes(mask)
    union = (mask | target).sum()
    return (mask & target).sum() / union if union else 0.0


def outline_near(camera, params, target):
    """For a fitting made of thin cables, two outlines one pixel apart overlap badly although the fit is right.
    This measure forgives NEAR pixels (of the 160 px fitting grid): the share of each outline that lies within
    that distance of the other, the smaller of the two shares. 1 = the same outline."""
    h, w = target.shape
    x, y, _ = camera.view(params, w, h)
    inside = (x >= 0) & (x < w) & (y >= 0) & (y < h)
    mask = np.zeros((h, w), bool)
    mask[y[inside].astype(int), x[inside].astype(int)] = True
    wide = 2 * NEAR + 1
    return float(min((mask & maximum_filter(target, wide)).sum() / max(mask.sum(), 1),
                     (target & maximum_filter(mask, wide)).sum() / max(target.sum(), 1)))


def fit_camera(camera, target, whole=False, any_way_up=False):
    """The photo's camera: rough poses all around the model, the best ones refined. `any_way_up`: the file may be
    drawn lying or on its side (a wall fitting before wall_turn): poses from above, from below and rolled too."""
    starts = []
    pitches = (-90, -60, -30, 0, 30, 60, 90) if any_way_up else (-60, -40, -25, -10, 0, 10, 25, 40)
    for yaw in np.radians(np.arange(0, 360, 15)):
        for pitch in np.radians(pitches):
            for roll in np.radians((0, 90, -90) if any_way_up else (0,)):
                for keep in ((1.0, 0.6, 0.3) if camera.zone else (1.0,)):
                    params = (yaw, pitch, roll, np.log(5.0), keep)
                    starts.append((outline_score(camera, params, target, whole), params))
    starts.sort(key=lambda s: -s[0])
    best = (0.0, None)
    for _, params in starts[:STARTS]:
        found = minimize(lambda p: -outline_score(camera, p, target, whole), params, method="Nelder-Mead",
                         options={"xatol": 2e-3, "fatol": 1e-4, "maxiter": 600,
                                  "initial_simplex": np.array(params) + np.vstack([np.zeros(5), np.diag([0.12, 0.12, 0.05, 0.4, 0.15 if camera.zone else 0.0])])})
        if -found.fun > best[0]:
            best = (-found.fun, found.x)
    return best


def seen_colours(camera, params, part_of_point, photos, parts_count, core, solid):
    """Median colour of each part where the photo shows it (points hidden behind others are left out), once per
    photo, then the share of each part's seen surface that lies in the lit photo's bright core."""
    w, h = photos[0].size
    scale = SEEN_SIDE / max(w, h)
    zw, zh = max(1, round(w * scale)), max(1, round(h * scale))
    x, y, z = camera.view(params, w, h)
    ix, iy = np.clip((x * scale).astype(int), 0, zw - 1), np.clip((y * scale).astype(int), 0, zh - 1)
    depth = np.full((zh, zw), -np.inf)
    np.maximum.at(depth, (iy[solid], ix[solid]), z[solid])
    front = solid & (z >= maximum_filter(depth, 3)[iy, ix] - 0.03)
    px, py = np.clip(x.astype(int), 0, w - 1), np.clip(y.astype(int), 0, h - 1)
    result = []
    for photo in photos:
        rgba = np.asarray(photo.convert("RGBA"), dtype=np.float32)
        colour, alpha = rgba[py, px, :3], rgba[py, px, 3]
        ok = front & (alpha > 240)
        table = np.full((parts_count, 3), np.nan)
        counts = np.zeros(parts_count, int)
        for part in range(parts_count):
            mine = ok & (part_of_point == part)
            counts[part] = mine.sum()
            if counts[part] >= 12:
                table[part] = np.median(colour[mine], axis=0)
        result.append((table, counts))
    step = core[1]
    inside = front & core[0][np.clip(py // step, 0, core[0].shape[0] - 1), np.clip(px // step, 0, core[0].shape[1] - 1)]
    seen = np.bincount(part_of_point[front], minlength=parts_count)
    result.append(np.bincount(part_of_point[inside], minlength=parts_count) / np.maximum(seen, 1))
    return result


def bright_core(unlit, lit):
    """The lit photo's bright core, at a coarser grid: of the pixels that are brighter when the fitting is on
    (by LIT_GAIN at least), those that are among the brightest (CORE_SHARE of the brightest one). An opal globe is
    white unlit and white lit: it gains little, and yet it is the brightest. -> (mask, step, lit picture)"""
    a = np.asarray(unlit.convert("RGBA"), dtype=np.float32)
    b = np.asarray(lit.convert("RGBA"), dtype=np.float32)
    lit_light = luminance(b[..., :3])
    step = max(1, max(unlit.size) // 250)
    small = (lit_light * ((lit_light - luminance(a[..., :3]) > LIT_GAIN) & (a[..., 3] > 240)))[::step, ::step]
    return (small > CORE_SHARE * small.max()) & (small > 0), step, b


def light_sources(camera, params, points, core):
    """Where the light comes from: each patch of the lit photo's bright core is one source; its place in space is
    the middle of the model's surfaces seen through that patch (a bulb inside a shade sits between the shade's near
    and far walls). -> [(position in model units, colour, weight)]"""
    mask, step, b = core
    h, w = b.shape[:2]
    patches, count = label(mask)
    small = mask
    x, y, _ = camera.view(params, w, h)
    found = []
    for patch in range(1, count + 1):
        ys, xs = np.nonzero(patches == patch)
        if len(ys) < 0.00006 * small.size:
            continue
        cx, cy = xs.mean() * step, ys.mean() * step
        reach = max(6.0, 0.6 * np.sqrt(len(ys) / np.pi) * step)
        near = (x - cx) ** 2 + (y - cy) ** 2 < reach ** 2
        if near.sum() < 20:
            continue
        colour = np.median(b[ys * step, xs * step, :3], axis=0)
        found.append([points[near].mean(0) * len(ys), colour * len(ys), len(ys)])
    merged = []
    for where, colour, weight in sorted(found, key=lambda f: -f[2]):
        for item in merged:
            if np.linalg.norm(item[0] / item[2] - where / weight) < SAME_SOURCE:
                item[0] += where; item[1] += colour; item[2] += weight; break
        else:
            merged.append([where, colour, weight])
    most = max((m[2] for m in merged), default=0)
    return [(where / weight, colour / weight, weight) for where, colour, weight in merged if weight >= 0.25 * most]


def clear_glass(camera, params, dense, dense_part, parts_count, core, sources):
    """Parts that are clear glass: a light source shows as a bright patch on the photo although the model has a
    closed surface in front of it. For each source, each part standing between it and the camera is measured on
    the patch (cells of 2 pixels): one that covers GLASS_COVER of it is glass; a perforated sheet covers less (the
    light is seen through its holes). -> one flag per part"""
    mask, step, b = core
    h, w = b.shape[:2]
    patches, _ = label(mask)
    x, y, z = camera.view(params, w, h, q=camera.other(dense))
    glass = np.zeros(parts_count, bool)
    fine = max(step // 2, 1)
    for where, _, _ in sources:
        sx, sy, sz = (float(v[0]) for v in camera.view(params, w, h, q=camera.other(where[None])))
        row, column = int(np.clip(sy // step, 0, mask.shape[0] - 1)), int(np.clip(sx // step, 0, mask.shape[1] - 1))
        patch = patches[max(row - 1, 0):row + 2, max(column - 1, 0):column + 2].max()
        if not patch:
            continue
        inside = patches == patch
        py, px = np.clip((y // step).astype(int), 0, mask.shape[0] - 1), np.clip((x // step).astype(int), 0, mask.shape[1] - 1)
        ahead = inside[py, px] & (z > sz + 0.01) & (x >= 0) & (x < w) & (y >= 0) & (y < h)
        cells = (y[ahead] // fine).astype(np.int64) * (w // fine + 1) + (x[ahead] // fine).astype(np.int64)
        total = inside.sum() * (step // fine) ** 2
        for part in np.unique(dense_part[ahead]):
            covered = len(np.unique(cells[dense_part[ahead] == part]))
            if covered >= GLASS_COVER * total:
                glass[part] = True
    return glass


def light_profile(dense, part, sources, see_through):
    """How much of a source's light leaves towards each slice of directions, from straight down (first) to
    straight up (last), 16 slices of equal solid angle: 1 = nothing in the way (a bare bulb), 0 = all stopped.
    The model's surfaces are sampled densely (finer than a perforation); seen from the source, each small cell of
    directions is as closed as the most opaque surface found in it. `see_through` = share of light each part
    lets through (fabric, opal glass). What is within BULB of the source is the bulb and its socket: left out."""
    points = dense
    opacity = (1.0 - see_through[part]).astype(np.float32)
    total = np.zeros(SLICES)
    for source in sources:
        away = points - source
        distance = np.linalg.norm(away, axis=1)
        keep = distance > BULB
        away, closed = away[keep] / distance[keep, None], opacity[keep]
        rows = np.clip(((1 + away[:, 1]) / 2 * CELLS).astype(int), 0, CELLS - 1)          # down .. up
        columns = np.clip(((np.arctan2(away[:, 2], away[:, 0]) / (2 * np.pi) + 0.5) * 2 * CELLS).astype(int), 0, 2 * CELLS - 1)
        grid = np.zeros((CELLS, 2 * CELLS), np.float32)
        order = np.argsort(closed, kind="stable")          # written last = the most opaque surface of the cell
        grid[rows[order], columns[order]] = closed[order]
        total += (1 - grid).reshape(SLICES, -1).mean(1)
    return [round(float(v), 3) for v in total / len(sources)]


def luminance(rgb):
    return (rgb @ np.array([0.2126, 0.7152, 0.0722])) / 255


def fill_hidden(table, parts, tri_count, centres):
    """A part the photo does not show takes the colour of its twins (same component, same factory material, about
    the same size); without a twin, of the nearest part the photo shows, of its factory material first: what
    touches a hidden part is most often made of the same thing (the far half of a wall plate, of a rod)."""
    known = ~np.isnan(table[:, 0])
    source = np.where(known, "photo", "").astype(object)
    seen = np.flatnonzero(known)
    for i, part in enumerate(parts):
        if known[i]:
            continue
        twins = [j for j in seen if parts[j]["definition"] == part["definition"] and parts[j]["mtl"] == part["mtl"]
                 and 0.7 < tri_count[j] / max(tri_count[i], 1) < 1.4]
        if twins:
            weights = tri_count[twins].astype(float)
            table[i] = (table[twins] * weights[:, None]).sum(0) / weights.sum()
            source[i] = "twin"
            continue
        same = [j for j in seen if parts[j]["mtl"] == part["mtl"]]
        pool = np.array(same if same else seen)
        table[i] = table[pool[np.argmin(np.linalg.norm(centres[pool] - centres[i], axis=1))]]
        source[i] = "voisine"
    return source


def group_colours(colours, kinds):
    """Greedy: parts of one kind (0 matter, 1 light, 2 clear glass) whose colours are close share a material.
    -> material id per part, [(colour, kind, parts)]"""
    materials, owner = [], np.zeros(len(colours), int)
    for i in np.argsort(-colours.sum(1)):
        for m, (colour, kind, members) in enumerate(materials):
            if kind == kinds[i] and np.linalg.norm(colour - colours[i]) < SAME_COLOUR:
                owner[i] = m; members.append(i); break
        else:
            owner[i] = len(materials); materials.append((colours[i], kinds[i], [i]))
    return owner, materials


def write_glb(path, pos, nor, corners, tri_material, tri_node, nodes, materials, extras):
    """One mesh per node, one primitive per material in it; positions in metres, relative to the node's origin."""
    chunks, views, accessors, meshes, gltf_nodes = [], [], [], [], []
    offset = 0

    def add(data, target):
        nonlocal offset
        raw = data.tobytes()
        pad = (-len(raw)) % 4
        views.append({"buffer": 0, "byteOffset": offset, "byteLength": len(raw), "target": target})
        chunks.append(raw + b"\0" * pad)
        offset += len(raw) + pad
        return len(views) - 1

    for node_id, (node_name, origin) in enumerate(nodes):
        primitives = []
        for m in range(len(materials)):
            mine = corners[(tri_material == m) & (tri_node == node_id)].reshape(-1, 2)
            if not len(mine):
                continue
            keys, index = np.unique(mine[:, 0] * (len(nor) + 2) + mine[:, 1] + 1, return_inverse=True)
            vertex, normal = keys // (len(nor) + 2), keys % (len(nor) + 2) - 1
            p = (pos[vertex] - origin).astype(np.float32)
            n = (nor[normal] if len(nor) else np.tile((0, 1, 0), (len(keys), 1))).astype(np.float32)
            n /= np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-9)
            accessors += [
                {"bufferView": add(p, 34962), "componentType": 5126, "count": len(p), "type": "VEC3",
                 "min": p.min(0).tolist(), "max": p.max(0).tolist()},
                {"bufferView": add(n, 34962), "componentType": 5126, "count": len(n), "type": "VEC3"},
                {"bufferView": add(index.astype(np.uint32), 34963), "componentType": 5125, "count": len(index), "type": "SCALAR"}]
            a = len(accessors)
            primitives.append({"attributes": {"POSITION": a - 3, "NORMAL": a - 2}, "indices": a - 1, "material": m})
        if primitives:
            meshes.append({"primitives": primitives})
            gltf_nodes += [{"name": node_name, "translation": [float(v) for v in origin], "children": [len(gltf_nodes) + 1]},
                           {"mesh": len(meshes) - 1, "name": node_name + "-forme"}]
    gltf = {"asset": {"version": "2.0", "generator": "essayage e3d"}, "scene": 0,
            "scenes": [{"nodes": list(range(0, len(gltf_nodes), 2))}], "nodes": gltf_nodes, "meshes": meshes,
            "materials": materials, "buffers": [{"byteLength": offset}], "bufferViews": views, "accessors": accessors,
            "extras": extras}
    text = json.dumps(gltf, separators=(",", ":")).encode()
    text += b" " * ((-len(text)) % 4)
    binary = b"".join(chunks)
    with open(path, "wb") as f:
        f.write(struct.pack("<4sII", b"glTF", 2, 28 + len(text) + len(binary)))
        f.write(struct.pack("<I4s", len(text), b"JSON") + text)
        f.write(struct.pack("<I4s", len(binary), b"BIN\0") + binary)


def proof(path, photo, camera, params, tris, tri_colour, pos_q, outline, tri_glass=None):
    """photo | the model drawn from the found camera (clear glass drawn see-through, over the rest)."""
    w, h = photo.size
    x, y, z = camera.view(params, w, h, q=pos_q)
    tz = z[tris].mean(1)
    a, b, c = pos_q[tris[:, 0]], pos_q[tris[:, 1]], pos_q[tris[:, 2]]
    normal = np.cross(b - a, c - a) @ rotation(*params[:3]).T
    shade = 0.55 + 0.45 * np.abs(normal @ np.array([0.25, 0.5, 0.83])) / np.maximum(np.linalg.norm(normal, axis=1), 1e-12)
    tri_glass = np.zeros(len(tris), bool) if tri_glass is None else tri_glass
    drawn = Image.new("RGBA", (w, h), (236, 234, 229, 255))
    veil = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    solid_draw, glass_draw = ImageDraw.Draw(drawn), ImageDraw.Draw(veil)
    for i in np.argsort(tz):
        t = tris[i]
        colour = tuple(int(v) for v in np.clip(tri_colour[i] * shade[i], 0, 255))
        corners = [(x[t[0]], y[t[0]]), (x[t[1]], y[t[1]]), (x[t[2]], y[t[2]])]
        if tri_glass[i]:
            glass_draw.polygon(corners, fill=colour + (round(255 * GLASS_ALPHA),))
        else:
            solid_draw.polygon(corners, fill=colour + (255,))
    drawn = Image.alpha_composite(drawn, veil).convert("RGB")
    sheet = Image.new("RGB", (w * 2, h), (236, 234, 229))
    sheet.paste(photo.convert("RGBA"), (0, 0), photo.convert("RGBA"))
    sheet.paste(drawn, (w, 0))
    ImageDraw.Draw(sheet).text((12, 8), f"photo | modele 3D (contours {outline:.3f})", fill=(200, 0, 0))
    sheet.thumbnail((1600, 1600))
    sheet.save(path, quality=86)


def wall_turn(pos, tris, params, lying):
    """How to turn a wall fitting's file so that its back is at z smallest and its top at y largest, whatever way
    the manufacturer drew it (`lying`: drawn as a ceiling light; its top is then what the photo shows as up).
    -> rotation matrix (rows = new axes)
    The side that goes against the wall is one of the upright sides of its box:
    - a plate (its thinnest size under PLATE of its largest: a disc, a plank) can only have one of its two faces
      there; its mount is a small flat base and its front a large flat face: the face that holds the least flat
      surface, among those that hold some (FLAT_MIN mm2 lying on the side and facing it);
    - any other fitting is held by a base: something that touches one side of the box exactly, over a compact
      outline (BASE_MIN mm wide at least, no longer than BASE_LONG times its width: the flat facet of a round
      shade is a long strip, a globe touches by a point). The largest one is the back; a product photo being taken from the room, a base that faces the
      photo's camera gives way to another one when there is one. No base at all: the side the camera does not see."""
    turn = rotation(*params[:3])
    to_camera, up_seen = turn[2], turn[1]
    centre = pos[tris].mean(1)
    a, b, c = pos[tris[:, 0]], pos[tris[:, 1]], pos[tris[:, 2]]
    normal = np.cross(b - a, c - a)
    area = np.linalg.norm(normal, axis=1)
    normal = normal / np.maximum(area, 1e-12)[:, None]
    sides = [np.array(v, float) for v in ((0, 0, -1), (1, 0, 0), (0, 0, 1), (-1, 0, 0), (0, 1, 0), (0, -1, 0))]

    def flat(side):
        """Surface lying flat on that side of the box (mm2)."""
        along = centre @ side
        return float(area[(along.max() - along < 1.5) & (np.abs(normal @ side) > 0.9)].sum()) / 2

    def base(side):
        """The footprint of what touches that side of the box exactly (corners within 0.1 mm of it): its width
        times its length, or 0 when it is not a base. A base may be hollow (a cup turned to the wall touches it
        by its rim only): its outline counts, not its surface."""
        along = pos @ side
        spread = np.sort(np.ptp(pos[along.max() - along < 0.1], axis=0) * (1 - np.abs(side)))[1:]
        return float(spread[0] * spread[1]) if spread[0] >= BASE_MIN and spread[1] <= BASE_LONG * spread[0] else 0.0

    held = {i: flat(side) for i, side in enumerate(sides)}
    size = np.ptp(pos, axis=0)
    if size.min() < PLATE * size.max():
        faces = [i for i, side in enumerate(sides) if abs(side[int(np.argmin(size))]) == 1]
        some = [i for i in faces if held[i] >= FLAT_MIN]
        back = min(some, key=held.get) if some else max(faces, key=held.get)
        out = sides[back]
        top = max((side for side in sides if abs(side @ out) < 0.5), key=lambda side: side @ up_seen)
    else:
        top = max(sides, key=lambda side: side @ up_seen) if lying else sides[4]
        upright = [i for i, side in enumerate(sides) if abs(side @ top) < 0.5]
        feet = {i: base(sides[i]) for i in upright}
        bases = sorted((i for i in upright if feet[i]), key=lambda i: -feet[i])
        if len(bases) > 1 and sides[bases[0]] @ to_camera > 0.5:
            bases = bases[1:]
        out = sides[bases[0]] if bases else min((sides[i] for i in upright), key=lambda side: side @ to_camera)
    return np.stack([np.cross(top, -out), top, -out])


def side_view(path, metres, tris, tri_colour):
    """A wall fitting seen from its side, the wall drawn as a line on the left: what proves that its back, and
    not its face, is against the wall."""
    scale = 560 / max(np.ptp(metres[:, 1]), np.ptp(metres[:, 2]), 1e-6)
    x = 60 + (metres[:, 2] - metres[:, 2].min()) * scale
    y = 20 + (metres[:, 1].max() - metres[:, 1]) * scale
    picture = Image.new("RGB", (int(x.max()) + 40, int(y.max()) + 20), (236, 234, 229))
    draw = ImageDraw.Draw(picture)
    for i in np.argsort(metres[tris][:, :, 0].mean(1)):
        t = tris[i]
        draw.polygon([(x[t[0]], y[t[0]]), (x[t[1]], y[t[1]]), (x[t[2]], y[t[2]])],
                     fill=tuple(int(v) for v in np.clip(tri_colour[i], 0, 255)))
    draw.rectangle([44, 0, 58, picture.height], fill=(120, 120, 120))
    draw.text((4, 4), "mur", fill=(200, 0, 0))
    picture.save(path, quality=84)


def make(obj, unlit_path, lit_path, pose, out, name, size_mm=None, origin=None):
    pos, nor, corners, tri_part, parts, unit = load_obj(obj, size_mm)
    tris = corners[:, :, 0]
    tri_count = np.bincount(tri_part, minlength=len(parts))
    unlit, lit = Image.open(unlit_path), Image.open(lit_path)
    alpha = unlit.getchannel("A")
    k = FIT_SIDE / max(alpha.size)
    target = np.asarray(alpha.resize((max(1, round(alpha.width * k)), max(1, round(alpha.height * k))), Image.Resampling.BOX)) > 90
    if pose == "mur":
        # first the photo's camera on the file as it is drawn, to know its wall side and its top; then the file is
        # turned, and everything below works on a fitting that stands as on its wall
        rough = sample(pos, tris, tri_part, 400_000)[0]
        centre, radius = (pos.min(0) + pos.max(0)) / 2, np.linalg.norm(pos.max(0) - pos.min(0)) / 2
        first = Camera(rough, centre, radius)
        upright, seen_from = fit_camera(first, target)
        lying = False
        if upright < 0.85:
            other, from_any_side = fit_camera(first, target, any_way_up=True)
            lying = other > upright + LYING
            seen_from = from_any_side if lying else seen_from
        turn = wall_turn(pos, tris, seen_from, lying)
        pos = pos @ turn.T
        nor = nor @ turn.T if len(nor) else nor
    points, part_of_point, area = sample(pos, tris, tri_part, 400_000)
    centre = (pos.min(0) + pos.max(0)) / 2
    radius = np.linalg.norm(pos.max(0) - pos.min(0)) / 2
    zone = cable_zone(points) if pose == "plafond" else None
    camera = Camera(points, centre, radius, zone)
    outline, params = fit_camera(camera, target)
    near = outline_near(camera, params, target)
    full = None
    if outline < MIN_OUTLINE and near < MIN_NEAR:
        # the photo's cut-out may have lost the inside of the fitting (a white diffuser on a light ground): the
        # outer outlines alone, holes filled on both sides, are fitted before the model is refused
        full, outer = fit_camera(camera, binary_fill_holes(target), whole=True)
        if full >= MIN_WHOLE:
            params = outer
        else:
            camera.view(params, *unlit.size)
            proof(out / f"{name}-refuse.jpg", lit, camera, params, tris, np.full((len(tris), 3), 150.0), camera.other(pos), outline)
            raise Refused(f"the 3D file's outline fits the photo at {outline:.2f} only (< {MIN_OUTLINE}), side by side "
                          f"at {near:.2f} (< {MIN_NEAR}), outer outlines at {full:.2f} (< {MIN_WHOLE})")
    core = bright_core(unlit, lit)
    dense, dense_part, _ = sample(pos, tris, tri_part, PROFILE_POINTS)

    def read(solid):
        """Colours, gain and what glows, with the points of `solid` parts only hiding what is behind them."""
        (base, seen), (glow, _), in_core = seen_colours(camera, params, part_of_point, (unlit, lit), len(parts), core, solid)
        gain = np.where(np.isnan(base[:, 0]), 0.0, luminance(np.nan_to_num(glow)) - luminance(np.nan_to_num(base)))
        # what glows: a part that gets much brighter, or whose seen surface is mostly the photo's bright core (an
        # opal globe is white unlit and white lit: it gains little, yet it is the light)
        return base, glow, seen, in_core, gain, (gain > GLOW_GAIN) | ((in_core > 0.5) & (seen >= 12))

    base, glow, seen, in_core, gain, glows = read(np.ones(len(points), bool))
    found = light_sources(camera, params, points, core)
    # what stands between a source and the camera while the photo still shows the light: clear glass when the
    # light is a small spot seen through it (a filament in a globe); a veil when the part itself is bright over a
    # good share of its surface (a fabric or opal shade lit from inside): a veil glows, it is not see-through
    over = clear_glass(camera, params, dense, dense_part, len(parts), core, found) & (seen >= 12) & ~glows
    glass = over & (in_core < VEIL_SHARE)
    # twins agree: of several like parts the photo shows (four shades of one chandelier), one alone is not glass
    for i in np.flatnonzero(glass):
        twins = [j for j in np.flatnonzero(seen >= 12) if parts[j]["definition"] == parts[i]["definition"]
                 and parts[j]["mtl"] == parts[i]["mtl"] and 0.7 < tri_count[j] / max(tri_count[i], 1) < 1.4]
        if 2 * sum(over[j] and in_core[j] < VEIL_SHARE for j in twins) < len(twins):
            glass[i] = False
    veil = over & ~glass & (in_core >= VEIL_SHARE)
    if glass.any():
        # behind clear glass the photo shows the inside: read again with the glass out of the way
        inner = read(~glass[part_of_point])
        keep = glass[:, None]
        base, glow = np.where(keep, base, inner[0]), np.where(keep, glow, inner[1])
        seen, in_core, gain = (np.where(glass, mine, theirs) for mine, theirs in zip((seen, in_core, gain), inner[2:5]))
        glows = inner[5] & ~glass
    glows |= veil
    tri_centre = pos[tris].mean(1)
    centres = np.stack([np.bincount(tri_part, weights=tri_centre[:, k], minlength=len(parts)) for k in range(3)], axis=1) / np.maximum(tri_count, 1)[:, None]
    source = fill_hidden(base, parts, tri_count, centres)
    # twins of a glowing part glow too (a bulb hidden behind a shade in the photo)
    for i, part in enumerate(parts):
        if source[i] == "twin" and not glows[i]:
            glows[i] = any(glows[j] and other["definition"] == part["definition"] and other["mtl"] == part["mtl"]
                           for j, other in enumerate(parts) if source[j] == "photo")
    lit_colour = np.where(np.isnan(glow), base, glow)
    # a bulb the photo does not show (behind a shade) glows all the same: a part that holds entirely within BULB
    # of a source is that source's bulb
    for where, _, _ in found:
        reach = np.linalg.norm(pos[tris] - where, axis=2).max(1)
        bulb = (np.bincount(tri_part, weights=reach < BULB, minlength=len(parts)) == tri_count) & ~glass & ~glows
        lit_colour[bulb] = BULB_LIGHT       # the photo never showed it lit: it glows as a bulb does
        glows |= bulb
    glass &= ~glows
    owner, groups = group_colours(base, np.where(glass, 2, glows.astype(int)))
    materials = []
    for colour, kind, members in groups:
        linear = (np.clip(colour, 0, 255) / 255) ** 2.2
        material = {"name": ("matiere", "lumiere", "verre")[kind] + f"-{len(materials)}", "doubleSided": True,
                    "pbrMetallicRoughness": {"baseColorFactor": [*linear.round(4).tolist(), 1.0],
                                             "metallicFactor": 0.0, "roughnessFactor": 0.8}}
        if kind == 2:
            material["alphaMode"] = "BLEND"
            material["pbrMetallicRoughness"]["baseColorFactor"][3] = GLASS_ALPHA
            material["pbrMetallicRoughness"]["roughnessFactor"] = 0.1
            material["extras"] = {"essayage": "verre"}
        if kind == 1:
            weights = tri_count[members].astype(float)
            emitted = (lit_colour[members] * weights[:, None]).sum(0) / weights.sum()
            material["emissiveFactor"] = ((np.clip(emitted, 0, 255) / 255) ** 2.2).round(4).tolist()
            material["extras"] = {"essayage": "lumiere"}
        materials.append(material)
    # origin: where the fitting meets the room (ceiling: middle of its top; wall: middle of its back)
    top = pos[:, 1] >= pos[:, 1].max() - 0.02 * (pos[:, 1].max() - pos[:, 1].min())
    hang = np.array([pos[top, 0].mean(), pos[:, 1].max(), pos[top, 2].mean()]) if pose == "plafond" else \
        np.array([centre[0], centre[1], pos[:, 2].min()])
    metres = (pos - hang) / 1000
    guessed = not found
    if guessed:
        # no bright patch on the photo: one source in the middle of what hangs (of the whole fitting on a wall)
        body = pos if zone is None else pos[pos[:, 1] < zone[0]]
        found = [((body.min(0) + body.max(0)) / 2, None, 1)]
    sources = [{"p": ((where - hang) / 1000).round(4).tolist()} for where, _, _ in found]
    # a part that brightens when lit without being a source lets light through (fabric, opal glass)
    see_through = np.clip((gain - 0.05) / 0.5, 0.0, 0.85) * (source == "photo")
    for i, part in enumerate(parts):
        if source[i] == "twin":
            twins = [j for j, other in enumerate(parts) if source[j] == "photo" and other["definition"] == part["definition"] and other["mtl"] == part["mtl"]]
            see_through[i] = max((see_through[j] for j in twins), default=0.0)
    see_through = np.where(glows, 0.85, see_through)        # a part that is the light itself (a globe, a diffuser)
    see_through = np.where(glass, 0.9, see_through)
    if guessed:
        # the photos show no bright spot: a fitting that glows softly all over (a fabric shade); what hangs lets
        # SOFT_THROUGH of the light through, in every direction
        low = pos[tris].mean(1)[:, 1] < (zone[0] if zone is not None else np.inf)
        soft = np.bincount(tri_part[low], minlength=len(parts)) > 0.5 * tri_count
        see_through = np.where(soft, np.maximum(see_through, SOFT_THROUGH), see_through)
    profile = light_profile(dense, dense_part, [where for where, _, _ in found], see_through)
    # nodes: "haut" stays at the ceiling, "tige" is the cable or rods (the viewer stretches it), "bas" hangs
    centre_y = pos[tris].mean(1)[:, 1]
    if zone is None:
        tri_node, nodes = np.zeros(len(tris), int), [("haut", np.zeros(3))]
    else:
        tri_node = np.where(centre_y > zone[1], 0, np.where(centre_y < zone[0], 2, 1))
        nodes = [("haut", np.zeros(3)), ("tige", np.array([0, (zone[1] - hang[1]) / 1000, 0])), ("bas", np.zeros(3))]
    size = (pos.max(0) - pos.min(0)) / 1000
    # origin: the photo and the manufacturer's file this model was made from (a later run skips a product whose
    # model already comes from the same two)
    model = {"v": 2, **(origin or {}), "pose": pose, "taille_m": size.round(4).tolist(),
             "sources": sources, "profil": profile,
             "suspension": None if zone is None else {"haut_m": round((zone[1] - hang[1]) / 1000, 4),
                                                      "longueur_m": round((zone[1] - zone[0]) / 1000, 4),
                                                      "photo": round(float(camera.keep), 3)},
             "preuve": {"contours": round(float(outline), 4), "contours_proches": round(near, 4),
                        "contours_pleins": None if full is None else round(float(full), 4), "camera": [round(float(v), 4) for v in params],
                        "unite": unit, "source_devinee": guessed,
                        "pieces": len(parts), "pieces_vues": int((source == "photo").sum()),
                        "grandes_pieces": [{"triangles": int(tri_count[i]), "couleur": [int(v) for v in base[i]],
                                            "gain": round(float(gain[i]), 3), "coeur": round(float(in_core[i]), 2),
                                            "lumiere": bool(glows[i]), "verre": bool(glass[i]), "laisse_passer": round(float(see_through[i]), 2),
                                            "vue": source[i]} for i in np.argsort(-tri_count)[:12]],
                        "triangles": int(len(tris)), "matieres": len(materials),
                        "matieres_lumiere": int(sum(g[1] == 1 for g in groups)),
                        "matieres_verre": int(sum(g[1] == 2 for g in groups))}}
    raw = out / f"{name}-brut.glb"
    write_glb(raw, metres, nor, corners, owner[tri_part], tri_node, nodes, materials, {"essayage": model})
    model["preuve"]["octets"] = pack(raw, out / f"{name}.glb", len(tris))
    raw.unlink()
    (out / f"{name}.json").write_text(json.dumps(model, ensure_ascii=False, indent=1), encoding="utf-8")
    camera.view(params, *unlit.size)
    tri_colour = np.where(glows[tri_part][:, None], lit_colour[tri_part], base[tri_part])
    proof(out / f"{name}-preuve.jpg", lit, camera, params, tris, tri_colour, camera.other(pos), outline, glass[tri_part])
    if pose == "mur":
        side_view(out / f"{name}-profil.jpg", metres, tris, tri_colour)
    print(name, json.dumps(model["preuve"]), "sources", len(model["sources"]))


def pack(raw, final, triangles):
    """The file a phone downloads: same model, compressed (meshopt), thinned when it has more triangles than a
    phone draws at ease. Node and material names are kept: the viewer finds the cable and the lights by them."""
    command = ["npx", "--yes", GLTF_TOOL, "optimize", str(raw), str(final), "--compress", "meshopt",
               "--flatten", "false", "--join", "false", "--instance", "false", "--palette", "false",
               "--texture-compress", "false", "--weld", "true"]
    command += (["--simplify", "true", "--simplify-ratio", f"{MOST_TRIANGLES / triangles:.3f}", "--simplify-error", "0.001"]
                if triangles > MOST_TRIANGLES else ["--simplify", "false"])
    done = subprocess.run(command, capture_output=True, text=True, shell=os.name == "nt")
    if done.returncode or not final.is_file():
        raise Refused(f"the 3D file could not be compressed: {(done.stderr or done.stdout)[-300:]}")
    return final.stat().st_size


def model_file(source, work):
    """The manufacturer's 3D file: an https address of an .obj, or of a zip that holds one (the largest is taken)."""
    if not source.startswith("https://"):
        raise Refused("source_3d must be an https address")
    work.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(source, headers={"User-Agent": "essayage-modele"})
    with urllib.request.urlopen(request, timeout=300) as answer:
        body = answer.read(MOST_BYTES + 1)
    if len(body) > MOST_BYTES:
        raise Refused(f"3D file larger than {MOST_BYTES // 1_000_000} MB")
    path = work / "modele.obj"
    if body[:2] == b"PK":
        with zipfile.ZipFile(io.BytesIO(body)) as archive:
            inside = [i for i in archive.infolist() if i.filename.lower().endswith(".obj")]
            if not inside:
                raise Refused("no .obj in the manufacturer's 3D archive: " + ", ".join(i.filename for i in archive.infolist())[:200])
            path.write_bytes(archive.read(max(inside, key=lambda i: i.file_size)))
    else:
        path.write_bytes(body)
    return path


def main():
    """python scripts/essayage_3d.py LOT_DIR   after essayage_modele.py assemble: every model of demande.json that
    names a "source_3d" gets out/essayage3d/<nom>.glb, <nom>.json and <nom>-preuve.jpg, made from the two
    cut-outs out/essayage/<nom>-eteint.webp and -allume.webp. One model failing does not stop the others; the run
    ends in error and names them (lines starting "FAILED")."""
    lot = Path(sys.argv[1])
    cut, out, work = ROOT / "out" / "essayage", ROOT / "out" / "essayage3d", ROOT / "out" / "essayage3d-travail"
    out.mkdir(parents=True, exist_ok=True)
    failed = []
    for m in json.loads((lot / "demande.json").read_text(encoding="utf-8")).get("modeles") or []:
        name = str(m.get("nom", ""))
        if not m.get("source_3d"):
            print(f"NOTE {name}: no 3D file named in the request, no 3D model")
            continue
        try:
            obj = model_file(m["source_3d"], work / name)
            size_cm = m.get("taille_cm") or max(m.get("cotes_cm") or [0])
            origin = {"photo": str(m.get("allume", "")).split("?")[0].rsplit("/", 1)[-1],
                      "source": m["source_3d"].split("?")[0].rsplit("/", 1)[-1]}
            make(obj, cut / f"{name}-eteint.webp", cut / f"{name}-allume.webp", m["pose"], out, name, size_cm * 10 or None, origin)
        except Refused as reason:
            failed.append(f"{name}: {reason}")
        except Exception as error:                     # one broken file must not cost the lot
            failed.append(f"{name}: {type(error).__name__}: {error}")
    for line in failed:
        print(f"FAILED: {line}")
        if os.environ.get("GITHUB_ACTIONS"):
            print(f"::error title=3D model failed::{line}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
