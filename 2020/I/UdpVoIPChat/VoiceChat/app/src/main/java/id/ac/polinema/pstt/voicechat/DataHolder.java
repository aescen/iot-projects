package id.ac.polinema.pstt.voicechat;

import android.util.Log;

import org.json.JSONException;
import org.json.JSONObject;

import java.net.InetAddress;
import java.util.HashMap;
import java.util.TreeMap;

public class DataHolder {
    private static HashMap<String, InetAddress> sContacts = new HashMap<String, InetAddress>();
    private static HashMap<String, String> sUsers = new HashMap<>();
    private static HashMap<String, String> sMessages = new HashMap<String, String>();
    private static Boolean sLISTEN_MSG;
    private static Boolean sLISTEN_WIFI;
    private static String sDisplayName;
    private static InetAddress sLocalIp;
    private static InetAddress sBcIp;
    private static boolean sContactsDataChange = true;
    private static boolean sMessagesDataChange = true;
    private static boolean sUsersDataChange = true;

    //Other methods
    void setContactsDataChange(Boolean dataChange) {
        sContactsDataChange = dataChange;
    }

    Boolean getContactDataChange() {
        return sContactsDataChange;
    }

    void setMessagesDataChange(Boolean dataChange) {
        sMessagesDataChange = dataChange;
    }

    Boolean getMessagesDataChange() {
        return sMessagesDataChange;
    }

    void setUsersDataChange(Boolean dataChange) {
        sUsersDataChange = dataChange;
    }

    Boolean getUsersDataChange() {
        return sUsersDataChange;
    }

    HashMap<String, InetAddress> getContacts() { return sContacts; }

    void setContacts(HashMap<String, InetAddress> contacts) {
        sContacts = contacts;
        sContactsDataChange = true;
    }

    void putContact(String hash, InetAddress value) {
        sContacts.put(hash, value);
        sContactsDataChange = true;
    }

    void removeContact(String hash) {
        sContacts.remove(hash);
        sContactsDataChange = true;
    }

    void clearContact() {
        sContacts.clear();
        sContactsDataChange = true;
    }

    HashMap<String, String> getMessages() {
        return sMessages;
    }

    void setMessages(HashMap<String, String> messages) {
        sMessages = messages;
        sMessagesDataChange = true;
    }

    void putMessage(String hash, String value) {
        sMessages.put(hash, value);
        sMessagesDataChange = true;
    }

    void removeMessage(String hash) {
        sMessages.remove(hash);
        sMessagesDataChange = true;
    }

    void clearMessage() {
        sMessages.clear();
        sMessagesDataChange = true;
    }

    String getLatestMessage(){
        TreeMap<Long, String> bucket = new TreeMap<>();
        if(!sMessages.isEmpty()){
            for (HashMap.Entry<String, String> entry : sMessages.entrySet()) {
                try {
                    JSONObject val = new JSONObject(entry.getValue());
                    if( !bucket.containsKey(val.getLong("time")) ){
                        bucket.put(val.getLong("time"), entry.getValue());
                    }
                } catch (JSONException e) {
                    //Log.e("getLatestMessage():","Error parsing json");
                }
            }
        }else return "";
        return bucket.lastEntry().getValue();
    }

    HashMap<String, String> getUsers() {
        return sUsers;
    }

    void setUser(HashMap<String, String> user) {
        sUsers = user;
        sUsersDataChange = true;
    }

    void putUser(String hash, String value) {
        sUsers.put(hash, value);
        sUsersDataChange = true;
    }

    void removeUser(String hash) {
        sUsers.remove(hash);
        sUsersDataChange = true;
    }

    void clearUser() {
        sUsers.clear();
        sUsersDataChange = true;
    }

    void clearAll() {
        sContacts.clear();
        sMessages.clear();
        sUsers.clear();
        sContactsDataChange = true;
        sMessagesDataChange = true;
        sUsersDataChange = true;
    }

    Boolean getListenMsg() {
        if (sLISTEN_MSG == null){
            sLISTEN_MSG = false;
        }
        return sLISTEN_MSG;
    }

    void setListenMsg(Boolean LISTEN_MSG) { sLISTEN_MSG = LISTEN_MSG; }

    String getDisplayName() {
        if (sDisplayName == null){
            sDisplayName = "Who";
        }
        return sDisplayName;
    }

    void setDisplayName(String displayName) {
        sDisplayName = displayName;
    }

    Boolean getListenWiFi() {
        if (sLISTEN_WIFI == null){
            sLISTEN_WIFI = false;
        }
        return sLISTEN_WIFI;
    }

    void setListenWiFi(Boolean LISTEN_WIFI) {
        sLISTEN_WIFI = LISTEN_WIFI;
    }

    InetAddress getLocalIp() {
        return sLocalIp;
    }

    void setLocalIp(InetAddress localIp) {
        sLocalIp = localIp;
    }

    InetAddress getBcIp() {
        return sBcIp;
    }

    void setBcIp(InetAddress bcIp) {
        sBcIp = bcIp;
    }

    //Singleton pattern
    private static DataHolder instance = null;

    private DataHolder(){}

    synchronized static DataHolder getInstance() {
        if(instance == null) {
            instance = new DataHolder();
        }
        return instance;
    }
}
