"""Clips for the shared human skeleton (keepers and visitors), round 3.

Bones: root, body (pelvis and torso), head, arm_L, arm_R, leg_L, leg_R. Weights are rigid (one bone per vertex).
Clips (all humans get all four, so the game loads every person the same way):
  walk  (24 frames, loop): legs and arms swing in opposition, body bobs
  idle  (48 frames, loop): slow breathing, small head turn
  wave  (48 frames, loop): right arm up and waving, body stays still
  carry (24 frames, loop): both arms held forward, gentle walk
Models that are one piece (wheelchair users, kid on shoulders) have only root + body: their clips move the body.
"""
import math

CLIPS = {"walk": 24, "idle": 48, "wave": 48, "carry": 24}
SKELETON = {"root", "body", "head", "arm_L", "arm_R", "leg_L", "leg_R"}


def is_human(bone_names, name=""):
    """Full skeleton, or a one-piece person (wheelchair user, kid on shoulders) named SM_/RIG_ keepers or visitors."""
    return {"leg_L", "leg_R", "arm_L", "arm_R"} <= set(bone_names) or ("_keepers_" in name or "_visitors_" in name)


def clips(arm, h, key):
    """Create the actions on `arm` (model height h metres). `key` is rig._key."""
    pb = arm.pose.bones
    has = lambda n: n in pb
    ad = arm.animation_data_create()
    for clip, n in CLIPS.items():
        for b in pb:
            b.rotation_euler = (0, 0, 0); b.location = (0, 0, 0); b.scale = (1, 1, 1)
        ad.action = None
        for f in range(n + 1):
            ph = 2 * math.pi * f / n
            if clip in ("walk", "carry"):
                amp = 28 if clip == "walk" else 14
                if has("leg_R"):
                    key(pb["leg_R"], f, rot=(amp * math.sin(ph), 0, 0))
                if has("leg_L"):
                    key(pb["leg_L"], f, rot=(-amp * math.sin(ph), 0, 0))
                if clip == "walk":
                    if has("arm_R"):
                        key(pb["arm_R"], f, rot=(-24 * math.sin(ph), 0, 0))
                    if has("arm_L"):
                        key(pb["arm_L"], f, rot=(24 * math.sin(ph), 0, 0))
                else:  # arms forward (-Y), hands steady
                    for a in ("arm_R", "arm_L"):
                        if has(a):
                            key(pb[a], f, rot=(-60 + 3 * math.sin(2 * ph), 0, 0))
                if has("body"):
                    key(pb["body"], f, loc=(0, 0, 0.012 * h * abs(math.sin(ph))), rot=(0, 2 * math.sin(ph), 0))
                if has("head"):
                    key(pb["head"], f, rot=(-2 * math.sin(2 * ph), 0, 0))
            elif clip == "idle":
                if has("body"):
                    s = 1 + 0.012 * math.sin(ph)
                    key(pb["body"], f, scale=(s, 1, s))
                if has("head"):
                    key(pb["head"], f, rot=(2 * math.sin(ph), 0, 12 * math.sin(ph)))
                for a, sg in (("arm_R", 1), ("arm_L", -1)):
                    if has(a):
                        key(pb[a], f, rot=(0, 0, sg * 1.5 * math.sin(ph)))
            elif clip == "wave":
                if has("arm_R"):
                    up = min(1.0, f / 8, (n - f) / 8)  # lift in 8 frames, wave, lower
                    key(pb["arm_R"], f, rot=(0, -(150 + 12 * math.sin(ph * 4)) * up, 0))
                if has("head"):
                    key(pb["head"], f, rot=(0, 0, 6 * math.sin(ph)))
                if has("body"):
                    key(pb["body"], f, rot=(0, 0, 0))
        act = ad.action
        if act is None:
            continue
        act.name = clip
        act.use_fake_user = True
        track = ad.nla_tracks.new()
        track.name = clip
        track.strips.new(clip, 0, act)
        track.mute = True
        ad.action = None
    for b in pb:
        b.rotation_euler = (0, 0, 0); b.location = (0, 0, 0); b.scale = (1, 1, 1)
