package id.ycmlg.absensisiswa.main.chat.chatservices;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.Service;
import android.content.Intent;
import android.graphics.BitmapFactory;
import android.media.RingtoneManager;
import android.net.Uri;
import android.os.Build;
import android.os.IBinder;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.core.app.NotificationCompat;

import com.google.firebase.database.ChildEventListener;
import com.google.firebase.database.DataSnapshot;
import com.google.firebase.database.DatabaseError;
import com.google.firebase.database.DatabaseReference;
import com.google.firebase.database.FirebaseDatabase;

import java.util.Map;

import id.ycmlg.absensisiswa.R;
import id.ycmlg.absensisiswa.data.LocalUserService;
import id.ycmlg.absensisiswa.main.chat.ChatActivity;
import id.ycmlg.absensisiswa.main.chat.ChatNotificationActivity;
import id.ycmlg.absensisiswa.main.chat.chatmodels.StaticInfo;
import id.ycmlg.absensisiswa.main.chat.chatmodels.User;

public class AppService extends Service {
    public AppService() {}

    @Override
    public IBinder onBind(Intent intent) {
        throw new UnsupportedOperationException("Not yet implemented");
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        FirebaseDatabase database = FirebaseDatabase.getInstance();
        User user = LocalUserService.getLocalUserFromPreferences(getApplicationContext());
        DatabaseReference reference = database.getReferenceFromUrl(StaticInfo.NotificationEndPoint + "/" + Tools.encodeString(user.Email));
        reference.addChildEventListener(
                new ChildEventListener() {
                    @Override
                    public void onChildAdded(DataSnapshot dataSnapshot, String s) {
                        if (LocalUserService.getLocalUserFromPreferences(getApplicationContext()).Email != null) {
                            Map map = (Map)dataSnapshot.getValue();
                            String mess = map.get("Message").toString();
                            String senderEmail = map.get("SenderEmail").toString();
                            String senderFullName = Tools.toProperName(map.get("FirstName").toString()) + " " + Tools.toProperName(
                                    map.get("LastName").toString());
                            int notificationType = 1; // Message
                            notificationType = map.get("NotificationType") == null ? 1 : Integer.parseInt(map.get("NotificationType").toString());
                            // check if user is on chat activity with senderEmail
                            if (!StaticInfo.UserCurrentChatFriendEmail.equals(senderEmail)) {
                                notifyUser(senderEmail, senderFullName, mess, notificationType);
                                // remove notification
                                reference.child(dataSnapshot.getKey()).removeValue();
                            } else {
                                reference.child(dataSnapshot.getKey()).removeValue();
                            }
                        }
                    }

                    @Override public void onChildChanged(DataSnapshot dataSnapshot, String s) { }
                    @Override public void onChildRemoved(DataSnapshot dataSnapshot) { }
                    @Override public void onChildMoved(DataSnapshot dataSnapshot, String s) { }
                    @Override public void onCancelled(@NonNull DatabaseError error) { }
                }
        );
        return START_STICKY;
    }

    @Override
    public void onDestroy() {
        super.onDestroy();
        // check if user is login
        if (LocalUserService.getLocalUserFromPreferences(getApplicationContext()).Email != null) {
            sendBroadcast(new Intent("id.ycmlg.absensisiswa.main.chat.restartservice"));
        }


    }

    @Override
    public void onTaskRemoved(Intent rootIntent) {
        Intent restartServiceIntent = new Intent(getApplicationContext(), this.getClass());
        restartServiceIntent.setPackage(getPackageName());
        try {
            if(LocalUserService.isAppVisible()) startService(new Intent(this, AppService.class));
        } catch (Exception e) {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                //startForegroundService(new Intent(this, AppService.class));
            }
            e.printStackTrace();
        }
        //Toast.makeText(this, "Running service ...", Toast.LENGTH_SHORT).show();
        super.onTaskRemoved(rootIntent);
    }

    private void notifyUser(String friendEmail, String senderFullName, String mess, int notificationType) {
        int uniqueID = Tools.createUniqueIdPerUser(friendEmail);
        Uri defaultSoundUri= RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION);
        Intent i;
        NotificationCompat.Builder not = new NotificationCompat.Builder(getApplicationContext(), String.valueOf(uniqueID));
        not.setAutoCancel(true);
        not.setSmallIcon(R.mipmap.ic_launcher_round);
        not.setTicker("New Message");
        not.setContentText(mess);
        not.setLargeIcon(BitmapFactory.decodeResource(getResources(), R.mipmap.ic_launcher_round));

        // 1) Message 3) Contact Request Accepted
        if (notificationType == 1 || notificationType == 3) {
            i = new Intent(getApplicationContext(), ChatActivity.class);
            DataContext db = new DataContext(getApplicationContext(), null, null, 1);
            User frnd = db.getFriendByEmailFromLocalDB(friendEmail);
            if (frnd.FirstName != null) {
                not.setContentTitle(frnd.FirstName + " " + frnd.LastName);
                i.putExtra("FriendFullName", frnd.FirstName + " " + frnd.LastName);
            } else {
                not.setContentTitle(senderFullName);
                i.putExtra("FriendFullName", senderFullName);
            }
        }
        // Contact Request
        else if (notificationType == 2) {
            i = new Intent(getApplicationContext(), ChatNotificationActivity.class);
            not.setContentTitle(senderFullName);
        } else {
            i = null;
        }
        i.putExtra("FriendEmail", friendEmail);
        PendingIntent pendingIntent = PendingIntent.getActivity(getApplicationContext(), uniqueID, i, PendingIntent.FLAG_UPDATE_CURRENT);
        not.setContentIntent(pendingIntent);
        NotificationManager nm = (NotificationManager) getSystemService(NOTIFICATION_SERVICE);
        not.setDefaults(Notification.DEFAULT_ALL);
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            int importance = NotificationManager.IMPORTANCE_HIGH;
            NotificationChannel mChannel = nm.getNotificationChannel(String.valueOf(uniqueID));
            if (mChannel == null) {
                mChannel = new NotificationChannel(String.valueOf(uniqueID), "Chat", importance);
                mChannel.enableVibration(true);
                mChannel.setVibrationPattern(new long[]{100, 200, 300, 400, 500, 400, 300, 200, 400});
                nm.createNotificationChannel(mChannel);
            }
            not.setSound(defaultSoundUri);
            not.setPriority(NotificationCompat.PRIORITY_DEFAULT);
        } else {
            not.setDefaults(Notification.DEFAULT_ALL);
            not.setVibrate(new long[]{100, 200, 300, 400, 500, 400, 300, 200, 400});
            not.setPriority(Notification.PRIORITY_HIGH);
        }
        nm.notify(uniqueID, not.build());
    }
}
