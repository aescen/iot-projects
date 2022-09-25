package id.ac.polinema.pstt.voicechat;

import android.content.Context;
import android.content.Intent;
import android.graphics.PorterDuff;
import android.os.Bundle;
import android.support.design.widget.FloatingActionButton;
import android.support.v4.widget.SwipeRefreshLayout;
import android.support.v7.app.AppCompatActivity;
import android.util.Log;
import android.view.View;
import android.widget.AdapterView;
import android.widget.ListView;
import android.widget.ProgressBar;
import android.widget.Toast;

import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.HashMap;

import static id.ac.polinema.pstt.voicechat.MainActivity.dH;
import static java.lang.Thread.sleep;
import static java.lang.Thread.yield;

public class MsgsActivity extends AppCompatActivity implements AdapterView.OnItemClickListener {
    static final String LOG_TAG = "MsgsActivity";
    private static String localIp = dH.getLocalIp().getHostAddress();
    private static final int SECOND_ACTIVITY_REQUEST_CODE = 0;
    private static final int THIRD_ACTIVITY_REQUEST_CODE = 1;
    private static final String EXTRA_ORIGIN = "ORIGIN";
    private static final String EXTRA_LOCALIP = "LOCALIP";
    private static final String EXTRA_DISPLAYNAME = "DISPLAYNAME";
    private static final String EXTRA_CONTACT = "CONTACT";
    private static final String EXTRA_IP = "IP";
    private SwipeRefreshLayout pullToRefresh;
    private String displayName = dH.getDisplayName();
    private String contactName;
    private String contactIp;
    private MsgsAdapter messageAdapter;
    private ListView messagesView;
    private static ArrayList<String> users = new ArrayList<String>();
    private static boolean scan = false;



    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_msgs);

        Intent intent = getIntent();
        contactName = intent.getStringExtra(EXTRA_CONTACT);
        contactIp = intent.getStringExtra(EXTRA_IP);

        //Log.i(LOG_TAG, "MsgsActivity started!" + displayName + ":" + contactName + ":"  + contactIp);

        //Log.d("dH msgs ip:",dH.getLocalIp().getHostAddress());
        //Log.d("dH msgs bc:",dH.getBcIp().getHostAddress());

        this.pullToRefresh = (SwipeRefreshLayout) findViewById(R.id.pullToRefresh);

        messageAdapter = new MsgsAdapter(this, true);
        messagesView = (ListView) findViewById(R.id.messagesView);
        messagesView.setAdapter(messageAdapter);
        messagesView.setOnItemClickListener(this);

        runOnUiThread(new Runnable() {
            @Override
            public void run() {
                messageAdapter.clear();
            }
        });

        final ProgressBar spinner = (ProgressBar) findViewById(R.id.progressBar);
        spinner.getIndeterminateDrawable().setColorFilter(
                getResources().getColor(R.color.colorPrimary),
                PorterDuff.Mode.SRC_IN);

        //setting an setOnRefreshListener on the SwipeDownLayout
        pullToRefresh.setOnRefreshListener(new SwipeRefreshLayout.OnRefreshListener() {
            @Override
            public void onRefresh() {
                pullToRefresh.setRefreshing(true);
                scan = false;
                scan = true;
                scanMessages();
                pullToRefresh.setRefreshing(false);
            }
        });

        FloatingActionButton fab = (FloatingActionButton) findViewById(R.id.fab);
        fab.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                try{
                    Intent intent = new Intent(MsgsActivity.this, SendMsgActivity.class);
                    intent.putExtra(EXTRA_ORIGIN, "FAB");
                    intent.putExtra(EXTRA_DISPLAYNAME, displayName);
                    intent.putExtra(EXTRA_LOCALIP, localIp);
                    startActivity(intent);
                    //startActivityForResult(intent, THIRD_ACTIVITY_REQUEST_CODE);
                    startActivity(intent);
                }catch (Exception ex){
                    //Toast.makeText(getApplicationContext(), ex.toString(), //Toast.LENGTH_SHORT).show();
                }
            }
        });

        spinner.setVisibility(View.GONE);

//        messagesView.setOnScrollListener(new AbsListView.OnScrollListener() {
//            @Override
//            public void onScrollStateChanged(AbsListView view, int scrollState) {
//
//            }
//
//            @Override
//            public void onScroll(AbsListView view, int firstVisibleItem, int visibleItemCount, int totalItemCount) {
//                int lastItem = firstVisibleItem + visibleItemCount;
//                if (lastItem == totalItemCount && firstVisibleItem > 0) {
//                    fab.hide();
//                }else {
//                    fab.show();
//                }
//            }
//        });
        dH.setMessagesDataChange(true);
        scanMessages();
    }

    private void scanMessages(){
        new Thread(new Runnable() {
            @Override
            public void run() {
                while (scan){
                    while (dH.getMessagesDataChange()) {
                        if(dH.getMessages() != null ){
                            if(!dH.getMessages().isEmpty()){
                                for (HashMap.Entry<String, String> entry : dH.getMessages().entrySet()) {
                                    final String key = entry.getKey();
                                    try {
                                        JSONObject messageJson = new JSONObject(entry.getValue());
                                        Integer id = messageJson.getInt("id");
                                        String messageText = messageJson.getString("message");
                                        String srcName = messageJson.getString("src");
                                        String srcIp = messageJson.getString("srcIp");
                                        String dstName = messageJson.getString("dst");
                                        String dstIp = messageJson.getString("dstIp");
                                        long time = messageJson.getLong("time");
                                        Integer status = messageJson.getInt("status");
                                        //Log.i(LOG_TAG, "New message: " + entry.getValue());
                                        boolean toThisUser = toThisUser(entry.getValue());
                                        if(toThisUser){
                                            if(!users.contains(srcName)){
                                                //Log.i("Users:", "adding.");
                                                users.add(srcName);
                                                final Message message = new Message(srcName, srcIp, messageText, toThisUser, time);
                                                runOnUiThread(
                                                        new Runnable() {
                                                            @Override
                                                            public void run(){
                                                                messageAdapter.add(message);
                                                                messagesView.setSelection(messagesView.getCount() - 1);
                                                            }
                                                        });
                                            }else{
                                                //Log.i("Users:", "exist.");
                                            }
                                        }else{
                                            if(!users.contains(dstName)){
                                                //Log.i("Users:", "adding.");
                                                users.add(dstName);
                                                final Message message = new Message(dstName, dstIp, messageText, !toThisUser, time);
                                                runOnUiThread(
                                                        new Runnable() {
                                                            @Override
                                                            public void run(){
                                                                messageAdapter.add(message);
                                                                messagesView.setSelection(messagesView.getCount() - 1);
                                                            }
                                                        });
                                            }else {
                                                //Log.i("Users:", "exist.");
                                            }
                                        }
                                    } catch (JSONException e) {
                                        e.printStackTrace();
                                        return;
                                    }
                                }
                            }
                        }
                        dH.setMessagesDataChange(false);
                    }
                    try {
                        sleep(500);
                    } catch (InterruptedException e) {
                        //Log.e("Thread:", "InterruptedException");
                    }
                }
                users.clear();
                runOnUiThread(new Runnable() {
                    @Override
                    public void run() {
                        messageAdapter.clear();
                    }
                });

            }
        }).start();
    }

    public void onItemClick(AdapterView<?> l, View v, int position, long id) {
        ////Log.i(LOG_TAG + "@ListView", "You clicked Item: " + id + " at position:" + position);
        Message obj = (Message) messagesView.getAdapter().getItem(position);
        String value = obj.getJson();
        ////Log.d(LOG_TAG + "@ListView", "Value is: "+value);
        Intent intent = new Intent(MsgsActivity.this, SendMsgActivity.class);
        intent.putExtra(EXTRA_ORIGIN, "MSGS");
        intent.putExtra(EXTRA_CONTACT, obj.getFrom());
        intent.putExtra(EXTRA_IP, obj.getFromIp());
        //intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TASK | Intent.FLAG_ACTIVITY_NO_HISTORY);
        startActivity(intent);
        //startActivityForResult(intent, THIRD_ACTIVITY_REQUEST_CODE);
    }

    // This method is called when the third activity finishes
    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);

        // check that it is the SecondActivity with an OK result
//        if (requestCode == THIRD_ACTIVITY_REQUEST_CODE) {
//            if (resultCode == RESULT_OK) {
//                // get String data from Intent
//                this.messages = (HashMap<Integer, String>) data.getSerializableExtra(EXTRA_MAP);
//            }
//        }
    }

    @Override
        public void onBackPressed() {
        super.onBackPressed();
        finish();
        //startActivity(intent);
    }

    @Override
    public void onPause() {
        super.onPause();
        scan = false;
    }
//
    @Override
    public void onResume(){
        super.onResume();
        users.clear();
        runOnUiThread(new Runnable() {
            @Override
            public void run() {
                messageAdapter.clear();
            }
        });
        scan = true;
        scanMessages();
    }
//
    @Override
    public void onRestart(){
        super.onRestart();
        users.clear();
        runOnUiThread(new Runnable() {
            @Override
            public void run() {
                messageAdapter.clear();
            }
        });
        scan = true;
        scanMessages();
    }
//
//    @Override
//    public void onStart(){
//        super.onStart();
//    }
//
//    @Override
//    public void onStop(){
//        super.onStop();
//    }
//
//    @Override
//    public void onDestroy(){
//        super.onDestroy();
//    }

    public boolean toThisUser(String json){
        try {
            JSONObject data = new JSONObject(json);
            String dst = data.getString("dst");
            String dstIp = data.getString("dstIp");
            if ( dst.contentEquals(this.displayName) && dstIp.contentEquals(localIp) ) {
                return true;
            }
        } catch (JSONException e) {
            e.printStackTrace();
        }
        return false;
    }
}
