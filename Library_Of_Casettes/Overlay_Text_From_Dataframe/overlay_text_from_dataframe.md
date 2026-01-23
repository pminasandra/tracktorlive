---
title: overlay_text_from_df
author: Pranav Minasandra (TracktorLive Cassette Maker GPT)
description: Overlays user-provided frame-wise text on video
known_issues: None.
---

```python
# CASSETTE BEGINS: OVERLAY_TEXT_FROM_DF
# DESCRIPTION: Overlays user-provided text on server.current_frame using a dataframe
#              with columns: frameindex, x, y, text.
# AUTHOR: TracktorLive Cassette Maker GPT
# USER DEFINED VARIABLES:
overlay_text_from_df_DF = df  # TODO: pandas.DataFrame with [frameindex, x, y, text]
overlay_text_from_df_FONT_SCALE = 0.7
overlay_text_from_df_COLOR_BGR = (0, 0, 0)  # (B, G, R)
overlay_text_from_df_THICKNESS = 1
overlay_text_from_df_FONT = cv2.FONT_HERSHEY_SIMPLEX
overlay_text_from_df_LINE_TYPE = cv2.LINE_AA
# KNOWN ISSUES: None

@server.startfunc
def overlay_text_from_df__setup(server):
    df = overlay_text_from_df_DF
    if df is None:
        server.overlay_text_from_df__frame_map = {}
        return

    # Precompute a frameindex -> list[(x, y, text)] map for speed
    _map = {}
    for fr, sub in df.groupby("frameindex", sort=False):
        try:
            fr_i = int(fr)
        except Exception:
            continue
        items = []
        for row in sub.itertuples(index=False):
            try:
                x = int(getattr(row, "x"))
                y = int(getattr(row, "y"))
                txt = str(getattr(row, "text"))
            except Exception:
                continue
            items.append((x, y, txt))
        if items:
            _map[fr_i] = items

    server.overlay_text_from_df__frame_map = _map


@server
def overlay_text_from_df(server):
    frame = server.current_frame
    if frame is None:
        return

    fr_i = int(server.frame_index)
    items = getattr(server, "overlay_text_from_df__frame_map", {}).get(fr_i, None)
    if not items:
        return

    for (x, y, txt) in items:
        cv2.putText(
            frame,
            txt,
            (x, y),
            overlay_text_from_df_FONT,
            overlay_text_from_df_FONT_SCALE,
            overlay_text_from_df_COLOR_BGR,
            overlay_text_from_df_THICKNESS,
            overlay_text_from_df_LINE_TYPE,
        )

    server.current_frame = frame

# CASSETTE ENDS: OVERLAY_TEXT_FROM_DF
```
