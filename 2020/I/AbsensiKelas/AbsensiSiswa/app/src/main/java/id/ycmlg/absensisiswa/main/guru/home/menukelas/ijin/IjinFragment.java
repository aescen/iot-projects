package id.ycmlg.absensisiswa.main.guru.home.menukelas.ijin;

import android.os.Bundle;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.fragment.app.Fragment;

import com.google.firebase.database.DataSnapshot;
import com.google.firebase.database.DatabaseError;
import com.google.firebase.database.DatabaseReference;
import com.google.firebase.database.FirebaseDatabase;
import com.google.firebase.database.ValueEventListener;

import java.util.Calendar;

import id.ycmlg.absensisiswa.R;
import id.ycmlg.absensisiswa.data.Absen;
import id.ycmlg.absensisiswa.data.SNTPClient;

/**
 * A simple {@link Fragment} subclass.
 * Use the {@link IjinFragment#newInstance} factory method to
 * create an instance of this fragment.
 */
public class IjinFragment extends Fragment {

    // TODO: Rename parameter arguments, choose names that match
    // the fragment initialization parameters, e.g. ARG_ITEM_NUMBER
    private static final String ARG_PARAM1 = "namaKelas";
    private static final String ARG_PARAM2 = "nis";
    private static final String ARG_PARAM3 = "namaLengkap";

    // TODO: Rename and change types of parameters
    private String namaKelas;
    private String nis;
    private String namaLengkap;
    private String idCard;

    public IjinFragment() {
        // Required empty public constructor
    }

    /**
     * Use this factory method to create a new instance of
     * this fragment using the provided parameters.
     *
     * @param namaKelas Parameter 1.
     * @param nis Parameter 2.
     * @param namaLengkap Parameter 2.
     * @return A new instance of fragment IjinFragment.
     */
    // TODO: Rename and change types and number of parameters
    public static IjinFragment newInstance(String namaKelas, String nis, String namaLengkap) {
        IjinFragment fragment = new IjinFragment();
        Bundle args = new Bundle();
        args.putString(ARG_PARAM1, namaKelas);
        args.putString(ARG_PARAM2, nis);
        args.putString(ARG_PARAM3, namaLengkap);
        fragment.setArguments(args);
        return fragment;
    }

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        if (getArguments() != null) {
            namaKelas = getArguments().getString(ARG_PARAM1);
            nis = getArguments().getString(ARG_PARAM2);
            namaLengkap = getArguments().getString(ARG_PARAM3);
            database = FirebaseDatabase.getInstance();
            absRef = database.getReference("abs").child(namaKelas.toLowerCase().replaceAll("\\s+",""));
            nfcRef = database.getReference("nfc");
        }
    }

    private View root;
    private FirebaseDatabase database = null;
    private DatabaseReference absRef = null;
    private DatabaseReference nfcRef = null;
    private Button bt_ket_sakit = null;
    private Button bt_ket_ijin = null;
    private Button bt_ket_tanpa_ket = null;
    private TextView tv_no_induk_ijin = null;
    private TextView tv_nama_lengkap_ijin = null;
    private LinearLayout pb_ll_ijin = null;
    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        // Inflate the layout for this fragment
        root = inflater.inflate(R.layout.fragment_ijin, container, false);
        tv_no_induk_ijin = root.findViewById(R.id.tv_no_induk_ijin);
        tv_nama_lengkap_ijin = root.findViewById(R.id.tv_nama_lengkap_ijin);
        bt_ket_sakit = root.findViewById(R.id.bt_ket_sakit);
        bt_ket_ijin = root.findViewById(R.id.bt_ket_ijin);
        bt_ket_tanpa_ket = root.findViewById(R.id.bt_ket_tanpa_ket);
        pb_ll_ijin = root.findViewById(R.id.pb_ll_ijin);

        tv_no_induk_ijin.setText(nis);
        tv_nama_lengkap_ijin.setText(namaLengkap);

        bt_ket_sakit.setOnClickListener(view -> setIjin("s"));
        bt_ket_ijin.setOnClickListener(view -> setIjin("i"));
        bt_ket_tanpa_ket.setOnClickListener(view -> setIjin("a"));

        return root;
    }

    private void setIjin(final String KET){
        pb_ll_ijin.setVisibility(View.VISIBLE);
        absRef.addListenerForSingleValueEvent(new ValueEventListener() {
            @Override
            public void onDataChange(@NonNull DataSnapshot absSnapshot) {
                SNTPClient sntpClient = null;
                sntpClient.getDate(Calendar.getInstance().getTimeZone(), new SNTPClient.Listener() {
                    @Override
                    public void onTimeReceived(String rawDate) {
                        final String tgl = rawDate.substring(0, rawDate.indexOf("T"));
                        final String wkt = rawDate.substring(rawDate.indexOf("T") + 1, rawDate.indexOf("+"));

                        nfcRef.addListenerForSingleValueEvent(new ValueEventListener() {
                            @Override
                            public void onDataChange(@NonNull DataSnapshot ncfSnapshot) {
                                for (DataSnapshot idChild: ncfSnapshot.getChildren()) {
                                    final String nNis = idChild.getKey();
                                    if(nNis != null){
                                        if(nNis.contentEquals(nis)){
                                            idCard = idChild.child("idcard").getValue().toString();
                                            break;
                                        }
                                    }
                                }
                                Absen newAbs = new Absen();
                                newAbs.idcard = idCard;
                                newAbs.ket = KET;
                                newAbs.nis = nis;
                                newAbs.nm = namaLengkap;
                                newAbs.tgl = tgl;
                                newAbs.wkt = wkt;
                                if (absSnapshot.child(tgl).getValue() != null){
                                    long arrTotal = absSnapshot.child(tgl).getChildrenCount();
                                    absRef.child(tgl).child(String.valueOf(arrTotal)).setValue(newAbs);
                                } else {
                                    absRef.child(tgl).child(String.valueOf(0)).setValue(newAbs);
                                }
                                final String toastStr
                                        = KET.contentEquals("s") ? "Absensi sakit tersimpan."
                                        : KET.contentEquals("i") ? "Absensi ijin tersimpan."
                                        : "Absensi tanpa\nketerangan tersimpan.";
                                Toast.makeText(requireActivity(), toastStr, Toast.LENGTH_SHORT).show();
                                pb_ll_ijin.setVisibility(View.GONE);
                                requireActivity().onBackPressed();
                            }

                            @Override
                            public void onCancelled(@NonNull DatabaseError error) {
                                //Log.i("I-NCF", "Cancelled.");
                                Toast.makeText(requireActivity(), "Penyimpanan gagal!", Toast.LENGTH_SHORT).show();
                                pb_ll_ijin.setVisibility(View.GONE);
                                requireActivity().onBackPressed();
                            }
                        });

                    }

                    @Override
                    public void onError(Exception ex) {
                        //Log.i("I-SNTP", "Error:" + ex.getCause());
                        Toast.makeText(requireActivity(), "Penyimpanan gagal!", Toast.LENGTH_SHORT).show();
                        pb_ll_ijin.setVisibility(View.GONE);
                        requireActivity().onBackPressed();
                    }
                });
            }

            @Override
            public void onCancelled(@NonNull DatabaseError error) {
                //Log.i("I-ABS", "Cancelled.");
                Toast.makeText(requireActivity(), "Penyimpanan gagal!", Toast.LENGTH_SHORT).show();
                pb_ll_ijin.setVisibility(View.GONE);
                requireActivity().onBackPressed();
            }
        });
    }


}