package id.ycmlg.absensisiswa.main.guru.history;

import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;

import id.ycmlg.absensisiswa.R;

public class TerkirimFragment extends Fragment {

    private final static String ARG_PARAM1 = "param1";
    private final static String ARG_PARAM2 = "param2";
    private String mParam1;
    private int counter;

    public TerkirimFragment(){}

    public static TerkirimFragment newInstance(String param, int counter) {
        TerkirimFragment fragment = new TerkirimFragment();
        Bundle args = new Bundle();
        args.putString(ARG_PARAM1, param);
        args.putInt(ARG_PARAM2, counter);
        fragment.setArguments(args);
        return fragment;
    }

    @Override
    public void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        if (getArguments() != null) {
            mParam1 = getArguments().getString(ARG_PARAM1);
            counter = getArguments().getInt(ARG_PARAM2);
        }
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState) {
        // Inflate the layout for this fragment
        return inflater.inflate(R.layout.fragment_terkirim, container, false);
    }

    public void onViewCreated(@NonNull View view, Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);
        view.findViewById(R.id.button_second).setOnClickListener(view1 -> {
            HistoryGuruFragment.setTabPosition(HistoryGuruFragment.PENDING_POSITION);
        });
        view.findViewById(R.id.button_second).setVisibility(View.GONE);
    }
}