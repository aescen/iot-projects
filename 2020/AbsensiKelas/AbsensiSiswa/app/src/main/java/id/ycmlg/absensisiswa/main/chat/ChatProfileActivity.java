package id.ycmlg.absensisiswa.main.chat;

import android.content.Intent;
import android.os.Build;
import android.os.Bundle;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import id.ycmlg.absensisiswa.R;
import id.ycmlg.absensisiswa.main.chat.chatmodels.User;
import id.ycmlg.absensisiswa.main.chat.chatservices.AppService;
import id.ycmlg.absensisiswa.main.chat.chatservices.DataContext;
import id.ycmlg.absensisiswa.data.LocalUserService;
import id.ycmlg.absensisiswa.main.chat.chatservices.Tools;

public class ChatProfileActivity extends AppCompatActivity {
    DataContext db = new DataContext(this, null, null, 1);
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_chat_profile);
        User user = LocalUserService.getLocalUserFromPreferences(this);
        TextView tv_UserFullName = findViewById(R.id.tv_UserFullName);
        tv_UserFullName.setText(Tools.toProperName(user.FirstName) + " " + Tools.toProperName(user.LastName));
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