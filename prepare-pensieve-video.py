#!/usr/bin/env python3

from os import path
from utils.utils import run_shell_cmd

###### config #########
PRINT_COMMANDS = True  # set it to False if you want to execute the script (may take some time)
VIDEO_NAME = 'BMPCC4K_v4min'
INPUT_VIDEO_PATH = path.join('input_videos', f'{VIDEO_NAME}.mp4')
OUTPUT_FOLDER = path.join('output_videos')
segment_size = 4  # in secs
target_fps = 30
dash_configs = [
    # [width, height, bitrate, id]
    [3840, 2160, 17408000, '4k'],
    [2560, 1440, 6144000, '2k'],
    [1920, 1080, 4300000, '1920p'],
    [1280, 720, 2850000, '1280p'],
    [1024, 576, 1850000, '1024p'],
    [768, 432, 1200000, '768p'],
    [640, 360, 750000, '640p'],
    [320, 180, 300000, '320p']
]

video_quality_renditions = [f"{OUTPUT_FOLDER}/{VIDEO_NAME}_intermed_{config[2]}.mp4#video:id={config[3]}"
                            for config in dash_configs]

mp4box_bin = "MP4Box "
ffmpeg_bin = "ffmpeg "
overwrite_output_files = "-y "

## get intermediate representations
for config in dash_configs:
    width = config[0]
    height = config[1]
    target_bitrate = config[2]

    input_file = f"-i {INPUT_VIDEO_PATH} "
    fps = f"-r {target_fps} "
    h264_encoding_options = f"-x264opts 'keyint={target_fps * segment_size}:" \
                            f"min-keyint={target_fps * segment_size}:no-scenecut' "
    resolution = f"-vf scale={width}:{height} "
    bitrate = f"-b:v {target_bitrate} "
    buffer_maxrate = f"-maxrate {target_bitrate * 2} -bufsize {target_bitrate * 2} "
    enable_faststart = f"-movflags faststart "
    h264_profile = f"-profile:v main "
    encoder_preset = f"-preset fast "
    skip_audio = f"-an "
    inter_output_file = f"{OUTPUT_FOLDER}/{VIDEO_NAME}_intermed_{target_bitrate}.mp4"

    command = ffmpeg_bin + overwrite_output_files + input_file + fps + h264_encoding_options + \
              resolution + bitrate + buffer_maxrate + enable_faststart + h264_profile + \
              encoder_preset + skip_audio + inter_output_file
    if PRINT_COMMANDS:
        print(command)
    else:
        run_shell_cmd(command)

## dash packaging
segment = f"-dash {segment_size * 1000} "
fragment = f"-frag {segment_size * 1000} "
random_access_points = "-rap "
segment_name = f"-segment-name 'segment_$RepresentationID$_' "
dash_fps = f"-fps {target_fps} "
video_renditions = f"{' '.join(video_quality_renditions)} "
output_mpd_file = f"-out {OUTPUT_FOLDER}/package/{VIDEO_NAME}_playlist.mpd"

dash_command = mp4box_bin + segment + fragment + random_access_points + \
               segment_name + dash_fps + video_renditions + output_mpd_file
if PRINT_COMMANDS:
    print(dash_command)
else:
    run_shell_cmd(dash_command)

print('Complete./')
