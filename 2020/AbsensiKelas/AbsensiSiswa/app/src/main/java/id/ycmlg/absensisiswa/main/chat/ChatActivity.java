package id.ycmlg.absensisiswa.main.chat;

import android.app.Activity;
import android.content.Intent;
import android.graphics.Color;
import android.os.Build;
import android.os.Bundle;
import android.text.Editable;
import android.text.SpannableString;
import android.text.TextWatcher;
import android.text.style.ForegroundColorSpan;
import android.text.style.RelativeSizeSpan;
import android.view.Gravity;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.view.ViewGroup;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AlertDialog;
import androidx.appcompat.app.AppCompatActivity;
import androidx.appcompat.widget.Toolbar;
import androidx.swiperefreshlayout.widget.SwipeRefreshLayout;

import com.google.android.material.floatingactionbutton.FloatingActionButton;
import com.google.firebase.database.ChildEventListener;
import com.google.firebase.database.DataSnapshot;
import com.google.firebase.database.DatabaseError;
import com.google.firebase.database.DatabaseReference;
import com.google.firebase.database.FirebaseDatabase;

import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import hani.momanii.supernova_emoji_library.Actions.EmojIconActions;
import hani.momanii.supernova_emoji_library.Helper.EmojiconEditText;
import hani.momanii.supernova_emoji_library.Helper.EmojiconTextView;
import id.ycmlg.absensisiswa.R;
import id.ycmlg.absensisiswa.main.chat.chatmodels.Message;
import id.ycmlg.absensisiswa.main.chat.chatmodels.StaticInfo;
import id.ycmlg.absensisiswa.main.chat.chatmodels.User;
import id.ycmlg.absensisiswa.main.chat.chatservices.AppService;
import id.ycmlg.absensisiswa.main.chat.chatservices.DataContext;
import id.ycmlg.absensisiswa.data.LocalUserService;
import id.ycmlg.absensisiswa.main.chat.chatservices.Tools;

public class ChatActivity extends AppCompatActivity {
    DataContext db = new DataContext(this, null, null, 1);
    EditText messageArea;
    ScrollView scrollView;
    LinearLayout layout;
    FirebaseDatabase database;
    DatabaseReference reference1, reference2, refNotMess, refFriend;
    User user;
    String friendEmail;
    DatabaseReference refUser;
    private int pageNo = 2;
    private FloatingActionButton submit_btn;

    private ChildEventListener reference1Listener;
    private ChildEventListener refFriendListener;
    private String friendFullName = "";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_chat);
        Toolbar toolbar = findViewById(R.id.toolbarChatActivity);
        setSupportActionBar(toolbar);
        messageArea = findViewById(R.id.et_Message);
        scrollView = findViewById(R.id.scrollView);
        layout = findViewById(R.id.layout1);
        database = FirebaseDatabase.getInstance();
        user = LocalUserService.getLocalUserFromPreferences(this);

        reference1Listener = new ChildEventListener() {
            @Override
            public void onChildAdded(DataSnapshot dataSnapshot, String s) {

                if (!dataSnapshot.getKey().equals(StaticInfo.TypingStatus)) {
                    Map map = (Map)dataSnapshot.getValue();
                    String mess = map.get("Message").toString();
                    String senderEmail = map.get("SenderEmail").toString();
                    String sentDate = map.get("SentDate").toString();
                    try {
                        // remove from server
                        reference1.child(dataSnapshot.getKey()).removeValue();
                        // save message on local db
                        db.saveMessageOnLocalDB(senderEmail, user.Email, mess, sentDate);
                        if (senderEmail.equals(user.Email)) {
                            // login user
                            appendMessage(mess, sentDate, 1, false);
                        } else {
                            appendMessage(mess, sentDate, 2, false);
                        }
                    } catch (Exception e) {

                    }
                } else {
                    // show typing status
                    String typingStatus = dataSnapshot.getValue().toString();
                    if (typingStatus.equals("Typing")) {
                        getSupportActionBar().setSubtitle(typingStatus + "...");
                    }
                }

            }

            @Override
            public void onChildChanged(DataSnapshot dataSnapshot, String s) {
                String typingStatus = dataSnapshot.getValue().toString();
                if (typingStatus.equals("Typing")) {
                    getSupportActionBar().setSubtitle(typingStatus + "...");
                } else {
                    // check if online
                    getSupportActionBar().setSubtitle("Online");
                }
            }

            @Override
            public void onChildRemoved(DataSnapshot dataSnapshot) {
                //layout.removeAllViews();
                if (dataSnapshot.getKey().equals("TypingStatus")) {
                    getSupportActionBar().setSubtitle("Online");

                }
            }

            @Override public void onChildMoved(DataSnapshot dataSnapshot, String s) { }
            @Override public void onCancelled(@NonNull DatabaseError error) { }

        };
        refFriendListener = new ChildEventListener() {
            @Override
            public void onChildAdded(DataSnapshot dataSnapshot, String s) {
                if (dataSnapshot.getKey().equals("Status")) {
                    // check if subtitle is not Typing
                    CharSequence subTitle = getSupportActionBar().getSubtitle();
                    if (subTitle != null) {
                        if (!subTitle.equals("Typing...")) {
                            String friendStatus = dataSnapshot.getValue().toString();
                            if (!friendStatus.equals("Online")) {
                                friendStatus = Tools.lastSeenProper(friendStatus);
                            }
                            getSupportActionBar().setSubtitle(friendStatus);
                        }
                    } else {
                        String friendStatus = dataSnapshot.getValue().toString();
                        if (!friendStatus.equals("Online")) {
                            friendStatus = Tools.lastSeenProper(friendStatus);
                        }
                        getSupportActionBar().setSubtitle(friendStatus);
                    }


                }

            }

            @Override
            public void onChildChanged(DataSnapshot dataSnapshot, String s) {
                String friendStatus = dataSnapshot.getValue().toString();
                if (!friendStatus.equals("Online")) {
                    friendStatus = Tools.lastSeenProper(friendStatus);
                }
                getSupportActionBar().setSubtitle(friendStatus);
            }

            @Override public void onChildRemoved(DataSnapshot dataSnapshot) { }
            @Override public void onChildMoved(DataSnapshot dataSnapshot, String s) { }
            @Override public void onCancelled(@NonNull DatabaseError error) { }
        };
        Bundle extras = getIntent().getExtras();
        friendEmail = extras.getString("FriendEmail");
        List<Message> chatList = db.getChat(user.Email, friendEmail, 1);
        for (Message item : chatList) {
            int messageType = item.FromMail.equals(user.Email) ? 1 : 2;
            appendMessage(item.Message, item.SentDate, messageType, false);
        }

        friendFullName = extras.getString("FriendFullName");

        getSupportActionBar().setTitle(friendFullName);
        reference1 = database.getReferenceFromUrl(StaticInfo.MessagesEndPoint + "/" + Tools.encodeString(user.Email) + "-@@-" + Tools.encodeString(friendEmail));
        reference2 = database.getReferenceFromUrl(StaticInfo.MessagesEndPoint + "/" + Tools.encodeString(friendEmail) + "-@@-" + Tools.encodeString(user.Email));
        refFriend = database.getReferenceFromUrl(StaticInfo.UsersURL + "/" + Tools.encodeString(friendEmail));
        refNotMess = database.getReferenceFromUrl(StaticInfo.NotificationEndPoint + "/" + Tools.encodeString(friendEmail));
        refFriend.addChildEventListener(refFriendListener);
        StaticInfo.UserCurrentChatFriendEmail = friendEmail;
        refUser = database.getReferenceFromUrl(StaticInfo.UsersURL + "/" + Tools.encodeString(user.Email));
        submit_btn = findViewById(R.id.submit_btn);

        messageArea.addTextChangedListener(new TextWatcher() {
            @Override
            public void beforeTextChanged(CharSequence s, int start, int count, int after) {

            }

            @Override
            public void onTextChanged(CharSequence s, int start, int before, int count) {
                if (messageArea.getText().toString().length() == 0) {
                    reference2.child(StaticInfo.TypingStatus).setValue("");
                } else if (messageArea.getText().toString().length() == 1) {
                    reference2.child(StaticInfo.TypingStatus).setValue("Typing");
                    // change color here
                    //  submit_btn.setColorFilter(R.color.colorPrimary);

                }
            }

            @Override
            public void afterTextChanged(Editable s) {

            }
        });

        View rootView = findViewById(R.id.rootLayout);
        EmojiconEditText emojiconEditText = findViewById(R.id.et_Message);
        ImageView emojiImageView = findViewById(R.id.emoji_btn);

        final EmojIconActions emojIcon = new EmojIconActions(this, rootView, emojiconEditText, emojiImageView, "#1c2764", "#e8e8e8", "#f4f4f4");
        emojIcon.ShowEmojIcon();

        emojIcon.setKeyboardListener(new EmojIconActions.KeyboardListener() {
            @Override
            public void onKeyboardOpen() {
                scrollView.post(() -> scrollView.fullScroll(View.FOCUS_DOWN));
            }
            @Override public void onKeyboardClose() { }
        });

        final SwipeRefreshLayout swipeRefreshLayout = findViewById(R.id.swiperefresh);

        swipeRefreshLayout.setOnRefreshListener(() -> {
            List<Message> chatList1 = db.getChat(user.Email, friendEmail, pageNo);
            layout.removeAllViews();
            for (Message item : chatList1) {
                int messageType = item.FromMail.equals(user.Email) ? 1 : 2;
                appendMessage(item.Message, item.SentDate, messageType, true);
            }
            swipeRefreshLayout.setRefreshing(false);
            pageNo++;
        });


        // getSupportActionBar().setDisplayHomeAsUpEnabled(true);
        toolbar.setOnClickListener(v -> {
            Intent intent = new Intent(ChatActivity.this, ChatFriendProfileActivity.class);
            intent.putExtra("Email", friendEmail);
            startActivityForResult(intent, StaticInfo.ChatAciviityRequestCode);
        });

    }

    @Override
    protected void onStart() {
        super.onStart();
        Bundle extras = getIntent().getExtras();
        friendEmail = extras.getString("FriendEmail");

        // getSupportActionBar().setTitle(extras.getString("FriendFullName"));
        // getSupportActionBar().setIcon(R.drawable.dp_placeholder_sm);

        scrollView.post(new Runnable() {
            @Override
            public void run() {
                scrollView.fullScroll(View.FOCUS_DOWN);
            }
        });
        StaticInfo.UserCurrentChatFriendEmail = friendEmail;
        // update status to online
        refUser.child("Status").setValue("Online");
        reference1.addChildEventListener(reference1Listener);
        if (!LocalUserService.isAppServiceRunning(this)) {
            try {
                if(LocalUserService.isAppVisible()) startService(new Intent(this, AppService.class));
            } catch (Exception e) {
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                    startForegroundService(new Intent(this, AppService.class));
                }
                e.printStackTrace();
            }
            //Toast.makeText(this, "Running service ...", Toast.LENGTH_SHORT).show();
        }
    }


    @Override
    protected void onPause() {
        super.onPause();
        reference1.removeEventListener(reference1Listener);
        LocalUserService.appPaused();
    }

    @Override
    protected void onRestart() {
        super.onRestart();
        StaticInfo.UserCurrentChatFriendEmail = friendEmail;
        refUser.child("Status").setValue("Online");
    }

    @Override
    protected void onStop() {
        super.onStop();
        StaticInfo.UserCurrentChatFriendEmail = "";
        reference1.removeEventListener(reference1Listener);
        reference2.child(StaticInfo.TypingStatus).setValue("");
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        StaticInfo.UserCurrentChatFriendEmail = "";
        // set last seen
        DateFormat dateFormat = new SimpleDateFormat("dd MM yy hh:mm a");
        Date date = new Date();
        refUser.child("Status").setValue(dateFormat.format(date));
        reference1.removeEventListener(reference1Listener);
        reference2.child(StaticInfo.TypingStatus).setValue("");
    }

    @Override
    protected void onNewIntent(Intent intent) {
        super.onNewIntent(intent);

        Bundle extras = intent.getExtras();
        layout.removeAllViews();
        friendEmail = extras.getString("FriendEmail");
        friendFullName = extras.getString("FriendFullName");
        getSupportActionBar().setTitle(friendFullName);
        List<Message> chatList = db.getChat(user.Email, friendEmail, 1);
        for (Message item : chatList) {
            int messageType = item.FromMail.equals(user.Email) ? 1 : 2;
            appendMessage(item.Message, item.SentDate, messageType, false);
        }

        StaticInfo.UserCurrentChatFriendEmail = friendEmail;
        reference1.removeEventListener(reference1Listener);
        reference1 = database.getReferenceFromUrl(StaticInfo.MessagesEndPoint + "/" + Tools.encodeString(user.Email) + "-@@-" + Tools.encodeString(friendEmail));
        reference1.addChildEventListener(reference1Listener);

        refFriend.removeEventListener(refFriendListener);
        refFriend = database.getReferenceFromUrl(StaticInfo.UsersURL + "/" + Tools.encodeString(friendEmail));
        refFriend.addChildEventListener(refFriendListener);

        reference2 = database.getReferenceFromUrl(StaticInfo.MessagesEndPoint + "/" + Tools.encodeString(friendEmail) + "-@@-" + Tools.encodeString(user.Email));

    }

    public void btn_SendMessageClick(View view) {

        String message = messageArea.getText().toString().trim();
        messageArea.setText("");
        if (!message.equals("")) {
            Map<String, String> map = new HashMap<>();
            map.put("Message", message);
            map.put("SenderEmail", user.Email);
            map.put("FirstName", user.FirstName);
            map.put("LastName", user.LastName);

            DateFormat dateFormat = new SimpleDateFormat("dd MM yy hh:mm a");
            Date date = new Date();
            String sentDate = dateFormat.format(date);

            map.put("SentDate", sentDate);
            //reference1.push().setValue(map);
            reference2.push().setValue(map);
            refNotMess.push().setValue(map);

            // save in local db
            db.saveMessageOnLocalDB(user.Email, friendEmail, message, sentDate);

            // appendmessage
            appendMessage(message, sentDate, 1, false);

        }
    }

    public void appendMessage(String mess, String sentDate, int messType, final boolean scrollUp) {

        EmojiconTextView textView = new EmojiconTextView(this);
        textView.setEmojiconSize(30);
        sentDate = Tools.messageSentDateProper(sentDate);
        SpannableString dateString = new SpannableString(sentDate);
        dateString.setSpan(new RelativeSizeSpan(0.7f), 0, sentDate.length(), 0);
        dateString.setSpan(new ForegroundColorSpan(Color.GRAY), 0, sentDate.length(), 0);

        textView.setText(mess + "\n");
        textView.append(dateString);
        textView.setTextColor(Color.parseColor("#000000"));


        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.WRAP_CONTENT,
                ViewGroup.LayoutParams.WRAP_CONTENT,
                6f
        );
        lp.setMargins(0, 0, 0, 5);
        // 1 user
        if (messType == 1) {
            textView.setBackgroundResource(R.drawable.messagebg1);
            lp.gravity = Gravity.RIGHT;
        }
        //  2 friend
        else {
            textView.setBackgroundResource(R.drawable.messagebg2);
            lp.gravity = Gravity.LEFT;
        }

        textView.setPadding(12, 4, 12, 4);

        textView.setLayoutParams(lp);
        layout.addView(textView);
        scrollView.post(new Runnable() {
            @Override
            public void run() {
                if (scrollUp)
                    scrollView.fullScroll(View.FOCUS_UP);
                else
                    scrollView.fullScroll(View.FOCUS_DOWN);
            }
        });
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        getMenuInflater().inflate(R.menu.menu_chat, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        int id = item.getItemId();
        if (id == R.id.menu_deleteConservation) {
            new AlertDialog.Builder(this)
                    .setTitle(friendFullName)
                    .setMessage("Are you sure to delete this chat?")
                    .setPositiveButton("Delete", (dialog, which) -> {
                        db.deleteChat(user.Email, friendEmail);
                        layout.removeAllViews();
                    })
                    .setNegativeButton(android.R.string.no, null)
                    .show();
            return true;
        }
        if (id == R.id.menu_deleteContact) {
            new AlertDialog.Builder(this)
                    .setTitle(friendFullName)
                    .setMessage("Are you sure to delete this contact?")
                    .setPositiveButton("Delete", (dialog, which) -> {
                        DatabaseReference ref = database.getReferenceFromUrl(StaticInfo.EndPoint + "/friends/" + Tools.encodeString(user.Email) + "/" + Tools.encodeString(friendEmail));
                        ref.removeValue();
                        // delete from local database
                        db.deleteFriendByEmailFromLocalDB(friendEmail);
                        finish();
                    })
                    .setNegativeButton(android.R.string.no, null)
                    .show();
            return true;
        }

        if (id == R.id.menu_friendProfile) {
            Intent intent = new Intent(ChatActivity.this, ChatFriendProfileActivity.class);
            intent.putExtra("Email", friendEmail);
            startActivityForResult(intent, StaticInfo.ChatAciviityRequestCode);
        }
        return true;
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {

        if (requestCode == StaticInfo.ChatAciviityRequestCode && resultCode == Activity.RESULT_OK) {
            User updatedFriend = db.getFriendByEmailFromLocalDB(friendEmail);
            friendFullName = updatedFriend.FirstName;
            getSupportActionBar().setTitle(updatedFriend.FirstName);
        }

        super.onActivityResult(requestCode, resultCode, data);
    }

    @Override
    protected void onResume() {
        super.onResume();
        LocalUserService.appResumed();
    }
}
