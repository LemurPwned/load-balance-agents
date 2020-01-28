for i in {0..15..1}; do neato < output$i.dot -Tpng -o graph$i.png ; done
ffmpeg -framerate 2 -pattern_type glob  -i '*.data.png'  -c:v libx264 -r 30 -pix_fmt yuv420p out.mp4