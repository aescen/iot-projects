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
import id.ycmlg.absensisiswa.main.chat.chatmodels.User;
import id.ycmlg.absensisiswa.main.chat.chatservices.Tools;

public class FriendListAdapter extends ArrayAdapter<User> {


    public FriendListAdapter(@NonNull Context context, List<User> contactList) {
        super(context, R.layout.custom_friend_list_row, contactList);
    }

    @NonNull
    @Override
    public View getView(int position, @Nullable View convertView, @NonNull ViewGroup parent) {
        LayoutInflater inflater = LayoutInflater.from(getContext());
        View customView = inflater.inflate(R.layout.custom_friend_list_row, parent, false);
        User user = getItem(position);
        TextView hiddenEmail = customView.findViewById(R.id.tv_HiddenEmail);
        TextView tv_Name = customView.findViewById(R.id.tv_FriendFullName);
        hiddenEmail.setText(String.valueOf(user.Email));
        tv_Name.setText(Tools.toProperName(user.FirstName) + " " + Tools.toProperName(user.LastName));
        return customView;
    }

}
