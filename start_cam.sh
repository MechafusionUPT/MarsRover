
FF_OUT="$HOME/MarsRover/static/hls"
mkdir -p "$FF_OUT"

ffmpeg -f v4l2 -input_format mjpeg -framerate 30 -video_size 1280x720 -i /dev/video0 \
       -vf format=yuv420p -c:v libx264 -preset ultrafast -tune zerolatency \
       -g 60 -keyint_min 60 -f hls -hls_time 2 -hls_list_size 10 \
       -hls_flags delete_segments+append_list "$FF_OUT/stream.m3u8"
