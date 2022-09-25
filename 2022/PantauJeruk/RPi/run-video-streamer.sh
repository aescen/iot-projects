#!/bin/bash

# need to run with sudo
# to run in background ./run-video-streamer.sh > /dev/null 2>&1 &

# for hls streaming:  https://stackoverflow.com/questions/39431714/ffmpeg-transcode-to-live-stream
#use video.js: https://github.com/videojs/video.js use http-streaming: https://github.com/videojs/http-streaming
# stream1 for HQ, stream2 for LQ
/usr/local/bin/ffmpeg -i "rtsp://admintapo:admintapo@192.168.0.100/stream2" -s 640x360 -crf 30 -r 60 -async 1 -acodec aac -ar 48000 -ac 2 -b:a 128k -vcodec libx264 -b:v 1024k -tune zerolatency -preset ultrafast -f ssegment -hls_flags delete_segments -segment_list /var/www/html/video/live/index.m3u8 -segment_list_type hls -segment_list_size 8 -segment_list_flags +live -segment_time 8 -segment_wrap 8 -hls_flags delete_segments /var/www/html/video/live/out_%6d.ts
# clean
rm -rf /var/www/html/video/out
mkdir /var/www/html/video/out/

# for flv streaming: https://stackoverflow.com/questions/66658044/stream-rtsp-to-html5-video-tag
# use flv.js: https://github.com/Bilibili/flv.js/
#/usr/local/bin/ffmpeg -i "rtsp://admintapo:admintapo@192.168.0.100/stream2" copy -an -f flv -s 640x360 -crf 30 -tune zerolatency -preset ultrafast -acodec aac -ar 44100 -ac 2 -b:a 96k -vcodec libx264 -r 25 -b:v 500k rtmp://localhost:1935/live/cam0

# ffmpeg streaming guide: https://trac.ffmpeg.org/wiki/StreamingGuide
