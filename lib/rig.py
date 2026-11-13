"""Armature and animation clips for rigged assets (round 3).

zoo.finish() calls build(ob, joints) when a generator declared joints. Weights are rigid: every part follows exactly
one bone (the toy look hides the small gaps at joints). Clips are made from the bone names that exist, so one set of
clips serves every 4-leg body plan:
  walk (24 frames, loop): diagonal leg pairs swing, body bobs, neck nods, tail sways
  idle (48 frames, loop): breathing, slow head turn, tail flick
  eat  (48 frames, loop): neck and head go down, chew, come back up
Bone names: root, body, neck, head, tail, leg_FL, leg_FR, leg_BL, leg_BR (F = front, at -Y).
"""
import math

import bpy
from mathutils import Vector

FPS = 24
CLIPS = {"walk": 24, "idle": 48, "eat": 48}
FLY = 24  # birds (bones wing_L / wing_R) also get a fly clip of this many frames


def build(ob, joints):
    name = ob.name.replace("SM_", "RIG_", 1)
    arm_d = bpy.data.armatures.new(name)
    arm = bpy.data.objects.new(name, arm_d)
    bpy.context.scene.collection.objects.link(arm)
    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.view_layer.objects.active = arm
    arm.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    size = max(ob.dimensions) or 1.0
    root = arm_d.edit_bones.new("root")
    root.head, root.tail = (0, 0, 0), (0, -0.15 * size, 0)
    eb = {"root": root}
    for n, (h, t, _) in joints.items():
        b = arm_d.edit_bones.new(n)
        b.head, b.tail = h, t
        if (b.tail - b.head).length < 1e-4:
            b.tail = b.head + Vector((0, 0, 0.05 * size))
        eb[n] = b
    for n, (_, _, par) in joints.items():
        eb[n].parent = eb.get(par, root)
    bpy.ops.object.mode_set(mode="OBJECT")
    ob.parent = arm
    md = ob.modifiers.new("Armature", "ARMATURE")
    md.object = arm
    for pb in arm.pose.bones:
        pb.rotation_mode = "XYZ"
    _clips(arm, max(ob.dimensions.z, 0.05))
    return arm


def _key(pb, frame, rot=None, loc=None, scale=None):
    if rot is not None:
        pb.rotation_euler = tuple(math.radians(a) for a in rot)
        pb.keyframe_insert("rotation_euler", frame=frame)
    if loc is not None:
        pb.location = loc
        pb.keyframe_insert("location", frame=frame)
    if scale is not None:
        pb.scale = scale
        pb.keyframe_insert("scale", frame=frame)


def _eat_angle(arm, h):
    """Neck bend (degrees; the head adds 0.6x) that brings the nose to just above the ground, capped at 60."""
    pb = arm.pose.bones
    if "head" not in pb:
        return 0.0
    neck = pb.get("neck")
    pivot = arm.matrix_world @ (neck or pb["head"]).head
    reach0 = pivot.y - (arm.matrix_world @ pb["head"].tail).y  # how far the nose is in front of the pivot (-Y)
    best = 0.0
    for ang in range(0, 61, 2):
        if neck:
            neck.rotation_euler = (math.radians(ang), 0, 0)
        pb["head"].rotation_euler = (math.radians(ang * 0.6), 0, 0)
        bpy.context.view_layer.update()
        tip = arm.matrix_world @ pb["head"].tail
        if pivot.y - tip.y < 0.55 * reach0:  # nose swinging back under the chest: stop before this step
            break
        best = ang
        if tip.z <= 0.2 * h:
            break
    for b in pb:
        b.rotation_euler = (0, 0, 0)
    bpy.context.view_layer.update()
    return float(best)


def _clips(arm, h):
    """h = model height in metres (scales the walk bob and the eat target)."""
    pb = arm.pose.bones
    has = lambda n: n in pb
    ad = arm.animation_data_create()
    if "trunk" in pb:
        return _plant_clips(arm, h)
    eat = _eat_angle(arm, h)
    clips = dict(CLIPS)
    if has("wing_L"):
        clips["fly"] = FLY
    if not any(n.startswith(("leg_", "arm_", "wing_")) for n in pb.keys()) and "neck" not in pb:
        del clips["walk"]  # legless swimmers (sea animals) get swim instead
        clips["swim"] = 24
        clips["crawl"] = 24  # RIGS.md insect row requires crawl; same body wave as swim
    for clip, n in clips.items():
        for b in pb:  # each clip starts from the rest pose
            b.rotation_euler = (0, 0, 0); b.location = (0, 0, 0); b.scale = (1, 1, 1)
        ad.action = None
        for f in range(n + 1):
            ph = 2 * math.pi * f / n
            if clip == "walk":
                for leg, off in (("leg_FL", 0), ("leg_BR", 0), ("leg_FR", math.pi), ("leg_BL", math.pi)):
                    if has(leg):
                        _key(pb[leg], f, rot=(22 * math.sin(ph + off), 0, 0))
                for leg, off in (("leg_L", 0), ("leg_R", math.pi)):  # two-leg walkers
                    if has(leg):
                        _key(pb[leg], f, rot=(25 * math.sin(ph + off), 0, 0))
                if has("body"):
                    _key(pb["body"], f, loc=(0, 0, 0.012 * h * abs(math.sin(ph))), rot=(0, 2 * math.sin(ph), 0))
                if has("neck"):
                    _key(pb["neck"], f, rot=(5 * math.sin(2 * ph), 0, 0))
                if has("head"):
                    _key(pb["head"], f, rot=(-4 * math.sin(2 * ph), 0, 3 * math.sin(ph)))
                if has("tail"):
                    _key(pb["tail"], f, rot=(0, 0, 18 * math.sin(ph)))
            elif clip == "fly":
                for wing, sgn in (("wing_L", -1), ("wing_R", 1)):
                    if has(wing):  # bone points down, local Z = world Y: flap up and out, then down
                        _key(pb[wing], f, rot=(0, 0, sgn * (10 + 45 * math.sin(ph))))
                if has("body"):
                    _key(pb["body"], f, loc=(0, 0, 0.03 * h * math.sin(ph + 1.2)))
                if has("neck"):
                    _key(pb["neck"], f, rot=(-8, 0, 0))
                if has("head"):
                    _key(pb["head"], f, rot=(4, 0, 0))
                for leg in ("leg_L", "leg_R"):
                    if has(leg):
                        _key(pb[leg], f, rot=(-35, 0, 0))
                if has("tail"):
                    _key(pb["tail"], f, rot=(10 * math.sin(ph), 0, 0))
            elif clip in ("swim", "crawl"):  # body rolls and bobs, tail beats in both axes, head counters
                _key(pb["body"], f, loc=(0, 0, 0.02 * h * math.sin(ph)), rot=(0, 3 * math.sin(ph), 4 * math.sin(ph)))
                if has("tail"):
                    _key(pb["tail"], f, rot=(12 * math.sin(ph + 1), 0, 25 * math.sin(ph)))
                if has("head"):
                    _key(pb["head"], f, rot=(3 * math.sin(ph), 0, -6 * math.sin(ph)))
            elif clip == "idle":
                if has("body"):
                    s = 1 + 0.015 * math.sin(2 * ph)
                    _key(pb["body"], f, scale=(s, 1, s))
                if has("head"):
                    _key(pb["head"], f, rot=(3 * math.sin(2 * ph), 0, 16 * math.sin(ph)))
                if has("neck"):
                    _key(pb["neck"], f, rot=(3 * math.sin(ph), 0, 4 * math.sin(ph)))
                if has("tail"):
                    flick = 25 * math.sin(4 * ph) * max(0.0, math.sin(ph))
                    _key(pb["tail"], f, rot=(0, 0, flick))
            elif clip == "eat":
                t = f / n
                down = math.sin(math.pi * min(1.0, t / 0.8)) ** 0.5 if t < 0.8 else 0.0  # ease down, hold, up
                chew = 4 * math.sin(6 * ph) * down
                if has("neck"):
                    _key(pb["neck"], f, rot=(eat * down, 0, 0))
                if has("head") and not has("neck"):  # head-only bone points -Y: local +X lifts the nose, so go negative
                    _key(pb["head"], f, rot=(-35 * down + chew, 0, 0))
                elif has("head"):
                    _key(pb["head"], f, rot=(eat * 0.6 * down + chew, 0, 0))
                elif has("body"):
                    _key(pb["body"], f, rot=(6 * down, 0, 0))
                if has("tail"):
                    _key(pb["tail"], f, rot=(0, 0, 8 * math.sin(ph)))
        act = ad.action
        if act is None:
            continue
        act.name = clip
        act.use_fake_user = True
        track = ad.nla_tracks.new()
        track.name = clip
        track.strips.new(clip, 0, act)
        track.mute = True  # tracks are for export; the scene shows the rest pose
        ad.action = None
    for b in pb:
        b.rotation_euler = (0, 0, 0); b.location = (0, 0, 0); b.scale = (1, 1, 1)


def _plant_clips(arm, h):
    """Plants: idle (48, tiny crown breathing) and sway (48, trunk and crown lean with a phase lag)."""
    pb = arm.pose.bones
    ad = arm.animation_data_create()
    for clip, n in (("idle", 48), ("sway", 48)):
        for b in pb:
            b.rotation_euler = (0, 0, 0); b.location = (0, 0, 0); b.scale = (1, 1, 1)
        ad.action = None
        amp = 1.0 if clip == "idle" else 5.0
        for f in range(n + 1):
            ph = 2 * math.pi * f / n
            _key(pb["trunk"], f, rot=(0.3 * amp * math.sin(ph + 0.6), 0, 0.5 * amp * math.sin(ph)))
            _key(pb["crown"], f, rot=(0.6 * amp * math.sin(ph), 0, 1.0 * amp * math.sin(ph - 0.8)))
        act = ad.action
        act.name = clip
        act.use_fake_user = True
        track = ad.nla_tracks.new()
        track.name = clip
        track.strips.new(clip, 0, act)
        track.mute = True
        ad.action = None
    for b in pb:
        b.rotation_euler = (0, 0, 0); b.location = (0, 0, 0); b.scale = (1, 1, 1)
