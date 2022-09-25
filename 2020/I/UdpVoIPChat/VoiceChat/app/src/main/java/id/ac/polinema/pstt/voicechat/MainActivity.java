package id.ac.polinema.pstt.voicechat;

import android.Manifest;
import android.app.AlertDialog;
import android.app.PendingIntent;
import android.content.DialogInterface;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.graphics.Color;
import android.os.Bundle;
import android.support.annotation.NonNull;
import android.support.v4.app.ActivityCompat;
import android.support.v4.app.TaskStackBuilder;
import android.support.v4.content.ContextCompat;
import android.support.v7.app.AppCompatActivity;
import android.util.Log;
import android.view.View;
import android.view.View.OnClickListener;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.RadioButton;
import android.widget.RadioGroup;
import android.widget.Toast;

import java.io.IOException;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.net.SocketException;
import java.net.SocketTimeoutException;
import java.net.UnknownHostException;
import java.util.HashMap;
import java.util.Map;
import java.util.Timer;
import java.util.TimerTask;

import static java.lang.Thread.sleep;

public class MainActivity extends AppCompatActivity {
    public static final String EXTRA_DISPLAYNAME = "DISPLAYNAME";
    public static final String EXTRA_CONTACT = "CONTACT";
    public static final String EXTRA_IP = "IP";
    public static final String algorithm = "SHA1";
    //variables
	private static final String LOG_TAG = "Voice Chat";
    private static final String EXTRA_ORIGIN = "ORIGIN";
    private static final String EXTRA_LOCALIP = "LOCALIP";
    private static final int LISTENER_PORT = 50003;
    private static final int BUF_SIZE = 1024;
    private static final int SECOND_ACTIVITY_REQUEST_CODE = 0;
    private static final int THIRD_ACTIVITY_REQUEST_CODE = 1;
    private static final int MICROPHONE_PERMISSION_CODE = 101;
    public static DataHolder dH = DataHolder.getInstance();
    private static String localIp;
    private static InetAddress bcIp;
    private ContactManager contactManager;
    private MsgsManager msgsManager;
    private String displayName;
    private Boolean STARTED;
    private boolean IN_CALL = false;
    private boolean IN_MSG = false;
    private boolean LISTEN = false;

    //on activity creation
	@Override
    protected void onCreate(Bundle savedInstanceState) {

        super.onCreate(savedInstanceState);
        // Check whether we're recreating a previously destroyed instance
//        if (savedInstanceState != null) {
//            // Restore value of members from saved state
////        private static HashMap<String, InetAddress> sContacts = new HashMap<String, InetAddress>();
////        private static HashMap<Integer, String> sUsers = new HashMap<>();
////        private static HashMap<String, String> sMessages = new HashMap<String, String>();
////        private static Boolean sLISTEN_MSG;
////        private static Boolean sLISTEN_WIFI;
////        private static String sDisplayName;
////        private static InetAddress sLocalIp;
////        private static InetAddress sBcIp;
//
//        } else {
//            // Probably initialize members with default values for a new instance
//        }

        setContentView(R.layout.activity_main);

        ////Log.i(LOG_TAG, "voicechat started");

        checkPermission(Manifest.permission.RECORD_AUDIO, MICROPHONE_PERMISSION_CODE);

        if(IpUtils.isWiFiAvailable()){
            dH.setLocalIp(IpUtils.getLocalIpAddress());
            dH.setBcIp(IpUtils.getBroadcastIp());
            localIp = dH.getLocalIp().getHostAddress();
            bcIp = dH.getBcIp();
            ////Log.d("dH main ip:",dH.getLocalIp().getHostAddress());
            ////Log.d("dH main bc:",dH.getBcIp().getHostAddress());
        } else {
            runOnUiThread(new Runnable() {
                @Override
                public void run() {
                    try {
                        final AlertDialog alert = new AlertDialog.Builder(MainActivity.this).create();
                        alert.setTitle("Oops ...");
                        alert.setMessage("WiFi seems offline, exiting.");
                        alert.setButton(-1, "OK", new DialogInterface.OnClickListener() {
                            public void onClick(DialogInterface dialog, int which) {
                                alert.dismiss();
                                finishAffinity();
                            }
                        });
                        alert.show();
                    } catch (Exception ex) {
                        ex.printStackTrace();
                    }
                }
            });
        }

        // START BUTTON
        // Pressing this buttons initiates the main functionality
        final Button btnStart = findViewById(R.id.buttonStart);
        btnStart.setOnClickListener(new OnClickListener() {

            //on start button click
			@Override
            public void onClick(View v) {
                ////Log.i(LOG_TAG, "Start button pressed");
                STARTED = true;

                //get name
				EditText displayNameText = findViewById(R.id.editTextDisplayName);
                displayName = displayNameText.getText().toString();
                if(displayName.length() == 0){
                    final AlertDialog alert = new AlertDialog.Builder(MainActivity.this).create();
                    alert.setTitle("Oops ...");
                    alert.setMessage("You must enter name first");
                    alert.setButton(-1, "Ok", new DialogInterface.OnClickListener() {
                        @Override
                        public void onClick(DialogInterface dialogInterface, int which) {
                            alert.dismiss();
                        }
                    });
                    alert.show();
                }else {
                    displayName.length();
                    dH.setDisplayName(displayName);

                    //disable name text & start button
                    displayNameText.setEnabled(false);
                    btnStart.setEnabled(false);
                    btnStart.setEnabled(false);
                    btnStart.setClickable(false);

                    //enable select contact
                    LinearLayout lL = findViewById(R.id.contactLayout);
                    lL.setVisibility(View.VISIBLE);

                    //enable update button
                    Button updateButton = findViewById(R.id.buttonUpdate);
                    updateButton.setVisibility(View.VISIBLE);
                    updateButton.setEnabled(true);
                    updateButton.setClickable(true);

                    //enable call button
                    Button callButton = findViewById(R.id.buttonCall);
                    callButton.setVisibility(View.VISIBLE);
                    callButton.setEnabled(false);
                    callButton.setClickable(false);

                    //enable message button
                    Button messageButton = findViewById(R.id.buttonMessage);
                    messageButton.setVisibility(View.VISIBLE);
                    messageButton.setEnabled(false);
                    messageButton.setClickable(false);

                    //enable messages button
                    Button btMsgs = findViewById(R.id.buttonMessages);
                    btMsgs.setVisibility(View.VISIBLE);
                    btMsgs.setEnabled(true);
                    btMsgs.setClickable(true);

                    //call managers
                    dH.setListenMsg(true);
                    contactManager = new ContactManager(displayName, bcIp);
                    msgsManager = new MsgsManager(displayName, localIp);
                    startCallListener();
                }
            }
        });

        // UPDATE BUTTON
        // Updates the list of reachable devices
        final Button btnUpdate = findViewById(R.id.buttonUpdate);
        btnUpdate.setOnClickListener(new OnClickListener() {

            @Override
            public void onClick(View v) {
                updateContactList();
                Button callButton = findViewById(R.id.buttonCall);
                Button messageButton = findViewById(R.id.buttonMessage);
                if(contactManager != null ){
                    if(!contactManager.getContacts().isEmpty()){
                        //enable call button
                        callButton.setVisibility(View.VISIBLE);
                        callButton.setEnabled(true);
                        callButton.setClickable(true);

                        //enable message button
                        messageButton.setVisibility(View.VISIBLE);
                        messageButton.setEnabled(true);
                        messageButton.setClickable(true);
                    }else{
                        //enable call button
                        callButton.setVisibility(View.VISIBLE);
                        callButton.setEnabled(false);
                        callButton.setClickable(false);

                        //enable message button
                        messageButton.setVisibility(View.VISIBLE);
                        messageButton.setEnabled(false);
                        messageButton.setClickable(false);
                    }
                }
                else{
                    //enable call button
                    callButton.setVisibility(View.VISIBLE);
                    callButton.setEnabled(false);
                    callButton.setClickable(false);

                    //enable message button
                    messageButton.setVisibility(View.VISIBLE);
                    messageButton.setEnabled(false);
                    messageButton.setClickable(false);
                }
            }
        });

        // CALL BUTTON
        // Attempts to initiate an audio chat session with the selected device
        final Button btnCall = findViewById(R.id.buttonCall);
        btnCall.setOnClickListener(new OnClickListener() {

            @Override
            public void onClick(View v) {
                RadioGroup radioGroup = findViewById(R.id.contactList);
                int selectedButton = radioGroup.getCheckedRadioButtonId();
                if(selectedButton == -1) {
                    // If no device was selected, present an error message to the user
                    ////Log.w(LOG_TAG, "Warning: no contact selected");
                    final AlertDialog alert = new AlertDialog.Builder(MainActivity.this).create();
                    alert.setTitle("Oops ...");
                    alert.setMessage("You must select a contact first");
                    alert.setButton(-1, "Ok", new DialogInterface.OnClickListener() {
                        public void onClick(DialogInterface dialog, int which) {
                            alert.dismiss();
                        }
                    });
                    alert.show();
                    return;
                }
                // Collect details about the selected contact
                RadioButton radioButton = findViewById(selectedButton);
                String contact = radioButton.getText().toString();
                InetAddress ip = contactManager.getContacts().get(contact);
                IN_CALL = true;

                // Send this information to the MakeCallActivity and start that activity
                Intent intent = new Intent(MainActivity.this, MakeCallActivity.class);
                intent.putExtra(EXTRA_CONTACT, contact);
                String address = ip.toString();
                address = address.substring(1);
                intent.putExtra(EXTRA_IP, address);
                intent.putExtra(EXTRA_DISPLAYNAME, displayName);
                startActivity(intent);
            }
        });

        // MSG BUTTON (attempts to intiate an text chat session with the selected device)
        final Button btnMsg = findViewById(R.id.buttonMessage);
        btnMsg.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {

                RadioGroup radioGroup = findViewById(R.id.contactList);
                int selectedButton = radioGroup.getCheckedRadioButtonId();
                if (selectedButton == -1) {

                    //if no device was selected, present an error message to the user
                    ////Log.w(LOG_TAG, "Warning: no contact selected");
                    final AlertDialog alert = new AlertDialog.Builder(MainActivity.this).create();
                    alert.setTitle("Oops ...");
                    alert.setMessage("You must selected a contact first");
                    alert.setButton(-1, "Ok", new DialogInterface.OnClickListener() {
                        @Override
                        public void onClick(DialogInterface dialogInterface, int which) {
                        alert.dismiss();
                        }
                    });
                    alert.show();
                    return;
                }

                //collect details about the selected contact
                RadioButton radioButton = findViewById(selectedButton);
                String contact = radioButton.getText().toString();
                InetAddress ip = contactManager.getContacts().get(contact);
                IN_MSG = true;

                //send this information to the SendMsgActivity and start that activity
                String address = ip.toString();
                address = address.substring(1);
                final String finalContact = contact;
                final String finalAddress = address;
                try{
                    //Toast.makeText(getApplicationContext(), "Start msgs", //Toast.LENGTH_SHORT).show();
                    Intent intent = new Intent(MainActivity.this, SendMsgActivity.class);
                    intent.putExtra(EXTRA_ORIGIN, "MAIN");
                    intent.putExtra(EXTRA_DISPLAYNAME, displayName);
                    intent.putExtra(EXTRA_LOCALIP, IpUtils.getLocalIpAddress());
                    intent.putExtra(EXTRA_CONTACT, finalContact);
                    intent.putExtra(EXTRA_IP, finalAddress);
                    startActivity(intent);
                }catch (Exception ex){
                    //Toast.makeText(getApplicationContext(), ex.toString(), //Toast.LENGTH_SHORT).show();
                }
            }
        });

        // MSGS BUTTON (attempts to intiate an text chat session with the selected device)
        final Button btnMsgs = findViewById(R.id.buttonMessages);
        btnMsgs.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                try {
                    IN_MSG = true;
                    //send this information to the SendMsgActivity and start that activity
                    Intent intent = new Intent(MainActivity.this, MsgsActivity.class);
                    //intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TASK | Intent.FLAG_ACTIVITY_NO_HISTORY);
                    //startActivityForResult(intent, SECOND_ACTIVITY_REQUEST_CODE);
                    startActivity(intent);
                }catch (Exception ex){
                    //Toast.makeText(getApplicationContext(), ex.toString(), //Toast.LENGTH_SHORT).show();
                }
            }
        });

    }

    @Override
    public void onSaveInstanceState(Bundle savedInstanceState) {
        // Save the user's current UI state
        savedInstanceState.putSerializable("sContacts", dH.getContacts());
        savedInstanceState.putSerializable("sUsers", dH.getUsers());
        savedInstanceState.putSerializable("sMessages", dH.getMessages());
        savedInstanceState.putBoolean("sLISTEN_WIFI", dH.getListenWiFi());
        savedInstanceState.putBoolean("sLISTEN_MSG", dH.getListenMsg());
        savedInstanceState.putString("sDisplayName", dH.getDisplayName());
        savedInstanceState.putString("sLocalIp", dH.getLocalIp().getHostAddress());
        savedInstanceState.putString("sBcIp", dH.getBcIp().getHostAddress());
        // Always call the superclass so it can save the view hierarchy state
        super.onSaveInstanceState(savedInstanceState);
    }


    @Override
    public void onBackPressed() {
        super.onBackPressed();
        IN_CALL = false;
        IN_MSG = false;
        onStop();
    }

    @Override
    public void onPause() {
        super.onPause();
        //Log.i(LOG_TAG, "Main activity paused!");
    }

    @Override
    public void onStop() {
        super.onStop();
        if(STARTED == null){
            finish();
            finishAffinity();
        } else if(STARTED && !IN_CALL && !IN_MSG) {
            contactManager.bye(displayName);
            contactManager.stopBroadcasting();
            contactManager.stopListening();
            msgsManager.stopListening();
            //STARTED = false;
            stopCallListener();
            ////Log.i(LOG_TAG, "App stopped!");
            //destroy app state from memory
            finish();
            finishAffinity();
        } else {
            //Log.i(LOG_TAG, "App on other activity!");
        }
    }

    @Override
    public void onRestart() {
        super.onRestart();
        ////Log.i(LOG_TAG, "App restarted!");
        IN_CALL = false;
        IN_MSG = false;
        STARTED = true;
        if(dH == null) {
            dH = DataHolder.getInstance();
        }
        if (contactManager == null){
            contactManager = new ContactManager(displayName, bcIp);
        }
        if(msgsManager == null){
            msgsManager = new MsgsManager(displayName,localIp);
        }
        updateContactList();
        //startCallListener();
    }

    // This method is called when the second activity finishes
    @Override
    @SuppressWarnings("unchecked")
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);

        // check that it is the SecondActivity or ThirdActivity with an OK result
        if (resultCode == RESULT_OK) {
            // get String data from Intent
        }
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions, @NonNull int[] grantResults){
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);

        if (requestCode == MICROPHONE_PERMISSION_CODE) {
            if (grantResults.length > 0
                    && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                //Toast.makeText(MainActivity.this,"Microphone Permission Granted", Toast.LENGTH_SHORT).show();
            }
            else {
                Toast.makeText(MainActivity.this, "Microphone Permission Denied", Toast.LENGTH_SHORT).show();
            }
        }
    }

    // Function to check and request permission.
    public void checkPermission(String permission, int requestCode)
    {
        if (ContextCompat.checkSelfPermission(MainActivity.this, permission)
                == PackageManager.PERMISSION_DENIED) {

            // Requesting the permission
            ActivityCompat.requestPermissions(MainActivity.this,
                    new String[] { permission },
                    requestCode);
        }
    }

    private void updateContactList() {
        // Create a copy of the HashMap used by the ContactManager
        HashMap<String, InetAddress> contacts = contactManager.getContacts();
        // Create a radio button for each contact in the HashMap
        RadioGroup radioGroup = findViewById(R.id.contactList);
        radioGroup.removeAllViews();

        for(String name : contacts.keySet()) {

            RadioButton radioButton = new RadioButton(getBaseContext());
            radioButton.setText(name);
            radioButton.setTextColor(Color.BLACK);
            radioGroup.addView(radioButton);
        }

        radioGroup.clearCheck();
    }

    private void startCallListener() {
        // Creates the listener thread
        LISTEN = true;
        Thread listener = new Thread(new Runnable() {

            @Override
            public void run() {
                try {
                    // Set up the socket and packet to receive
                    ////Log.i(LOG_TAG, "Incoming call listener started");
                    DatagramSocket socket = new DatagramSocket(LISTENER_PORT);
                    socket.setSoTimeout(5000);
                    byte[] buffer = new byte[BUF_SIZE];
                    DatagramPacket packet = new DatagramPacket(buffer, BUF_SIZE);
                    while(LISTEN) {
                        // Listen for incoming call requests
                        try {
                            ////Log.i(LOG_TAG, "Listening for incoming calls");
                            socket.receive(packet);
                            String data = new String(buffer, 0, packet.getLength());
                            ////Log.i(LOG_TAG, "Packet received from "+ packet.getAddress() +" with contents: " + data);
                            String action = data.substring(0, 4);
                            if(action.equals("CAL:")) {
                                // Received a call request. Start the ReceiveCallActivity
                                String address = packet.getAddress().toString();
                                String name = data.substring(4, packet.getLength());

                                Intent intent = new Intent(MainActivity.this, ReceiveCallActivity.class);
                                intent.putExtra(EXTRA_CONTACT, name);
                                intent.putExtra(EXTRA_IP, address.substring(1));
                                IN_CALL = true;
                                //LISTEN = false;
                                //stopCallListener();

                                startActivity(intent);
                            }
                            else {
                                // Received an invalid request
                                ////Log.w(LOG_TAG, packet.getAddress() + " sent invalid message: " + data);
                            }
                        } catch (SocketTimeoutException e) {
                            ////Log.i(LOG_TAG, "No packet received yet.");
                        }
                        catch (IOException e) {
                            ////Log.e(LOG_TAG, "IOException in listen: " + e);
                        }
                    }
                    ////Log.i(LOG_TAG, "Call Listener ending");
                    socket.disconnect();
                    socket.close();
                }
                catch(SocketException e) {

                    ////Log.e(LOG_TAG, "SocketException in listener " + e);
                }
            }
        });
        listener.start();
    }

    private void stopCallListener() {
        // Ends the listener thread
        LISTEN = false;
    }
}
