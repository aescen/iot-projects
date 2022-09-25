package id.ycmlg.absensisiswa.main.guru.home.menukelas.nfcread;

import android.os.Bundle;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;

import androidx.annotation.NonNull;
import androidx.fragment.app.Fragment;

import com.google.firebase.database.DataSnapshot;
import com.google.firebase.database.DatabaseError;
import com.google.firebase.database.DatabaseReference;
import com.google.firebase.database.FirebaseDatabase;
import com.google.firebase.database.ValueEventListener;

import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Date;
import java.util.List;

import id.ycmlg.absensisiswa.databinding.FragmentHistoryNfcBinding;

/**
 * A simple {@link Fragment} subclass.
 * Use the {@link HistoryNFCFragment#newInstance} factory method to
 * create an instance of this fragment.
 */
public class HistoryNFCFragment extends Fragment {

    // TODO: Rename parameter arguments, choose names that match
    // the fragment initialization parameters, e.g. ARG_ITEM_NUMBER
    private static final String ARG_PARAM1 = "namaKelas";
    private static final String ARG_PARAM2 = "tglPath";
    private static final String ARG_PARAM3 = "idCard";
    private static final String ARG_PARAM4 = "nis";
    private static final String ARG_PARAM5 = "nama";

    // TODO: Rename and change types of parameters
    private String namaKelas;
    private String tglPath;
    private String idCard;
    private String nis;
    private String nama;

    public HistoryNFCFragment() {
        // Required empty public constructor
    }

    /**
     * Use this factory method to create a new instance of
     * this fragment using the provided parameters.
     *
     * @param namaKelas Parameter 1.
     * @param tglPath Parameter 2.
     * @param idCard Parameter 3.
     * @param nis Parameter 4.
     * @param nama Parameter 5.
     * @return A new instance of fragment HistoryNFCFragment.
     */
    // TODO: Rename and change types and number of parameters
    public static HistoryNFCFragment newInstance(String namaKelas, String tglPath, String idCard, String nis, String nama) {
        HistoryNFCFragment fragment = new HistoryNFCFragment();
        Bundle args = new Bundle();
        args.putString(ARG_PARAM1, namaKelas);
        args.putString(ARG_PARAM2, tglPath);
        args.putString(ARG_PARAM3, idCard);
        args.putString(ARG_PARAM4, nis);
        args.putString(ARG_PARAM5, nama);
        fragment.setArguments(args);
        return fragment;
    }

    public static HistoryNFCFragment newInstance(String namaKelas) {
        HistoryNFCFragment fragment = new HistoryNFCFragment();
        Bundle args = new Bundle();
        args.putString(ARG_PARAM1, namaKelas);
        fragment.setArguments(args);
        return fragment;
    }

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        if (getArguments() != null) {
            namaKelas = getArguments().getString(ARG_PARAM1,null);
            tglPath = getArguments().getString(ARG_PARAM2,null);
            idCard = getArguments().getString(ARG_PARAM3,null);
            nis = getArguments().getString(ARG_PARAM4,null);
            nama = getArguments().getString(ARG_PARAM5,null);
            database = FirebaseDatabase.getInstance();
            kelasRef = database.getReference("abs").child(namaKelas.toLowerCase().replaceAll("\\s+",""));
        }
    }

    @Override
    public void onDestroyView() {
        super.onDestroyView();
        historyNfcBinding = null;
    }

    private FirebaseDatabase database;
    private DatabaseReference kelasRef;
    private View root;
    private FragmentHistoryNfcBinding historyNfcBinding;
    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        // Inflate the layout for this fragment
        //root = inflater.inflate(R.layout.fragment_history_nfc, container, false);

        //using view binding
        historyNfcBinding = FragmentHistoryNfcBinding.inflate(inflater, container, false);
        root = historyNfcBinding.getRoot();

        if(idCard != null && nama != null && nis != null) {
            historyNfcBinding.tvIdCard.setText(idCard);
            historyNfcBinding.tvNfcReadNamaLengkap.setText(nama);
            historyNfcBinding.tvNoInduk.setText(nis);
        } else{
            if(kelasRef != null){
                kelasRef.addListenerForSingleValueEvent(new ValueEventListener() {
                    @Override
                    public void onDataChange(@NonNull DataSnapshot snapshot) {
                        List<Date> dateList = new ArrayList<>();
                        for (DataSnapshot childTgl : snapshot.getChildren()) {
                            final String tgl = childTgl.getKey();
                            int yyyy = Integer.parseInt(tgl.substring(6, tgl.length()));
                            int mm = Integer.parseInt(tgl.substring(3, 5));
                            int dd = Integer.parseInt(tgl.substring(0, 2));
                            dateList.add(new Date(yyyy-1900, mm-1, dd));
                        }
                        Collections.sort(dateList);
                        SimpleDateFormat formatter = new SimpleDateFormat("dd-MM-yyyy");
                        Date date = new Date();
                        date.setTime(dateList.get(dateList.size() - 1).getTime());
                        final String lastTgl = formatter.format(date);
                        final int lastItem = (int) snapshot.child(lastTgl).getChildrenCount() - 1;
                        //Log.i("HNFC", "lastTgl: " + lastTgl + "lastItem:" + lastItem);
                        idCard = snapshot.child(lastTgl)
                                .child(String.valueOf(lastItem))
                                .child("idcard").getValue().toString();
                        nama = snapshot.child(lastTgl)
                                .child(String.valueOf(lastItem))
                                .child("nm").getValue().toString();
                        nis = snapshot.child(lastTgl)
                                .child(String.valueOf(lastItem))
                                .child("nis").getValue().toString();
                        historyNfcBinding.tvIdCard.setText(idCard);
                        historyNfcBinding.tvNfcReadNamaLengkap.setText(nama);
                        historyNfcBinding.tvNoInduk.setText(nis);
                    }

                    @Override
                    public void onCancelled(@NonNull DatabaseError error) {

                    }
                });
            }

        }

        return root;
    }
}