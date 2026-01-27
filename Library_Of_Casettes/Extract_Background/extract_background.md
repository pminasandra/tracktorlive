---
title: extract_background
author: Pranav Minasandra (TracktorLive Cassette Maker GPT)
description: computes per-pixel variability to estimate a background image.
known_issues: none
---

```python
# CASSETTE BEGINS: EXTRACT_BACKGROUND
# DESCRIPTION: computes per-pixel variability to estimate a background image.
# AUTHOR: Pranav Minasandra (TracktorLive Cassette Maker GPT)
# USER DEFINED VARIABLES:
bgstat_SAMPLE_EVERY_N_FRAMES = 100          # take 1 sample every N frames
bgstat_MAX_SAMPLES = 600                   # cap stored samples to limit RAM
bgstat_USE_GRAYSCALE = False                # True: compute stats on grayscale
bgstat_STABILITY_VAR_THRESH = 4.0          # variance threshold (uint8 gray scale ~0-255)
bgstat_BG_OUTFILE = "background_est.png"   # output background estimate
bgstat_VAR_OUTFILE = "background_var.png"  # output variance heatmap (8-bit scaled)
# KNOWN ISSUES: If lighting changes strongly over time, "stable pixel" background may be imperfect.

@server.startfunc
def bgstat_setup(server):
    server.bgstat__samples = []
    server.bgstat__shape = None
    server.bgstat__count = 0

@server
def bgstat_collect(server):
    # sample the frame about to be tracked (fast + consistent timing)
    fr = server.current_frame
    if fr is None:
        return

    server.bgstat__count += 1
    if (server.bgstat__count % int(bgstat_SAMPLE_EVERY_N_FRAMES)) != 0:
        return

    if bgstat_USE_GRAYSCALE:
        samp = cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY)
    else:
        samp = fr.copy()

    # lock sample shape (avoid odd resizing mismatches)
    if server.bgstat__shape is None:
        server.bgstat__shape = samp.shape
    else:
        if samp.shape != server.bgstat__shape:
            samp = cv2.resize(samp, (server.bgstat__shape[1], server.bgstat__shape[0]))

    # store as compact uint8
    if samp.dtype != np.uint8:
        samp = np.clip(samp, 0, 255).astype(np.uint8)

    server.bgstat__samples.append(samp)

    # cap memory (keep most recent samples)
    if len(server.bgstat__samples) > int(bgstat_MAX_SAMPLES):
        server.bgstat__samples = server.bgstat__samples[-int(bgstat_MAX_SAMPLES):]

@server.stopfunc
def bgstat_finalize(server):
    samples = getattr(server, "bgstat__samples", [])
    if len(samples) < 2:
        return

    stack = np.stack(samples, axis=0).astype(np.float32)  # (T, H, W) or (T, H, W, C)
    var = np.var(stack, axis=0)
    med = np.median(stack, axis=0)

    # stable pixels mask (per-channel if color; then require all channels stable)
    if var.ndim == 3:  # grayscale (H, W)
        stable = var <= float(bgstat_STABILITY_VAR_THRESH)
        bg = med
        bg_out = np.clip(bg, 0, 255).astype(np.uint8)
        # variance visualization
        v = var
    else:  # color (H, W, C)
        stable = np.all(var <= float(bgstat_STABILITY_VAR_THRESH), axis=2)
        bg = med
        bg_out = np.clip(bg, 0, 255).astype(np.uint8)
        v = np.mean(var, axis=2)

    # fill unstable pixels with global median (robust fallback)
    if stable.ndim == 2 and bg_out.ndim == 2:
        fallback = np.median(bg_out[stable]) if np.any(stable) else np.median(bg_out)
        bg_out[~stable] = np.uint8(np.clip(fallback, 0, 255))
    elif stable.ndim == 2 and bg_out.ndim == 3:
        for c in range(3):
            ch = bg_out[:, :, c]
            fallback = np.median(ch[stable]) if np.any(stable) else np.median(ch)
            ch[~stable] = np.uint8(np.clip(fallback, 0, 255))
            bg_out[:, :, c] = ch

    # save background estimate
    cv2.imwrite(bgstat_BG_OUTFILE, bg_out)

    # save variance heatmap (8-bit scaled)
    vmax = float(np.percentile(v, 99.0)) if v.size else 1.0
    vmax = vmax if vmax > 1e-8 else 1.0
    var8 = np.clip((v / vmax) * 255.0, 0, 255).astype(np.uint8)
    cv2.imwrite(bgstat_VAR_OUTFILE, var8)

# CASSETTE ENDS: EXTRACT_BACKGROUND
```
