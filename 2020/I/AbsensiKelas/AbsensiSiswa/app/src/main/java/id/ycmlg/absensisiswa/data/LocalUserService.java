package id.ycmlg.absensisiswa.data;

import android.app.ActivityManager;
import android.content.Context;
import android.content.SharedPreferences;

import id.ycmlg.absensisiswa.main.chat.chatmodels.User;
import id.ycmlg.absensisiswa.main.chat.chatservices.AppService;

public class LocalUserService {
    public static User getLocalUserFromPreferences(Context context){
        SharedPreferences pref = context.getSharedPreferences("LocalUser", 0);
        User user = new User();
        user.id = pref.getString("id","null");
        user.uid = pref.getString("uid","null");
        user.Email = pref.getString("Email","null");
        user.FirstName = pref.getString("FirstName","null");
        user.LastName = pref.getString("LastName","null");
        return user;
    }

    public static boolean deleteLocalUserFromPreferences(Context context){
        try {
            SharedPreferences pref = context.getSharedPreferences("LocalUser",0);
            SharedPreferences.Editor editor = pref.edit();
            editor.clear();
            editor.apply();
            return true;
        } catch (Exception e) {
            e.printStackTrace();
            return true;
        }
    }

    public static boolean isAppServiceRunning(Context context){
        ActivityManager manager = (ActivityManager) context.getSystemService(Context.ACTIVITY_SERVICE);
        for (ActivityManager.RunningServiceInfo aService : manager.getRunningServices(Integer.MAX_VALUE)) {
            if (AppService.class.getName().equals(aService.service.getClassName())) {
                return true;
            }
        }
        return false;
    }

    public static boolean isAppVisible() {
        return appVisible;
    }

    public static void appResumed() {
        appVisible = true;
    }

    public static void appPaused() {
        appVisible = false;
    }

    private static boolean appVisible;


}
