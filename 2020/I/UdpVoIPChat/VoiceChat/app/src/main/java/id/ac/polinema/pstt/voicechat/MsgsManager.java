package id.ac.polinema.pstt.voicechat;

import android.util.Log;

import org.json.JSONException;
import org.json.JSONObject;

import java.io.IOException;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.net.SocketException;
import java.net.SocketTimeoutException;
import java.net.UnknownHostException;
import java.util.HashMap;
import java.util.Random;

import static id.ac.polinema.pstt.voicechat.MainActivity.dH;
import static java.lang.Thread.sleep;

public class MsgsManager {
    private static final String LOG_TAG = "MsgsManager";
    private static final int MSG_BROADCAST_PORT = 50005;
    private static final int BUF_SIZE = 1024;
    private boolean LISTEN = true;
    private String displayName;
    private String localIP;

    public MsgsManager(String displayName, String localIP) {
        this.displayName = displayName;
        this.localIP = localIP;
        startRcvListener();
    }

    private void sendAck(final String hash, final String ip){
        new Thread(new Runnable() {
            @Override
            public void run() {
                String message = "ACK:"+ hash;
                while(true){
                    try {
                        InetAddress address = InetAddress.getByName(ip);
                        byte[] dataAck = message.getBytes();
                        DatagramSocket socketAck = new DatagramSocket();
                        socketAck.setSoTimeout(2000);
                        DatagramPacket packetAck = new DatagramPacket(dataAck, dataAck.length, address, MSG_BROADCAST_PORT);
                        socketAck.send(packetAck);
                        //Log.i(LOG_TAG, "Sent message( " + message + " ) to " + ip);
                        socketAck.disconnect();
                        socketAck.close();
                    }
                    catch(UnknownHostException e) {

                        //Log.e(LOG_TAG, "Failure. UnknownHostException in sendMessage: " + ip);
                    }
                    catch(SocketException e) {

                        //Log.e(LOG_TAG, "Failure. SocketException in sendMessage: " + e);
                    }
                    catch(IOException e) {

                        //Log.e(LOG_TAG, "Failure. IOException in sendMessage: " + e);
                    }
                }
            }
        }).start();
    }

    private void updateMsgStatus(int status, Integer hash){

    }

    private void startRcvListener() {
        // Create msg listener thread
        Thread listenThread = new Thread(new Runnable() {
            @Override
            public void run() {
                DatagramSocket socket = null;
                try {
                    socket = new DatagramSocket(MSG_BROADCAST_PORT, InetAddress.getByName(localIP));
                    byte[] buffer = new byte[BUF_SIZE];
                    socket.setSoTimeout(10000);
                    DatagramPacket packet = new DatagramPacket(buffer, BUF_SIZE);
                    //Log.i(LOG_TAG, "Msg listener started!");
                    while(LISTEN) {
                        try {
                            //Log.i(LOG_TAG, "Listening for packets");
                            socket.receive(packet);
                            String datas = new String(buffer, 0, packet.getLength());
                            //Log.i(LOG_TAG, "Packet received from " + packet.getAddress() + " with contents: " + datas);
                            String action = datas.substring(0, 4);
                            if (action.equals("ACK:")) {
                                // Add notification received. Attempt to add contact
                                //Log.i(LOG_TAG, "Listener received ACK request");
                                //update status to received
                                int status = 1;
                                updateMsgStatus(status, Integer.parseInt(datas.substring(4, datas.length())));
                            } else if (action.equals("MRD:")) {
                                // Bye notification received. Attempt to remove contact
                                //Log.i(LOG_TAG, "Listener received BYE request");
                                //update status to seen
                                int status = 2;
                                updateMsgStatus(status, Integer.parseInt(datas.substring(4, datas.length())));
                            } else if (action.equals("REQ:")) {
                                // Bye notification received. Attempt to remove contact
                                //Log.i(LOG_TAG, "Listener received REQ request");
                                String nname = datas.substring(4, datas.length());
                                InetAddress address = packet.getAddress();
                                if ( !dH.getContacts().containsKey(nname)) {
                                    if ( nname.contentEquals(dH.getDisplayName()) ){
                                        ////Log.i(LOG_TAG, "Local contact: " + nname);
                                        return;
                                    }
                                    else if ( !nname.contentEquals(dH.getDisplayName()) ){
                                        ////Log.i(LOG_TAG, "Adding contact: " + nname);
                                        dH.putContact(nname, address);
                                        ////Log.i(LOG_TAG, "#Contacts: " + dH.getContacts().size());
                                        return;
                                    }
                                }
                                String replyAck = "ACK:"+ dH.getDisplayName();
                                DatagramPacket dp = new DatagramPacket(replyAck.getBytes(), replyAck.length(), packet.getAddress(), packet.getPort());
                                socket.send(dp);
                                //Log.i("Replying REQ:",replyAck);
                            } else {
                                // Invalid notification received
                                //Log.w(LOG_TAG, "Listener received non action request: " + action + "continuing as JSONobj.");
                                try {
                                    JSONObject payloadRcv = new JSONObject(datas);
                                    String hash = payloadRcv.getString("hash");
                                    String id = payloadRcv.getString("id");
                                    String message = payloadRcv.getString("message");
                                    String src = payloadRcv.getString("src");
                                    String srcIp = payloadRcv.getString("srcIp");
                                    String dst = payloadRcv.getString("dst");
                                    String dstIp = payloadRcv.getString("dstIp");
                                    String time = payloadRcv.getString("time");
                                    String status = payloadRcv.getString("status");
                                    payloadRcv = new JSONObject();
                                    payloadRcv.put("id", id);
                                    payloadRcv.put("message", message);
                                    payloadRcv.put("src", src);
                                    payloadRcv.put("srcIp", srcIp);
                                    payloadRcv.put("dst", dst);
                                    payloadRcv.put("dstIp", dstIp);
                                    payloadRcv.put("time", time);
                                    payloadRcv.put("status", status);//-1 = not sent, 0 = received, 1 = unread
                                    //status -1 = not sent, 0 = sent but no ack, 1 = received, 2 = unseen
                                    //hash doesn't exist
                                    if (!dH.getMessages().containsKey(hash) &&
                                            //not from self & srcIp is correct
                                            (!src.contentEquals(displayName) && !srcIp.contentEquals(localIP) && srcIp.contentEquals(packet.getAddress().getHostAddress())) &&
                                            //dst is this ip
                                            (dst.contentEquals(displayName) && dstIp.contentEquals(localIP))) {
                                        //Save new message
                                        //Log.i(LOG_TAG, "Receive msg: " + "hash:" + hash + "-payload:"+ payloadRcv.toString());
                                        dH.putMessage(hash, payloadRcv.toString());
                                        //Send ack
                                        String replyAck = "ACK";
                                        DatagramPacket dp = new DatagramPacket(replyAck.getBytes(), replyAck.length(), packet.getAddress(), packet.getPort());
                                        socket.send(dp);
                                        //sendAck("ACK:" + hash, srcIp);
                                    }
                                    //hash exist, not from self and dst is correct
//                                    else if (dH.getMessages().containsKey(hash) &&
//                                            //not from self
//                                            !(src.contentEquals(displayName) && srcIp.contentEquals(localIP)) &&
//                                            //dst is this ip
//                                            (dst.contentEquals(displayName) && dstIp.contentEquals(localIP))) {
//                                        //Resend ack
//                                        sendAck("ACK:" + hash, srcIp);
//                                        //Log.i(LOG_TAG, "Resend ACK: " + "hash:" + hash + "-to:"+ srcIp);
//                                    }
                                } catch (JSONException e) {
                                    //Log.e(LOG_TAG, "JSONExcepion in listener: " + e);
                                }
                            }
                        } catch (SocketTimeoutException e) {
                            //Log.i(LOG_TAG, "No packet received yet.");
                        } catch (IOException e) {
                            //Log.e(LOG_TAG, "IOException in listen: " + e);
                        }
                    }
                    //Log.i(LOG_TAG, "Msg listener ending!");
                    socket.disconnect();
                    socket.close();
                }
                catch (SocketException e) {
                    //Log.e(LOG_TAG, "SocketExcepion in msg listener: " + e);
                    if(socket != null){
                        socket.disconnect();
                        socket.close();
                    }
                    startRcvListener();
                } catch (UnknownHostException e) {
                    //Log.e(LOG_TAG, "UnknownHostException in msg listener: " + e);
                }
            }
        });
        listenThread.start();
    }
    public void stopListening() {
        // Stops the listener thread
        LISTEN = false;
    }
}
