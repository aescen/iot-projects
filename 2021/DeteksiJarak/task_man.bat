python3 src\deteksiJarak_local.py -v samples\new\1.5m_dekat.mp4 -s y -f 0
sleep 5
python3 src\deteksiJarak_local.py -v samples\new\1m_dekat.mp4 -s y -f 0
sleep 5
python3 src\deteksiJarak_local.py -v samples\new\50cm_dekat.mp4 -s y -f 0
sleep 5

python3 src\deteksiJarak_local.py -v samples\new\1.5m_sedang.mp4 -s y -f 0
sleep 5
python3 src\deteksiJarak_local.py -v samples\new\1m_sedang.mp4 -s y -f 0
sleep 5
python3 src\deteksiJarak_local.py -v samples\new\50cm_sedang.mp4 -s y -f 0
sleep 5

python3 src\deteksiJarak_local.py -v samples\new\1.5m_jauh.mp4 -s y -f 0
sleep 5
python3 src\deteksiJarak_local.py -v samples\new\1m_jauh.mp4 -s y -f 0
sleep 5
python3 src\deteksiJarak_local.py -v samples\new\50cm_jauh.mp4 -s y -f 0
sleep 5

python3 src\deteksiJarak_local.py -v samples\new\diagonal_1.mp4 -s y -f 0
sleep 5
python3 src\deteksiJarak_local.py -v samples\new\diagonal_2.mp4 -s y -f 0

echo 'done'
