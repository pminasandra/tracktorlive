# The Library of Cassettes

Here are all the cassettes available as of now.

| Title | Description |
|---|---|
| [Add Circular Mask](Add_Circular_Mask/add_circular_mask.md) | Masks everything except a circle of specified position and radius |
| [Add Custom Mask](Add_Custom_Mask/add_custom_mask.md) | Add a custom mask to every frame based on user-provided image file |
| [Add Rectangular Mask](Add_Rectangular_Mask/add_rectangular_mask.md) | Masks everything except a rectangle of specified vertices |
| [Background Subtract](Background_Subtract/background-subtract.md) | Replace background pixels with white using an averaged background image |
| [Boost Contrast](Boost_Contrast/boost_contrast.md) | Brightness and contrast control |
| [Channel Select](Channel_Select/channel_select.md) | Preserves only one of the BGR channels |
| [Display Feed](Display_Feed/show_live_feed.md) | Displays current tracking from the server in real-time. Press 'q' or <Esc> to close running display at any time |
| [Display Final Vel Plot](Display_Final_Plot/display_final_plot.md) | Displays and saves a plot of velocities when we reach the end of the video file we are analysing |
| [Display With Circ Hl](Display_With_Circ_Highlight/display_with_rect_highlight.md) | Displays current tracking from the server in real-time. Highlights a chosen circular region. Press 'q' or <Esc> to close running display at any time |
| [Display With Rect Hl](Display_With_Rect_Highlight/display_with_rect_highlight.md) | Displays current tracking from the server in real-time. Highlights a chosen rectangular region. Press 'q' or <Esc> to close running display at any time |
| [Dynamic Masking](Dynamic_Masking/dynamic_masking.md) | Only look for individuals in vicinity of previous locs |
| [Extract Specified Frames](Extract_Specified_Frames/extract_specified_frames.md) | Saves as jpg all frames at specified indices |
| [First Person Views](First_Person_Views/first_person_views.md) | For each tracked individual, crop a fixed-size square that is rotated so the animal’s heading points “up”. Uses EMA + rate limiting to smooth orientation. Writes one MP4 per individual |
| [Message Arduino](Message_Arduino/message_arduino.md) | When a user-defined function returns a character, transmits that character to a connected Arduino |
| [Preserve Frame](Preserve_Frame/preserve_frame.md) | Put non-edited frames in framesbuffer (useful for dumpvideo methods) |
| [Print Directions](Print_Directions/print_directions.md) | Calculates and prints the direction based on position changes |
| [Print Position](Print_Position/print_position.md) | Print current position of the target individual |
| [Record When Together](Record_When_Together/record_when_together.md) | When two animals are close together, record video only then |
| [Run Command On Condition](Run_Command_On_Condition/run_command_on_condition.md) | Runs a shell command when a function returns True, respecting a time based cooldown rule |
| [Timesync](Timesync/timesync.md) | Creates a parquet file of time.time() clock, useful for ms level sync |
| [Update Plot](Update_plot/update_plot.md) | Displays (and saves) a plot every few seconds. Useful to monitor data in real time |

## Contributing Cassettes
