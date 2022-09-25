package id.ac.polinema.pstt.voicechat;

import android.util.Log;

import org.json.JSONException;
import org.json.JSONObject;

public class User {
    private String from;
    private String fromIp;
    private long time;
    private JSONObject json;

    public User(String from, String fromIp, long time) {
        this.from = from;
        this.fromIp = fromIp;
        this.time = time;
        this.json = new JSONObject();
        try {
            json.put("from", from);
            json.put("fromIp", fromIp);
            json.put("time", String.valueOf(time));
        } catch (JSONException e) {
            //Log.e("JSONEx:","Error creating message json");
        }
    }

    public String getFrom() {
        return from;
    }
    public String getFromIp() {
        return fromIp;
    }
    public long getTime(){ return time; }
    public String getJson() { return json.toString(); }
}
