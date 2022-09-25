package id.ac.polinema.pstt.voicechat;

import android.annotation.SuppressLint;
import android.app.Activity;
import android.content.Context;
import android.support.annotation.NonNull;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.BaseAdapter;
import android.widget.TextView;

import java.util.ArrayList;
import java.util.List;

import static id.ac.polinema.pstt.voicechat.MainActivity.dH;

public class MsgsAdapter extends BaseAdapter {
    private List<Message> messages = new ArrayList<Message>();
    private static Boolean userList;
    private static boolean toName = false;
    private static Boolean toTheRight = null;
    private Context context;

    public MsgsAdapter(@NonNull Context ctx, boolean uL) {
        context = ctx;
        userList = uL;
    }

    public void clear() {
        messages.clear();
        notifyDataSetChanged();
    }

    public void add(Message m) {
        if(!messages.contains(m)){
            messages.add(m);
            if(!dH.getUsers().containsKey(m.getFrom())){
                dH.putUser(m.getFrom(), m.getFrom());
            }
            notifyDataSetChanged();
        }
    }

    @Override
    public int getCount() {
        return messages.size();
    }

    @Override
    public Object getItem(int i) {
        return messages.get(i);
    }

    @Override
    public long getItemId(int i) {
        return i;
    }

    @SuppressLint("SetTextI18n")
    @Override
    public View getView(int i, View convertView, ViewGroup viewGroup) {
        UserViewHolder holderUsers = new UserViewHolder();
        MessageViewHolder holderMessages = new MessageViewHolder();
        LayoutInflater messageInflater = (LayoutInflater) this.context.getApplicationContext().getSystemService(Activity.LAYOUT_INFLATER_SERVICE);
        Message message = messages.get(i);
        if (userList){
            convertView = messageInflater.inflate(R.layout.messages_list, viewGroup, false);
            holderUsers.name = (TextView) convertView.findViewById(R.id.listtext1);
            holderUsers.address = (TextView) convertView.findViewById(R.id.listtext2);
            convertView.setTag(holderUsers);
            holderUsers.name.setText(message.getFrom());
            holderUsers.address.setText(message.getFromIp());
        } else {
            if (!message.toThisUser()) {//my message
                //Log.i("getView:", "Outgoing, set to the right");
                convertView = messageInflater.inflate(R.layout.my_message, viewGroup, false);
                holderMessages.name = (TextView) convertView.findViewById(R.id.mm_name);
                holderMessages.messageBody = (TextView) convertView.findViewById(R.id.mm_message_body);
                convertView.setTag(holderMessages);
                holderMessages.name.setVisibility(View.VISIBLE);
                holderMessages.name.setText(message.getFrom() + "@" + message.getFromIp());
//                //set to right
//                if(toTheRight == null ){//null or new
//                    toTheRight = true;//set to the right
//                    toName = true;//toName
//                    //Log.i("getView:", "Outgoing, no message yet, set toName");
//                }
//                if(toTheRight && toName) {//from null, name it
//                    holderMessages.name.setVisibility(View.VISIBLE);
//                    holderMessages.name.setText(message.getFrom() + "@" + message.getFromIp());
//                    toName = false;//just named, set to false
//                    //Log.i("getView:", "Just named");
//                } else if(toTheRight && !toName) {//already named
//                    holderMessages.name.setVisibility(View.GONE);
//                    //Log.i("getView:", "Already named");
//                } else if(!toTheRight){//from left, name it
//                    holderMessages.name.setVisibility(View.VISIBLE);
//                    holderMessages.name.setText(message.getFrom() + "@" + message.getFromIp());
//                    toTheRight = true;//set to the right
//                    toName = false;//just named, set to false
//                    //Log.i("getView:", "Just named");
//                }
                holderMessages.messageBody.setText(message.getText());
            } else {//other message
                //Log.i("getView:", "Incoming, set to the left");
                convertView = messageInflater.inflate(R.layout.other_message, viewGroup, false);
                holderMessages.name = (TextView) convertView.findViewById(R.id.om_name);
                holderMessages.messageBody = (TextView) convertView.findViewById(R.id.om_message_body);
                convertView.setTag(holderMessages);
                holderMessages.name.setVisibility(View.VISIBLE);
                holderMessages.name.setText(message.getFrom() + "@" + message.getFromIp());
//                if(toTheRight == null) {//null or new
//                    toTheRight = false;//set to the left
//                    toName = true;
//                    //Log.i("getView:", "Incoming, no message yet, set toName");
//                }
//                if(!toTheRight && toName) {//from null, name it
//                    holderMessages.name.setVisibility(View.VISIBLE);
//                    holderMessages.name.setText(message.getFrom() + "@" + message.getFromIp());
//                    toName = false;
//                    //Log.i("getView:", "Incoming, not to the left, set toName");
//                } else if(!toTheRight && !toName){//already named
//                    holderMessages.name.setVisibility(View.GONE);
//                    //Log.i("getView:", "Already named");
//                } else if(toTheRight){//from left, name it
//                    holderMessages.name.setVisibility(View.VISIBLE);
//                    holderMessages.name.setText(message.getFrom() + "@" + message.getFromIp());
//                    toTheRight = false;//set to the left
//                    toName = false;//just named, set to false
//                    //Log.i("getView:", "Just named");
//                }
                holderMessages.messageBody.setText(message.getText());
            }
        }
        //Log.i("getView:", message.getJson() + "userlist:" + userList + "cV:" + convertView);
        return convertView;
    }
}

class MessageViewHolder {
    public TextView name;
    public TextView messageBody;
}

class UserViewHolder {
    public TextView name;
    public TextView address;
}