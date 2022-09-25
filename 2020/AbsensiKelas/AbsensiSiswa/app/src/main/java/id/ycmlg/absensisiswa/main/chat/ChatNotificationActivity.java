package id.ycmlg.absensisiswa.main.chat;

import android.content.Intent;
import android.os.Build;
import android.os.Bundle;
import android.widget.ListAdapter;
import android.widget.ListView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;

import com.google.firebase.database.ChildEventListener;
import com.google.firebase.database.DataSnapshot;
import com.google.firebase.database.DatabaseError;
import com.google.firebase.database.DatabaseReference;
import com.google.firebase.database.FirebaseDatabase;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import id.ycmlg.absensisiswa.R;
import id.ycmlg.absensisiswa.main.chat.chatadapter.NotficationListAdapter;
import id.ycmlg.absensisiswa.main.chat.chatmodels.NotificationModel;
import id.ycmlg.absensisiswa.main.chat.chatmodels.StaticInfo;
import id.ycmlg.absensisiswa.main.chat.chatmodels.User;
import id.ycmlg.absensisiswa.main.chat.chatservices.AppService;
import id.ycmlg.absensisiswa.data.LocalUserService;
import id.ycmlg.absensisiswa.main.chat.chatservices.Tools;

public class ChatNotificationActivity extends AppCompatActivity {
    ListView lv_NotificationList;
    User user;
    List<NotificationModel> notificationList;
    FirebaseDatabase database;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_chat_notification);
        getSupportActionBar().setTitle("Notifications");
        database = FirebaseDatabase.getInstance();
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

        lv_NotificationList = findViewById(R.id.lv_NoticicationList);
        notificationList = new ArrayList<>();
        user = LocalUserService.getLocalUserFromPreferences(this);
        DatabaseReference reqRef = database.getReferenceFromUrl(StaticInfo.EndPoint + "/friendrequests/" + Tools.encodeString(user.Email));
        reqRef.addChildEventListener(
                new ChildEventListener() {
                    @Override
                    public void onChildAdded(DataSnapshot dataSnapshot, String s) {
                        Map map = (Map)dataSnapshot.getValue();
                        String firstName = map.get("FirstName").toString();
                        String lastName = map.get("LastName").toString();
                        final String key = dataSnapshot.getKey();
                        NotificationModel not = new NotificationModel();
                        not.FirstName = firstName;
                        not.LastName = lastName;
                        not.NotificationType = 1; // friend request
                        notificationList.add(not);
                        not.EmailFrom = Tools.decodeString(key);
                        not.FriendRequestFireBaseKey = dataSnapshot.getKey();
                        not.NotificationMessage = Tools.toProperName(firstName) + " " + Tools.toProperName(lastName);
                        ListAdapter adp = new NotficationListAdapter(ChatNotificationActivity.this, notificationList);
                        lv_NotificationList.setAdapter(adp);
                    }

                    @Override
                    public void onChildChanged(DataSnapshot dataSnapshot, String s) {

                    }

                    @Override
                    public void onChildRemoved(DataSnapshot dataSnapshot) {
                        String friendEmail = Tools.decodeString(dataSnapshot.getKey());
                        int index = -1;
                        for (int i = 0; i < notificationList.size(); i++) {
                            NotificationModel item = notificationList.get(i);
                            if (item.EmailFrom.equals(friendEmail))
                                index = i;
                        }
                        notificationList.remove(index);
                        ListAdapter adp = new NotficationListAdapter(ChatNotificationActivity.this, notificationList);
                        lv_NotificationList.setAdapter(adp);

                    }

                    @Override public void onChildMoved(DataSnapshot dataSnapshot, String s) { }
                    @Override public void onCancelled(@NonNull DatabaseError error) { }
                }
        );
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
