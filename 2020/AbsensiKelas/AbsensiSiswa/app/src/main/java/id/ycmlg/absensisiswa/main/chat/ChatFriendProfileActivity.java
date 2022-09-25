package id.ycmlg.absensisiswa.main.chat;

import android.app.Activity;
import android.app.ProgressDialog;
import android.content.Intent;
import android.os.AsyncTask;
import android.os.Build;
import android.os.Bundle;
import android.text.InputType;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ImageButton;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AlertDialog;
import androidx.appcompat.app.AppCompatActivity;

import com.google.firebase.database.DataSnapshot;
import com.google.firebase.database.DatabaseError;
import com.google.firebase.database.DatabaseReference;
import com.google.firebase.database.FirebaseDatabase;
import com.google.firebase.database.ValueEventListener;

import java.util.HashMap;
import java.util.Map;

import id.ycmlg.absensisiswa.R;
import id.ycmlg.absensisiswa.main.chat.chatmodels.StaticInfo;
import id.ycmlg.absensisiswa.main.chat.chatmodels.User;
import id.ycmlg.absensisiswa.main.chat.chatservices.AppService;
import id.ycmlg.absensisiswa.main.chat.chatservices.DataContext;
import id.ycmlg.absensisiswa.data.LocalUserService;
import id.ycmlg.absensisiswa.main.chat.chatservices.Tools;

public class ChatFriendProfileActivity extends AppCompatActivity {
    String friendEmail;
    TextView tv_FriendFullName;
    User user, f;
    ProgressDialog pd;
    Button btn_AddFriend;
    private static FirebaseDatabase database;
    private DataContext db;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_chat_friend_profile);
        getSupportActionBar().setTitle("Friend Profile");
        btn_AddFriend = findViewById(R.id.btn_AddFriend);
        pd = new ProgressDialog(this);

        pd.setMessage("Loading...");
        f = new User();
        Bundle extras = getIntent().getExtras();
        friendEmail = extras.getString("Email");
        tv_FriendFullName = findViewById(R.id.tv_FriendFullName_L_FriendProfile);

        user = LocalUserService.getLocalUserFromPreferences(getApplicationContext());
        database = FirebaseDatabase.getInstance();
        db = new DataContext(this, null, null, 1);

        // check if already friends otherwise get info from server
        User friend = db.getFriendByEmailFromLocalDB(friendEmail);
        if (friend.Email == null) {
            ImageButton btn_EditName = findViewById(R.id.btn_EditName);
            btn_EditName.setVisibility(View.INVISIBLE);
            FindFriendsTask t = new FindFriendsTask();
            t.execute();
        } else {
            tv_FriendFullName.setText(Tools.toProperName(friend.FirstName) + " " + Tools.toProperName(friend.LastName));
            btn_AddFriend.setEnabled(false);
            btn_AddFriend.setText("Connected");
        }

    }

    @Override
    protected void onStart() {
        super.onStart();
        if (!LocalUserService.isAppServiceRunning(this)) {
            try {
                if(LocalUserService.isAppVisible()) startService(new Intent(this, AppService.class));
            } catch (Exception e) {
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                    //startForegroundService(new Intent(this, AppService.class));
                }
                e.printStackTrace();
            }
            //Toast.makeText(this, "Running service ...", Toast.LENGTH_SHORT).show();
        }
    }

    public class FindFriendsTask extends AsyncTask<Void, Void, String> {
        @Override protected void onPreExecute() {
            pd.show();
        }

        @Override
        protected String doInBackground(Void... params) {

            //User user = LocalUserService.getLocalUserFromPreferences(getApplicationContext());
            //List<User> friendList = new ArrayList<>();
            DatabaseReference usersRef = database.getReferenceFromUrl(StaticInfo.UsersURL + "/");
            usersRef.addListenerForSingleValueEvent(new ValueEventListener() {
                @Override
                public void onDataChange(@NonNull DataSnapshot snapshot) {
                    for (DataSnapshot aUser : snapshot.getChildren()) {
                        String serEmail = Tools.decodeString(aUser.child("Email").getValue(String.class));
                        if(serEmail.contentEquals(friendEmail)){
                            f.Email = serEmail;
                            f.FirstName = aUser.child("FirstName").getValue(String.class);
                            f.LastName = aUser.child("LastName").getValue(String.class);
                            tv_FriendFullName.setText(Tools.toProperName(f.FirstName) + " " + Tools.toProperName(f.LastName));
                            pd.hide();
                            break;
                        }
                    }
                }

                @Override
                public void onCancelled(@NonNull DatabaseError error) {
                    pd.hide();
                }
            });


            return null;
        }

        @Override protected void onPostExecute(String jsonListString) {}
    }

    public void btn_SendFriendRequestClick(View view) {
        FirebaseDatabase database = FirebaseDatabase.getInstance();
        DatabaseReference friendReqRef = database.getReferenceFromUrl(StaticInfo.FriendRequestsEndPoint);
        DatabaseReference notifRef = database.getReferenceFromUrl(StaticInfo.NotificationEndPoint + "/" + Tools.encodeString(friendEmail));
        Map<String, String> map = new HashMap<>();
        map.put("FirstName", user.FirstName);
        map.put("LastName", user.LastName);
        friendReqRef.child(Tools.encodeString(f.Email)).child(Tools.encodeString(user.Email)).setValue(map);
        btn_AddFriend.setEnabled(false);
        btn_AddFriend.setText("Request Sent");

        map.put("SenderEmail", user.Email);
        map.put("Message", "Pending contact request");
        map.put("NotificationType", "2");

        notifRef.push().setValue(map);

    }

    public void btn_EditNameClick(View view) {

        AlertDialog.Builder builder = new AlertDialog.Builder(this);
        builder.setTitle("Set display name");
        final EditText et = new EditText(this);
        et.setText(tv_FriendFullName.getText());
        et.setInputType(InputType.TYPE_TEXT_FLAG_CAP_SENTENCES);
        builder.setView(et);
        builder.setPositiveButton("Save", (dialog, which) -> {
            String newName = et.getText().toString();
            db.setPreferedDisplayName(friendEmail, newName);
            tv_FriendFullName.setText(newName);
            setResult(Activity.RESULT_OK);
        });
        builder.setNegativeButton("Cancel", (dialog, which) -> dialog.cancel());
        builder.show();

    }

    @Override
    protected void onResume() {
        super.onResume();
        LocalUserService.appResumed();
    }

    @Override
    protected void onPause() {
        super.onPause();
        LocalUserService.appPaused();
    }
}