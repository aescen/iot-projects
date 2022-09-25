package id.ycmlg.absensisiswa.main.chat.chatadapter;

import android.content.Context;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;

import java.util.List;

import id.ycmlg.absensisiswa.R;
import id.ycmlg.absensisiswa.main.chat.chatmodels.Message;
import id.ycmlg.absensisiswa.main.chat.chatservices.Tools;


public class AdapterLastChat extends ArrayAdapter<Message> {

    public AdapterLastChat(@NonNull Context context, List<Message> messageList) {
        super(context, R.layout.custom_lastchat_row, messageList);
    }

    @NonNull
    @Override
    public View getView(int position, @Nullable View convertView, @NonNull ViewGroup parent) {
        LayoutInflater inflater = LayoutInflater.from(getContext());
        View customView = inflater.inflate(R.layout.custom_lastchat_row, parent, false);
        Message message = getItem(position);
        TextView hiddenEmail = customView.findViewById(R.id.tv_lastChat_HiddenEmail);
        TextView tv_Name = customView.findViewById(R.id.tv_lastChat_FriendFullName);
        TextView tv_MessageDate = customView.findViewById(R.id.tv_lastChat_MessageDate);
        TextView tv_Message = customView.findViewById(R.id.tv_lastChat_Message);
        hiddenEmail.setText(String.valueOf(message.FromMail));
        tv_Name.setText(message.FriendFullName);
        String properDate = Tools.messageSentDateProper(message.SentDate);
        tv_MessageDate.setText(properDate);
        if (message.Message.length() > 20){
            message.Message = message.Message.substring(0,20);
        }
        tv_Message.setText(message.Message);
        return customView;
    }

}
