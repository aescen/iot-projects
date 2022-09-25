package id.ac.polinema.pstt.voicechat;

import android.util.Log;

import org.json.JSONException;
import org.json.JSONObject;

public class Message {
    private String from;
    private String fromIp;
    private String text;
    private boolean toThisUser;
    private long time;
    private Integer status;
    private JSONObject json;
    private Message message;

    public Message(String from, String fromIp, String text, boolean toThisUser, long time) {
        this.from = from;
        this.fromIp = fromIp;
        this.text = text;
        this.toThisUser = toThisUser;
        this.time = time;
        this.json = new JSONObject();
        try {
            json.put("from", from);
            json.put("fromIp", fromIp);
            json.put("text", text);
            json.put("dst", String.valueOf(toThisUser));
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
    public String getText() {
        return text;
    }
    public boolean toThisUser() {
        return toThisUser;
    }
    public long getTime(){ return time; }
    public String getJson() { return json.toString(); }
}
