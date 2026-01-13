---
title: print_position
author: Isaac Planas-Sitjà
description: Print current position of the target individual.
known_issues: None.
---

```python
# CASSETTE BEGINS: PRINT_POSITION
# AUTHOR: Isaac Planas-Sitjà
# DESCRIPTION: Print current position of the target individual.
# KNOWN ISSUE: None.

@client
def get_position(data, clock):
    coords = data[0, :, -1]
    if not np.isnan(coords).any():
        x, y = coords
        print(f"Position: x = {x:.1f}, y = {y:.1f}")

# CASSETTE ENDS: PRINT_POSITION
```
