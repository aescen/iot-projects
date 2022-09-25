package id.ac.polinema.pstt.voicechat;

import android.util.Log;

import java.io.IOException;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.net.SocketException;
import java.net.SocketTimeoutException;
import java.util.HashMap;

import static id.ac.polinema.pstt.voicechat.MainActivity.dH;

public class ContactManager {

    public static final int BROADCAST_PORT = 50001; // Socket on which packets are sent/received
    private static final String LOG_TAG = "ContactManager";
    private static final int BROADCAST_INTERVAL = 2000; // Milliseconds
    private static final int BROADCAST_BUF_SIZE = 1024;
    private boolean BROADCAST = true;
    private boolean LISTEN = true;
    private String displayName;
    private InetAddress broadcastIP;

    public ContactManager(String name, InetAddress broadcastIP) {
        this.displayName= name;
        this.broadcastIP = broadcastIP;
        listen();
        broadcastName(name, broadcastIP);
    }

    public HashMap<String, InetAddress> getContacts() {
        return dH.getContacts();
    }

    public void addContact(String nname, InetAddress address) {
        //if the contact isn't already known to us, add it
        ////Log.i(LOG_TAG, "Contact:" + nname);
        ////Log.i(LOG_TAG, "Local Contact:" + this.displayName);
        if ( !dH.getContacts().containsKey(nname)) {
            if ( nname.contentEquals(this.displayName) ){
                ////Log.i(LOG_TAG, "Local contact: " + nname);
                return;
            }
            else if ( !nname.contentEquals(this.displayName) ){
                ////Log.i(LOG_TAG, "Adding contact: " + nname);
                dH.putContact(nname, address);
                ////Log.i(LOG_TAG, "#Contacts: " + dH.getContacts().size());
                return;
            }
        }

        ////Log.i(LOG_TAG, "Contact already exist: " + nname);
        return;
    }

    public void removeContact(String name) {
        // If the contact is known to us, remove it
        if(dH.getContacts().containsKey(name)) {

            ////Log.i(LOG_TAG, "Removing contact: " + name);
            dH.removeContact(name);
            ////Log.i(LOG_TAG, "#Contacts: " + dH.getContacts().size());
            return;
        }
        ////Log.i(LOG_TAG, "Cannot remove contact. " + name + " does not exist.");
        return;
    }

    public void bye(final String name) {
        // Sends a Bye notification to other devices
        Thread byeThread = new Thread(new Runnable() {

            @Override
            public void run() {

                try {
                    ////Log.i(LOG_TAG, "Attempting to broadcast BYE notification!");
                    String notification = "BYE:"+name;
                    byte[] message = notification.getBytes();
                    DatagramSocket socket = new DatagramSocket();
                    socket.setBroadcast(true);
                    DatagramPacket packet = new DatagramPacket(message, message.length, broadcastIP, BROADCAST_PORT);
                    socket.send(packet);
                    ////Log.i(LOG_TAG, "Broadcast BYE notification!");
                    socket.disconnect();
                    socket.close();
                    return;
                }
                catch(SocketException e) {

                    ////Log.e(LOG_TAG, "SocketException during BYE notification: " + e);
                }
                catch(IOException e) {

                    ////Log.e(LOG_TAG, "IOException during BYE notification: " + e);
                }
            }
        });
        byeThread.start();
    }

    public void broadcastName(final String name, final InetAddress broadcastIP) {
        // Broadcasts the name of the device at a regular interval
        ////Log.i(LOG_TAG, "Broadcasting started!");
        Thread broadcastThread = new Thread(new Runnable() {

            @Override
            public void run() {

                try {

                    String request = "ADD:"+name;
                    byte[] message = request.getBytes();
                    DatagramSocket socket = new DatagramSocket();
                    socket.setBroadcast(true);
                    DatagramPacket packet = new DatagramPacket(message, message.length, broadcastIP, BROADCAST_PORT);
                    while(BROADCAST) {

                        socket.send(packet);
                        ////Log.i(LOG_TAG, "Broadcast packet sent: " + packet.getAddress().toString());
                        Thread.sleep(BROADCAST_INTERVAL);
                    }
                    ////Log.i(LOG_TAG, "Broadcaster ending!");
                    socket.disconnect();
                    socket.close();
                }
                catch(SocketException e) {
                    ////Log.e(LOG_TAG, "SocketExceltion in broadcast: " + e);
                    ////Log.i(LOG_TAG, "Broadcaster ending!");
                }
                catch(IOException e) {
                    ////Log.e(LOG_TAG, "IOException in broadcast: " + e);
                    ////Log.i(LOG_TAG, "Broadcaster ending!");
                }
                catch(InterruptedException e) {
                    ////Log.e(LOG_TAG, "InterruptedException in broadcast: " + e);
                    ////Log.i(LOG_TAG, "Broadcaster ending!");
                }
            }
        });
        broadcastThread.start();
    }

    public void stopBroadcasting() {
        // Ends the broadcasting thread
        BROADCAST = false;
    }

    public void listen() {
        // Create the listener thread
        ////Log.i(LOG_TAG, "Listening started!");
        final Thread listenThread = new Thread(new Runnable() {

            @Override
            public void run() {
                DatagramSocket socket = null;
                try {
                    socket = new DatagramSocket(BROADCAST_PORT);
                    byte[] buffer = new byte[BROADCAST_BUF_SIZE];
                    DatagramPacket packet = new DatagramPacket(buffer, BROADCAST_BUF_SIZE);
                    socket.setSoTimeout(10000);
                    ////Log.i(LOG_TAG, "Contact listener started!");
                    while(LISTEN) {
                        try {
                            //Listen in for new notifications
                            ////Log.i(LOG_TAG, "Listening for a packet!");
                            socket.receive(packet);
                            String data = new String(buffer, 0, packet.getLength());
                            ////Log.i(LOG_TAG, "Packet received: " + data);
                            String action = data.substring(0, 4);
                            if(action.equals("ADD:")) {
                                // Add notification received. Attempt to add contact
                                ////Log.i(LOG_TAG, "Listener received ADD request");
                                addContact(data.substring(4, data.length()), packet.getAddress());
                            }
                            else if(action.equals("BYE:")) {
                                // Bye notification received. Attempt to remove contact
                                ////Log.i(LOG_TAG, "Listener received BYE request");
                                removeContact(data.substring(4, data.length()));
                            }
                            else {
                                // Invalid notification received
                                ////Log.w(LOG_TAG, "Listener received invalid request: " + action);
                            }
                        }catch (SocketTimeoutException e) {
                            ////Log.i(LOG_TAG, "No packet received yet.");
                        }catch (IOException e) {
                            ////Log.e(LOG_TAG, "IOExcepion in listener: " + e);
                        }
                    }
                    ////Log.i(LOG_TAG, "Listener ending!");
                    socket.disconnect();
                    socket.close();
                }
                catch (SocketException e) {
                    ////Log.e(LOG_TAG, "SocketExcepion in listener: " + e);
                    if(socket != null){
                        socket.disconnect();
                        socket.close();
                    }
                    listen();
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
