package id.ac.polinema.pstt.voicechat;

import android.media.AudioFormat;
import android.media.AudioManager;
import android.media.AudioRecord;
import android.media.AudioTrack;
import android.media.MediaRecorder;
import android.media.audiofx.AcousticEchoCanceler;
import android.media.audiofx.AutomaticGainControl;
import android.media.audiofx.NoiseSuppressor;
import android.util.Log;

import java.io.IOException;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.net.SocketException;
import java.net.UnknownHostException;

@SuppressWarnings("deprecation")
public class AudioCall {

    private static final String LOG_TAG = "AudioCall";
    private static final int DEFAULT_SAMPLE_RATE = 16000; // Hertz
    //private static final int SAMPLE_SIZE_IN_BYTES = 2;
    private static final int SAMPLE_INTERVAL = 10; // Milliseconds
    //private static final int DEFAULT_SAMPLES_PER_BUFFER = (DEFAULT_SAMPLE_RATE / 1000) * SAMPLE_INTERVAL; // 10ms
    private static final int DEFAULT_BUFFER_SIZE = AudioRecord.getMinBufferSize(DEFAULT_SAMPLE_RATE, AudioFormat.CHANNEL_IN_MONO, AudioFormat.ENCODING_PCM_16BIT);
    //private static final int DEFAULT_BUFFER_SIZE = SAMPLE_SIZE_IN_BYTES * DEFAULT_SAMPLES_PER_BUFFER;
    private InetAddress address; // Address to call
    private int port = 50000; // Port the packets are addressed to
    private boolean mic = false; // Enable mic?
    private boolean speakers = false; // Enable speakers?

    public AudioCall(InetAddress address) {

        this.address = address;
    }

    public void startCall() {

        startMic();
        startSpeakers();
    }

    public void endCall() {

        //Log.i(LOG_TAG, "Ending call!");
        muteMic();
        muteSpeakers();
    }

    public void muteMic() {

        mic = false;
    }

    public void muteSpeakers() {

        speakers = false;
    }

    private void checkThingsForRecorder(int audioSessionId) {

        if(NoiseSuppressor.isAvailable())
        {
              NoiseSuppressor.create(audioSessionId);
        }
        if(AutomaticGainControl.isAvailable())
        {
             AutomaticGainControl.create(audioSessionId);
        }
        if(AcousticEchoCanceler.isAvailable()){
             AcousticEchoCanceler.create(audioSessionId);
        }
    }

    public void startMic() {
        // Creates the thread for capturing and transmitting audio
        mic = true;
        Thread thread = new Thread(new Runnable() {

            @Override
            public void run() {
                // Create an instance of the AudioRecord class
                //Log.i(LOG_TAG, "Send thread started. Thread id: " + Thread.currentThread().getId());
                AudioRecord audioRecorder = new AudioRecord (MediaRecorder.AudioSource.VOICE_COMMUNICATION, DEFAULT_SAMPLE_RATE,
                        AudioFormat.CHANNEL_IN_MONO, AudioFormat.ENCODING_PCM_16BIT, DEFAULT_BUFFER_SIZE*2);
                checkThingsForRecorder(audioRecorder.getAudioSessionId());
                int bytes_read = 0;
                int bytes_sent = 0;
                byte[] buf = new byte[DEFAULT_BUFFER_SIZE];
                try {
                    // Create a socket and start recording
                    //Log.i(LOG_TAG, "Packet destination: " + address.toString());
                    DatagramSocket socket = new DatagramSocket();
                    audioRecorder.startRecording();
                    while(mic) {
                        // Capture audio from the mic and transmit it
                        bytes_read = audioRecorder.read(buf, 0, DEFAULT_BUFFER_SIZE);
                        DatagramPacket packet = new DatagramPacket(buf, bytes_read, address, port);
                        socket.send(packet);
                        bytes_sent += bytes_read;
                        //Log.i(LOG_TAG, "Total bytes sent: " + bytes_sent);
                        Thread.sleep(SAMPLE_INTERVAL, 0);
                    }
                    // Stop recording and release resources
                    audioRecorder.stop();
                    audioRecorder.release();
                    socket.disconnect();
                    socket.close();
                    mic = false;
                    return;
                }
                catch(InterruptedException e) {

                    //Log.e(LOG_TAG, "InterruptedException: " + e.toString());
                    mic = false;
                }
                catch(SocketException e) {

                    //Log.e(LOG_TAG, "SocketException: " + e.toString());
                    mic = false;
                }
                catch(UnknownHostException e) {

                    //Log.e(LOG_TAG, "UnknownHostException: " + e.toString());
                    mic = false;
                }
                catch(IOException e) {

                    //Log.e(LOG_TAG, "IOException: " + e.toString());
                    mic = false;
                }
            }
        });
        thread.start();
    }

    public void startSpeakers() {
        // Creates the thread for receiving and playing back audio
        if(!speakers) {

            speakers = true;
            Thread receiveThread = new Thread(new Runnable() {

                @Override
                public void run() {
                    // Create an instance of AudioTrack, used for playing back audio
                    //Log.i(LOG_TAG, "Receive thread started. Thread id: " + Thread.currentThread().getId());
                    //AudioTrack t = new AudioTrack(AudioAttributes.USAGE_VOICE_COMMUNICATION, AudioFormat.CHANNEL_IN_MONO , DEFAULT_BUFFER_SIZE, AudioTrack.MODE_STREAM, AudioManager.AUDIO_SESSION_ID_GENERATE);
                    AudioTrack track = new AudioTrack(AudioManager.STREAM_MUSIC, DEFAULT_SAMPLE_RATE, AudioFormat.CHANNEL_OUT_MONO,
                            AudioFormat.ENCODING_PCM_16BIT, DEFAULT_BUFFER_SIZE, AudioTrack.MODE_STREAM);
                    track.play();
                    try {
                        // Define a socket to receive the audio
                        DatagramSocket socket = new DatagramSocket(port);
                        byte[] buf = new byte[DEFAULT_BUFFER_SIZE];
                        while(speakers) {
                            // Play back the audio received from packets
                            DatagramPacket packet = new DatagramPacket(buf, DEFAULT_BUFFER_SIZE);
                            socket.receive(packet);
                            //Log.i(LOG_TAG, "Packet received: " + packet.getLength());
                            track.write(packet.getData(), 0, DEFAULT_BUFFER_SIZE);
                        }
                        // Stop playing back and release resources
                        socket.disconnect();
                        socket.close();
                        track.stop();
                        track.flush();
                        track.release();
                        speakers = false;
                        return;
                    }
                    catch(SocketException e) {

                        //Log.e(LOG_TAG, "SocketException: " + e.toString());
                        speakers = false;
                    }
                    catch(IOException e) {

                        //Log.e(LOG_TAG, "IOException: " + e.toString());
                        speakers = false;
                    }
                }
            });
            receiveThread.start();
        }
    }
}
