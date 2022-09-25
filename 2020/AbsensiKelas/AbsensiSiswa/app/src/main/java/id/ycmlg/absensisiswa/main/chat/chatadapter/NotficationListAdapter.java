package id.ycmlg.absensisiswa.main.chat.chatadapter;


import android.app.Activity;
import android.graphics.Color;
import android.view.Gravity;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.ImageButton;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.appcompat.app.AlertDialog;

import com.google.firebase.database.DatabaseReference;
import com.google.firebase.database.FirebaseDatabase;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import id.ycmlg.absensisiswa.R;
import id.ycmlg.absensisiswa.main.chat.chatmodels.NotificationModel;
import id.ycmlg.absensisiswa.main.chat.chatmodels.StaticInfo;
import id.ycmlg.absensisiswa.main.chat.chatmodels.User;
import id.ycmlg.absensisiswa.data.LocalUserService;
import id.ycmlg.absensisiswa.main.chat.chatservices.Tools;

public class NotficationListAdapter extends ArrayAdapter<NotificationModel> {

    private final Activity activity;
    private ImageButton acceptBtn;
    private ImageButton rejectBtn;
    private final FirebaseDatabase database = FirebaseDatabase.getInstance();


    public NotficationListAdapter(@NonNull Activity activity, List<NotificationModel> list) {
        super(activity, R.layout.custom_notication_row, list);
        this.activity = activity;

    }

    @NonNull
    @Override
    public View getView(int position, @Nullable View convertView, @NonNull ViewGroup parent) {

        LayoutInflater inflater = LayoutInflater.from(getContext());
        View customView = inflater.inflate(R.layout.custom_notication_row, parent, false);
        NotificationModel model = getItem(position);
        // get layout
        LinearLayout layout = customView.findViewById(R.id.layout_CustomNotificationRow);

        // make components according to model and append to layout

        TextView tv_NotficationMessage = customView.findViewById(R.id.tv_NotificationMessage);
        tv_NotficationMessage.setText(model.NotificationMessage);

        // friend request
        if (model.NotificationType == 1) {
            // make button and append
//            acceptBtn = new Button(getContext());
//            rejectBtn = new Button(getContext());

            acceptBtn = new ImageButton(getContext());
            rejectBtn = new ImageButton(getContext());

            acceptBtn.setBackgroundColor(Color.TRANSPARENT);
            rejectBtn.setBackgroundColor(Color.TRANSPARENT);

            acceptBtn.setImageResource(R.drawable.emoji_2705);
            rejectBtn.setImageResource(R.drawable.emoji_274c);

            setCustomOnClick(acceptBtn, model.EmailFrom, model.FirstName, model.LastName);
            onRejectClick(rejectBtn, position, model.FirstName + " " + model.LastName);
            // set layout params
            LinearLayout.LayoutParams layoutParams = new LinearLayout.LayoutParams(
                    ViewGroup.LayoutParams.WRAP_CONTENT,
                    ViewGroup.LayoutParams.WRAP_CONTENT
            );
            layoutParams.gravity = Gravity.CENTER;

            acceptBtn.setLayoutParams(layoutParams);
            rejectBtn.setLayoutParams(layoutParams);
            acceptBtn.setPadding(4, 4, 4, 4);
            rejectBtn.setPadding(4, 4, 4, 4);
            layout.addView(acceptBtn);
            layout.addView(rejectBtn);
        }
        return customView;
    }


    private void setCustomOnClick(final ImageButton btn, final String friendEmail, final String friendFirstName, final String friendLastName) {

        btn.setOnClickListener(v -> {
                    User user = LocalUserService.getLocalUserFromPreferences(activity);
                    // add to friends and remove from requests
                    DatabaseReference fireBase = database.getReferenceFromUrl(StaticInfo.FriendsURL);
                    // set each other friends

                    Map<String, String> map1 = new HashMap<>();
                    map1.put("Email", friendEmail);
                    map1.put("FirstName", friendFirstName);
                    map1.put("LastName", friendLastName);
                    fireBase.child(Tools.encodeString(user.Email)).child(Tools.encodeString(friendEmail)).setValue(map1);

                    Map<String, String> map2 = new HashMap<>();
                    map2.put("Email", user.Email);
                    map2.put("FirstName", user.FirstName);
                    map2.put("LastName", user.LastName);
                    fireBase.child(Tools.encodeString(friendEmail)).child(Tools.encodeString(user.Email)).setValue(map2);

                    DatabaseReference frRequ = database.getReferenceFromUrl(StaticInfo.EndPoint + "/friendrequests");
                    frRequ.child(Tools.encodeString(user.Email)).child(Tools.encodeString(friendEmail)).removeValue();
                    acceptBtn.setEnabled(false);

                    Toast.makeText(activity, "Accepted", Toast.LENGTH_SHORT).show();
                    rejectBtn.setEnabled(false);

                    Map<String, String> notMap = new HashMap<String, String>();
                    notMap.put("SenderEmail", user.Email);
                    notMap.put("FirstName", user.FirstName);
                    notMap.put("LastName", user.LastName);
                    notMap.put("Message", "Contact request accepted start chating... ");
                    // accepted contact reques
                    notMap.put("NotificationType", "3");
                    DatabaseReference notRef = database.getReferenceFromUrl(StaticInfo.NotificationEndPoint + "/" + Tools.encodeString(friendEmail));
                    notRef.push().setValue(notMap);
                }
        );


    }

    private void onRejectClick(final ImageButton btn, final int modelPosition, final String friendFullName) {
        btn.setOnClickListener(v -> new AlertDialog.Builder(activity)
                .setTitle(friendFullName)
                .setMessage("Are you sure to reject this contact request?")
                .setPositiveButton("Reject", (dialog, which) -> {
                    User user = LocalUserService.getLocalUserFromPreferences(activity);
                    DatabaseReference fireBase = database.getReferenceFromUrl(StaticInfo.FriendRequestsEndPoint + "/" + Tools.encodeString(user.Email) + "/" + getItem(modelPosition).FriendRequestFireBaseKey);
                    fireBase.removeValue();
                    rejectBtn.setEnabled(false);
                    acceptBtn.setEnabled(false);
                    Toast.makeText(activity, "Rejected", Toast.LENGTH_SHORT).show();
                })
                .setNegativeButton(android.R.string.no, null)
                .show());

    }
}
