package id.ac.polinema.pstt.voicechat;

import android.annotation.SuppressLint;
import android.app.AlertDialog;
import android.content.DialogInterface;
import android.content.Intent;
import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;
import android.text.Editable;
import android.text.TextWatcher;
import android.util.Log;
import android.view.View;
import android.view.View.OnClickListener;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ImageButton;
import android.widget.ListView;
import android.widget.ProgressBar;
import android.widget.TextView;

import org.json.JSONException;
import org.json.JSONObject;

import java.io.IOException;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.net.InetSocketAddress;
import java.net.Socket;
import java.net.SocketAddress;
import java.net.SocketException;
import java.net.SocketTimeoutException;
import java.net.UnknownHostException;
import java.security.NoSuchAlgorithmException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;
import java.util.Random;
import java.util.TreeMap;

import static id.ac.polinema.pstt.voicechat.MainActivity.algorithm;
import static id.ac.polinema.pstt.voicechat.MainActivity.dH;
import static id.ac.polinema.pstt.voicechat.Utils.getChecksum;
import static java.lang.Math.abs;
import static java.lang.Thread.sleep;

public class SendMsgActivity extends AppCompatActivity {
    private static final String LOG_TAG = "SendMsgs";
    private static final int MSG_BROADCAST_PORT = 50005;
    private static final int BUF_SIZE = 1024;
    private static final String EXTRA_ORIGIN = "ORIGIN";
    private static final String EXTRA_LOCALIP = "LOCALIP";
    private static final String EXTRA_DISPLAYNAME = "DISPLAYNAME";
    private static final String EXTRA_CONTACT = "CONTACT";
    private static final String EXTRA_IP = "IP";
    private static final int SECOND_ACTIVITY_REQUEST_CODE = 0;
    private static final int THIRD_ACTIVITY_REQUEST_CODE = 1;
    private static String localIp = dH.getLocalIp().getHostAddress();
    private static String contactName;
    private static String contactIp;
    private ParseMessages m;
    private Map<Long, Message> mLists = new TreeMap<Long, Message>();
    private ArrayList<String> mViews = new ArrayList<String>();
    private String displayName;
    private MsgsAdapter messageAdapter;
    private ListView messagesView;
    private String origin;
    private AppCompatActivity sendMsgsActivity = this;
    private static boolean isAlive = false;

    @SuppressLint("SetTextI18n")
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_send_msg);

        messageAdapter = new MsgsAdapter(this, false);
        messagesView = (ListView) findViewById(R.id.messages);
        messagesView.setAdapter(messageAdapter);
        runOnUiThread(new Runnable() {
            @Override
            public void run() {
                messageAdapter.clear();
            }
        });

        //Log.i(LOG_TAG, "SendMsgActivity started!");
//        //Log.d("dH send ip:",dH.getLocalIp().getHostAddress());
//        //Log.d("dH send bc:",dH.getBcIp().getHostAddress());

        final EditText editText = (EditText) findViewById(R.id.editTextDestination);
        final TextView msgEdText = (TextView) findViewById(R.id.editTextMsg);
        final Button btOk = (Button) findViewById(R.id.bt_ok);
        final ImageButton sendMsg= (ImageButton) findViewById(R.id.imageButtonSend);
        btOk.setEnabled(false);
        btOk.setClickable(false);
        sendMsg.setEnabled(false);
        sendMsg.setClickable(false);

        Intent intent = getIntent();
        origin = intent.getStringExtra(EXTRA_ORIGIN);
        displayName = dH.getDisplayName();
        if (!origin.contentEquals("FAB")){
            contactName = intent.getStringExtra(EXTRA_CONTACT);
            contactIp = intent.getStringExtra(EXTRA_IP);
            editText.setText(contactName + "@" + contactIp);
            editText.setEnabled(false);
            editText.setClickable(false);
        } else {
            editText.setText("");
            editText.setEnabled(true);
            editText.setClickable(true);
            msgEdText.setEnabled(false);
            msgEdText.setClickable(false);
        }

        editText.addTextChangedListener(new TextWatcher() {
            @Override
            public void beforeTextChanged(CharSequence s, int start, int count, int after) {
                btOk.setEnabled(false);
                btOk.setClickable(false);

            }

            @Override
            public void onTextChanged(CharSequence s, int start, int before, int count) {
                if(s.length() != 0){
                    btOk.setEnabled(true);
                    btOk.setClickable(true);
                }
            }

            @Override
            public void afterTextChanged(Editable s) {
                if(s.length() != 0){
                    btOk.setEnabled(true);
                    btOk.setClickable(true);
                }
            }
        });

        btOk.setOnClickListener(new OnClickListener() {
            @Override
            public void onClick(View v) {
                String host = editText.getText().toString();
                if(host.length() > 0 && !host.contentEquals(localIp)){
                    boolean iO = isAlive(host);
                    if(iO){
                        editText.setText(contactName + "@" + contactIp);
                        editText.setEnabled(false);
                        editText.setClickable(false);
                        btOk.setEnabled(false);
                        btOk.setClickable(false);
                        msgEdText.setEnabled(true);
                        msgEdText.setClickable(true);
                        origin = "FABchecked";
                        //Log.i(LOG_TAG, "FAB checked...");
                        dH.setMessagesDataChange(true);
                        scanMessages();
                    } else {
                        // If no device was selected, present an error message to the user
                        //Log.w(LOG_TAG, "Warning: host unreachable! " + editText.getText().toString());
                        final AlertDialog alert = new AlertDialog.Builder(sendMsgsActivity).create();
                        alert.setTitle("Oops...");
                        alert.setMessage("Host " + editText.getText().toString() + " is unreachable/offline, check connection/ip address.");
                        alert.setButton(-1, "Ok", new DialogInterface.OnClickListener() {
                            public void onClick(DialogInterface dialog, int which) {
                                alert.dismiss();
                            }
                        });
                        alert.show();
                    }
                }
            }
        });

        msgEdText.addTextChangedListener(new TextWatcher() {
            @Override
            public void beforeTextChanged(CharSequence s, int start, int count, int after) {
                sendMsg.setEnabled(false);
                sendMsg.setClickable(false);
            }

            @Override
            public void onTextChanged(CharSequence s, int start, int before, int count) {
                if(s.length() != 0){
                    sendMsg.setBackgroundResource(R.drawable.ic_send_black_24dp);
                    sendMsg.setEnabled(true);
                    sendMsg.setClickable(true);
                }
                else if(s.length() == 0){
                    sendMsg.setBackgroundResource(R.drawable.ic_send_grey_24dp);
                    sendMsg.setEnabled(false);
                    sendMsg.setClickable(false);
                }
            }

            @Override
            public void afterTextChanged(Editable s) {
                if(s.length() != 0){
                    sendMsg.setEnabled(true);
                    sendMsg.setClickable(true);
                } else if(s.length() == 0){
                    sendMsg.setBackgroundResource(R.drawable.ic_send_grey_24dp);
                    sendMsg.setEnabled(false);
                    sendMsg.setClickable(false);
                }
            }
        });

        sendMsg.setOnClickListener(new OnClickListener() {
            @Override
            public void onClick(View view){
                if (!origin.contentEquals("FAB")){
                    if ( (msgEdText.getText().length() > 0) && contactIp.length() > 0 ){
                        String msgText = msgEdText.getText().toString();
                        sendMessage(msgText, contactIp, contactName);
                        msgEdText.setText("");
                    }
                } else if(msgEdText.getText() != null && contactIp != null){
                    if ( (msgEdText.getText().length() > 0) && contactIp.length() > 0 ){
                        String msgText = msgEdText.getText().toString();
                        sendMessage(msgText, contactIp, contactName);
                        msgEdText.setText("");
                    }
                }
            }
        });
        if(!origin.contentEquals("FAB")){
            dH.setMessagesDataChange(true);
            scanMessages();
        }else{
            //Log.i(LOG_TAG, "Waiting FAB checked...");
        }
    }

    public boolean isAlive(final String host) {
        isAlive = false;
        new Thread(new Runnable() {
            @Override
            public void run() {
                try{
                    InetAddress address = InetAddress.getByName(host);
                    String payload = "REQ:" + displayName;
                    byte[] data = payload.getBytes();
                    DatagramSocket socket = new DatagramSocket();
                    socket.setSoTimeout(2000);
                    DatagramPacket packet = new DatagramPacket(data, data.length, address, MSG_BROADCAST_PORT);
                    //Log.i(LOG_TAG, "Sending req: " + payload + " data length:" + data.length + " to:" + host);
                    socket.send(packet);
                    byte[] ack = new byte[BUF_SIZE];
                    DatagramPacket dp = new DatagramPacket(ack, ack.length);
                    socket.receive(dp);
                    String datas = new String(ack, 0, packet.getLength());
                    if (datas.equals("ACK:")) {
                        //Log.i(LOG_TAG, "Req succes: " + payload + "data length:" + data.length + " to:" + host);
                        String nname = datas.substring(4, datas.length());
                        InetAddress addr = packet.getAddress();
                        if ( !dH.getContacts().containsKey(nname)) {
                            if ( nname.contentEquals(dH.getDisplayName()) ){
                                ////Log.i(LOG_TAG, "Local contact: " + nname);
                                return;
                            }
                            else if ( !nname.contentEquals(dH.getDisplayName()) ){
                                ////Log.i(LOG_TAG, "Adding contact: " + nname);
                                dH.putContact(nname, addr);
                                contactName = nname;
                                contactIp = addr.getHostAddress();
                                ////Log.i(LOG_TAG, "#Contacts: " + dH.getContacts().size());
                                return;
                            }
                        }
                    }
                    socket.disconnect();
                    socket.close();
                    isAlive = true;
                } catch (UnknownHostException e) {
                    //Log.e("Req:","UnknownHostException");
                } catch (SocketException e) {
                    //Log.e("Req:","SocketException");
                } catch (SocketTimeoutException e) {
                    //Log.e("Req:","SocketTimeoutException");
                } catch (IOException e) {
                    //Log.e("Req:","IOException");
                }
            }
        }).start();
        Long utcNow = System.currentTimeMillis()/1000;
        final ProgressBar prgressBar = (ProgressBar) findViewById(R.id.progBar);
        boolean vis = false;
        do{
            if (!vis){
                runOnUiThread(new Runnable() {
                    @Override
                    public void run() {
                        prgressBar.setVisibility(View.VISIBLE);
                    }
                });
                vis = true;
            }
            else if(isAlive){
                runOnUiThread(new Runnable() {
                    @Override
                    public void run() {
                        prgressBar.setVisibility(View.GONE);
                    }
                });
                break;
            }
        }
        while ((System.currentTimeMillis()/1000) - utcNow <= 2000 );
        return isAlive;
    }

    @Override
    public void onBackPressed() {
        super.onBackPressed();
        // put the String to pass back into an Intent and close this activity
        Intent intent;
        if(origin.contentEquals("MAIN")) {
            intent = new Intent(this, MainActivity.class);
        } else {
            intent = new Intent(this, MsgsActivity.class);
        }
        setResult(RESULT_OK, intent);
        intent.setFlags(Intent.FLAG_ACTIVITY_LAUNCHED_FROM_HISTORY);
        finishActivity(THIRD_ACTIVITY_REQUEST_CODE);
        finish();
        //startActivity(intent);
    }

    private void scanMessages(){
        new Thread(new Runnable() {
            @Override
            public void run() {
                while(true){
                    while (dH.getMessagesDataChange()) {
                        if(dH.getMessages() != null ){
                            if(!dH.getMessages().isEmpty()){
                                m = new ParseMessages(dH.getMessages(), displayName, localIp);
                                mLists = m.getSortedLists();
                                //Log.d(LOG_TAG,"Scanning messages...");
                                for(final Map.Entry<Long,Message> entry : mLists.entrySet()) {
                                    try {
                                        final String hashed = getChecksum(entry.getValue().getJson(), algorithm);
                                        if(contactName != null && contactIp != null){
                                            if( //this user
                                                    (entry.getValue().getFrom().contentEquals(displayName) && entry.getValue().getFromIp().contentEquals(localIp)) ||
                                                            //or other user is correct
                                                            (entry.getValue().getFrom().contentEquals(contactName) && entry.getValue().getFromIp().contentEquals(contactIp))
                                            ){
                                                if( !mViews.contains(hashed) ){
                                                    mViews.add(hashed);
                                                    //Log.d(LOG_TAG,"Adding scanned msg..."+ entry.getValue().getJson() + ":"  + hashed);
                                                    runOnUiThread(new Runnable() {
                                                        @Override
                                                        public void run() {
                                                            messageAdapter.add(entry.getValue());
                                                            messagesView.setSelection(messagesView.getCount() - 1);
                                                        }
                                                    });
                                                }else{
                                                    //Log.d(LOG_TAG,"Message exist...");
                                                }
                                            }
                                        }
                                    } catch (IOException e) {
                                        e.printStackTrace();
                                    } catch (NoSuchAlgorithmException e) {
                                        //Log.e(LOG_TAG, "Checksum error, NoSuchAlgorithmException - " + algorithm);
                                    }
                                }

                                //Log.i(LOG_TAG,"Last message:" + dH.getLatestMessage());
                            }
                        }
                        try {
                            sleep(500 + new Random().nextInt(1000));
                        } catch (InterruptedException e) {
                            //Log.d(LOG_TAG,"Scanning message interrupted...");
                        }

                        dH.setMessagesDataChange(false);
                    }
                    try {
                        sleep(100);
                    } catch (InterruptedException e) {
                        //Log.e("Thread:", "InterruptedException");
                    }
                }
            }
        }).start();
    }

    private void sendMessage(final String message, final String ip, final String contactName) {
        new Thread(new Runnable() {
            @Override
            public void run() {
                try {
                    Long utcNow = System.currentTimeMillis()/1000;
                    JSONObject payload = new JSONObject();
                    try {
                        final int id = (displayName + localIp).hashCode();
                        payload.put("id", abs(id));
                        payload.put("message", message);
                        payload.put("src", displayName);
                        payload.put("srcIp", localIp);
                        payload.put("dst", contactName);
                        payload.put("dstIp", ip);
                        payload.put("time", utcNow);
                        payload.put("status", 0);//-1 = not sent, 0 = received, 1 = unread
                        final String hashCoded = getChecksum(payload.toString(), algorithm);
                        payload.put("hash", hashCoded);
                        //save message payload to bucket
                        dH.putMessage(hashCoded, payload.toString());
                        if (mLists == null) new TreeMap<Long, Message>();
                        if( !mLists.containsKey(utcNow) ){
                            final Message n = new Message(displayName, localIp, message, false, utcNow);
                            mLists.put(utcNow, n);
                            runOnUiThread(new Runnable() {
                                @Override
                                public void run() {
                                    try {
                                        final String hashed = getChecksum(n.getJson(), algorithm);
                                        if( !mViews.contains(hashed) ) {
                                            //Log.d(LOG_TAG,"Adding sended msg..." + n.getJson() + ":" + hashed);
                                            mViews.add(hashed);
                                            messageAdapter.add(n);
                                            messagesView.setSelection(messagesView.getCount() - 1);
                                        }else{
                                            //Log.d(LOG_TAG,"Message already exist...");
                                        }
                                    } catch (IOException e) {
                                        e.printStackTrace();
                                    } catch (NoSuchAlgorithmException e) {
                                        //Log.e(LOG_TAG, "Checksum error, NoSuchAlgorithmException - " + algorithm);
                                    }
                                }
                            });
                        }
                        InetAddress address = InetAddress.getByName(ip);
                        byte[] data = payload.toString().getBytes();
                        DatagramSocket socket = new DatagramSocket();
                        DatagramPacket packet = new DatagramPacket(data, data.length, address, MSG_BROADCAST_PORT);
                        //Log.i(LOG_TAG, "Sending msg: " + " hash:" + hashCoded + "-payload:"+ payload.toString() + "data length:" + data.length + " to:" + contactIp);
                        socket.send(packet);
                        byte[] ack = new byte[BUF_SIZE];
                        DatagramPacket dp = new DatagramPacket(ack, ack.length);
                        socket.receive(dp);
                        String datas = new String(ack, 0, packet.getLength());
                        if (datas.equals("ACK")) {
                            //Log.i(LOG_TAG, "Msg sent: " + " hash:" + hashCoded + "-payload:"+ payload.toString() + "data length:" + data.length + " to:" + contactIp);
                        }
                        socket.disconnect();
                        socket.close();
                    } catch (JSONException e) {
                        //Log.e(LOG_TAG, "Failure to create JSON.");
                    } catch (NoSuchAlgorithmException e) {
                        //Log.e(LOG_TAG, "Checksum error, NoSuchAlgorithmException - " + algorithm);
                    }
                } catch (UnknownHostException e) {
                    //Log.e(LOG_TAG, "Failure. UnknownHostException in sendMessage: " + contactIp);
                } catch (SocketException e) {
                    //Log.e(LOG_TAG, "Failure. SocketException in sendMessage: " + e);
                } catch (IOException e) {
                    //Log.e(LOG_TAG, "Failure. IOException in sendMessage: " + e);
                }
            }
        }).start();
    }
}

class ParseMessages{
    private String displayName;
    private String localIp;
    private HashMap<String, String> messages;
    private TreeMap<Long, Message> mListspm = new TreeMap<Long, Message>();

    public ParseMessages(HashMap<String, String> messages, String displayName, String localIp) {
        this.messages = messages;
        this.displayName = displayName;
        this.localIp = localIp;
        sortMessages();
    }

    private void sortMessages(){
        if(messages != null ){
            if(!messages.isEmpty()){
                for (HashMap.Entry<String, String> entry : messages.entrySet()) {
                    aMessage m = new aMessage(entry.getValue(), displayName, localIp);
                    final Message message = new Message(m.getSrcName(), m.getSrcIp(), m.getMessageText(), m.getToThisUser(), m.getTime());
                    if( !mListspm.containsKey(m.getTime()) ){
                        mListspm.put(m.getTime(), message);
                    }
                }
            }
        }
    }

    public Map<Long, Message> getSortedLists() {
        return mListspm;
    }

    class aMessage{
        private Integer id;
        private String messageText;
        private String srcName;
        private String srcIp;
        private String dstName;
        private String dstIp;
        private Long time;
        private Integer status;
        private Boolean toThisUser;
        private String displayName;
        private String localIp;

        public aMessage(String json, String displayName, String localIp) {
            this.displayName = displayName;
            this.localIp = localIp;
            try {
                JSONObject messageJson = new JSONObject(json);
                this.id = messageJson.getInt("id");
                this.messageText = messageJson.getString("message");
                this.srcName = messageJson.getString("src");
                this.srcIp = messageJson.getString("srcIp");
                this.dstName = messageJson.getString("dst");
                this.dstIp = messageJson.getString("dstIp");
                this.time = messageJson.getLong("time");
                this.status = messageJson.getInt("status");
                this.toThisUser = toThisUser(dstName, dstIp);
            } catch (JSONException e) {
                //Log.e("JSON:","JSONException");
            }
        }

        private Boolean toThisUser(String dstName, String dstIp){
            if ( dstName.contentEquals(this.displayName) && dstIp.contentEquals(this.localIp) ) return true;
            else return false;
        }

        public Integer getId() {
            return id;
        }

        public String getMessageText() {
            return messageText;
        }

        public String getSrcName() {
            return srcName;
        }

        public String getSrcIp() {
            return srcIp;
        }

        public String getDstName() {
            return dstName;
        }

        public String getDstIp() {
            return dstIp;
        }

        public Long getTime() {
            return time;
        }

        public Integer getStatus() {
            return status;
        }

        public Boolean getToThisUser() {
            return toThisUser;
        }
    }
}