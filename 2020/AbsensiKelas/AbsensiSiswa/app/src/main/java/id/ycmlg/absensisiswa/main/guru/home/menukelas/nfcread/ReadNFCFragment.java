package id.ycmlg.absensisiswa.main.guru.home.menukelas.nfcread;

import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import android.graphics.Color;
import android.graphics.drawable.ColorDrawable;
import android.nfc.NdefMessage;
import android.nfc.NdefRecord;
import android.nfc.NfcAdapter;
import android.nfc.Tag;
import android.nfc.tech.MifareClassic;
import android.nfc.tech.MifareUltralight;
import android.os.Bundle;
import android.os.Parcelable;
import android.util.Log;
import android.view.Gravity;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.PopupWindow;
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
import java.util.List;

import id.ycmlg.absensisiswa.R;
import id.ycmlg.absensisiswa.data.Absen;
import id.ycmlg.absensisiswa.data.SNTPClient;
import id.ycmlg.absensisiswa.nfc.parser.NdefMessageParser;
import id.ycmlg.absensisiswa.nfc.record.ParsedNdefRecord;

import static android.provider.Settings.ACTION_NFC_SETTINGS;
import static id.ycmlg.absensisiswa.nfc.utils.Utils.toDec;
import static id.ycmlg.absensisiswa.nfc.utils.Utils.toHex;
import static id.ycmlg.absensisiswa.nfc.utils.Utils.toReversedDec;
import static id.ycmlg.absensisiswa.nfc.utils.Utils.toReversedHex;

/**
 * A simple {@link Fragment} subclass.
 * Use the {@link ReadNFCFragment#newInstance} factory method to
 * create an instance of this fragment.
 */
public class ReadNFCFragment extends Fragment {

    // TODO: Rename parameter arguments, choose names that match
    // the fragment initialization parameters, e.g. ARG_ITEM_NUMBER
    private static final String ARG_PARAM1 = "namaKelas";
    private static final String ARG_PARAM2 = "param2";

    // TODO: Rename and change types of parameters
    private String namaKelas;
    private String mParam2;

    public ReadNFCFragment() {
        // Required empty public constructor
    }

    /**
     * Use this factory method to create a new instance of
     * this fragment using the provided parameters.
     *
     * @param namaKelas Parameter 1.
     * @param param2 Parameter 2.
     * @return A new instance of fragment ReadNFCFragment.
     */
    // TODO: Rename and change types and number of parameters
    public static ReadNFCFragment newInstance(String namaKelas, String param2) {
        ReadNFCFragment fragment = new ReadNFCFragment();
        Bundle args = new Bundle();
        args.putString(ARG_PARAM1, namaKelas);
        args.putString(ARG_PARAM2, param2);
        fragment.setArguments(args);
        return fragment;
    }

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        if (getArguments() != null) {
            namaKelas = getArguments().getString(ARG_PARAM1);
            mParam2 = getArguments().getString(ARG_PARAM2);
            database = FirebaseDatabase.getInstance();
            absRef = database.getReference("abs").child(namaKelas.toLowerCase().replaceAll("\\s+",""));
            nfcRef = database.getReference("nfc");
        }
        nfcAdapter = NfcAdapter.getDefaultAdapter(requireContext());
        if (nfcAdapter == null){
            Toast.makeText(requireContext(), "No NFC!", Toast.LENGTH_SHORT).show();
            requireActivity().finish();
        }
    }

    private View root = null;
    private LayoutInflater inflaterPopUp;
    private Button bt_scan_nfc = null;
    private Button bt_history_nfc = null;
    private Button bt_scan_nfc_result = null;
    private FirebaseDatabase database;
    private DatabaseReference absRef;
    private DatabaseReference nfcRef;
    private NfcAdapter nfcAdapter = null;
    private PendingIntent pendingIntent = null;
    private TextView tv_nfc_read_result;
    private PopupWindow popupWindowToScan;
    private PopupWindow popupWindowResult;
    private View viewToScan;
    private View viewResult;
    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        // Inflate the layout for this fragment
        root = inflater.inflate(R.layout.fragment_read_nfc, container, false);
        bt_scan_nfc = root.findViewById(R.id.bt_scan_nfc);
        bt_history_nfc = root.findViewById(R.id.bt_history_nfc);

        bt_scan_nfc.setOnClickListener(view -> scanNFC());

        bt_history_nfc.setOnClickListener(view -> {
            Fragment fragment = HistoryNFCFragment.newInstance(namaKelas);
            requireActivity().getSupportFragmentManager().
                    beginTransaction()
                    .replace(R.id.nav_kelas_host_fragment, fragment)
                    .addToBackStack(null)
                    .commit();
        });

        pendingIntent  = PendingIntent.getActivity(requireContext(),
                0 ,
                new Intent(requireContext(),
                        requireContext().getClass()).addFlags(Intent.FLAG_ACTIVITY_SINGLE_TOP),
                0);

        return root;
    }

    private void scanNFC() {
        inflaterPopUp = (LayoutInflater) requireContext().getSystemService(Context.LAYOUT_INFLATER_SERVICE);
        viewToScan = inflaterPopUp.inflate(R.layout.nfc_read_ready_to_scan, null);
        popupWindowToScan = new PopupWindow(viewToScan, ViewGroup.LayoutParams.WRAP_CONTENT,
                ViewGroup.LayoutParams.WRAP_CONTENT, true); // Creation of popup
        popupWindowToScan.setBackgroundDrawable(new ColorDrawable(Color.TRANSPARENT));
        popupWindowToScan.setOutsideTouchable(true);
        popupWindowToScan.showAtLocation(viewToScan, Gravity.BOTTOM, 0, 0); // Displaying popup
        bt_scan_nfc = viewToScan.findViewById(R.id.bt_scan_nfc_cancel);

        viewResult = inflaterPopUp.inflate(R.layout.nfc_read_result, null);
        popupWindowResult = new PopupWindow(viewResult, ViewGroup.LayoutParams.WRAP_CONTENT,
                ViewGroup.LayoutParams.WRAP_CONTENT, true); // Creation of popup
        popupWindowResult.setBackgroundDrawable(new ColorDrawable(Color.TRANSPARENT));
        popupWindowResult.setOutsideTouchable(true);
        popupWindowResult.showAtLocation(viewResult, Gravity.BOTTOM, 0, 0); // Displaying popup
        viewResult.setVisibility(View.GONE);
        bt_scan_nfc_result = viewResult.findViewById(R.id.bt_scan_nfc_result);
        tv_nfc_read_result = viewResult.findViewById(R.id.tv_nfc_read_result);

        bt_scan_nfc.setOnClickListener(view -> {
            if (popupWindowToScan.isShowing()) {
                viewToScan.setVisibility(View.GONE);
                popupWindowToScan.dismiss();
            }
        });
    }

    @Override
    public void onResume() {
        super.onResume();
        if (nfcAdapter != null) {
            if (!nfcAdapter.isEnabled()) {
                showNFCSettings();
            }
            nfcAdapter.enableForegroundDispatch(requireActivity(), pendingIntent, null, null);
            resolveIntent(requireActivity().getIntent());
        }
    }

    private void showNFCSettings(){
        Toast.makeText(requireContext(), "You need to enable NFC!", Toast.LENGTH_SHORT).show();
        Intent intent = new Intent(ACTION_NFC_SETTINGS);
        startActivity(intent);
    }

    private void resolveIntent(Intent intent) {
        String action = intent.getAction();
        if (NfcAdapter.ACTION_TAG_DISCOVERED.equals(action)
                || NfcAdapter.ACTION_TECH_DISCOVERED.equals(action)
                || NfcAdapter.ACTION_NDEF_DISCOVERED.equals(action)) {
            Parcelable[] rawMsgs = intent.getParcelableArrayExtra(NfcAdapter.EXTRA_NDEF_MESSAGES);
            NdefMessage[] msgs;

            if (rawMsgs != null) {
                msgs = new NdefMessage[rawMsgs.length];
                for (int i = 0; i < rawMsgs.length; i++) {
                    msgs[i] = (NdefMessage) rawMsgs[i];
                }
            } else {
                byte[] empty = new byte[0];
                byte[] id = intent.getByteArrayExtra(NfcAdapter.EXTRA_ID);
                Tag tag = intent.getParcelableExtra(NfcAdapter.EXTRA_TAG);
                final String hexr = toReversedHex(tag.getId()).toUpperCase().replace("\\s+", "").trim();
                if(tv_nfc_read_result != null) {
                    //tv_nfc_read_result.setText(hexr);
                    popupWindowToScan.dismiss();
                    viewToScan.setVisibility(View.GONE);
                    viewResult.setVisibility(View.VISIBLE);
                    if(nfcRef != null && absRef != null){
                        final String finalHexr = hexr.toUpperCase().replaceAll("\\s+","").trim();
                        nfcRef.addListenerForSingleValueEvent(new ValueEventListener() {
                            @Override
                            public void onDataChange(@NonNull DataSnapshot snapshot) {
                                if (snapshot != null){
                                    for (DataSnapshot nfcCard : snapshot.getChildren()){
                                        final String nfcCardUserId = nfcCard.getKey();
                                        final String nfcCardId = nfcCard.child("idcard").getValue().toString().toUpperCase().replaceAll("\\s+","").trim();
                                        final String nfcCardName = nfcCard.child("nama").getValue().toString();
                                        if(nfcCardId.contentEquals(finalHexr)){
                                            //Log.i("RNFC-CARD", snapshot.toString() + ":" + nfcCardId + "=" + finalHexr);
                                            SNTPClient sntpClient = null;
                                            sntpClient.getDate(Calendar.getInstance().getTimeZone(), new SNTPClient.Listener() {
                                                @Override
                                                public void onTimeReceived(String rawDate) {
                                                    final String tgl = rawDate.substring(0, rawDate.indexOf("T"));
                                                    final String wkt = rawDate.substring(rawDate.indexOf("T") + 1, rawDate.indexOf("+"));
                                                    //final String fullDate = tgl + "T" + wkt + ":" + rawDate.substring(rawDate.indexOf("+") + 1, rawDate.length());
                                                    //Log.i("RNFC-CARD", "rawDate: " + rawDate + ";date:" + tgl + ";time:" + wkt + ";fullDate:" + fullDate);

                                                    absRef.child(tgl).addListenerForSingleValueEvent(new ValueEventListener() {
                                                        @Override
                                                        public void onDataChange(@NonNull DataSnapshot snapshot) {
                                                            boolean absPresent = false;
                                                            for (DataSnapshot absChild: snapshot.getChildren()) {
                                                                if(absChild.child("idcard").getValue().toString().contentEquals(nfcCardId)){
                                                                   absPresent = true;
                                                                }
                                                            }
                                                            if(!absPresent){
                                                                Absen abs = new Absen();
                                                                abs.ket = "m";
                                                                abs.nis = nfcCardUserId;
                                                                abs.nm = nfcCardName;
                                                                abs.idcard = nfcCardId;
                                                                abs.tgl = tgl;
                                                                abs.wkt = wkt;

                                                                absRef.child(tgl).addListenerForSingleValueEvent(new ValueEventListener() {
                                                                    @Override
                                                                    public void onDataChange(@NonNull DataSnapshot snapshot) {
                                                                        bt_scan_nfc_result.setOnClickListener(view -> {
                                                                            Fragment fragment = HistoryNFCFragment.newInstance(namaKelas, tgl, nfcCardId, nfcCardUserId, nfcCardName);
                                                                            requireActivity().getSupportFragmentManager().
                                                                                    beginTransaction()
                                                                                    .replace(R.id.nav_kelas_host_fragment, fragment)
                                                                                    .addToBackStack(null)
                                                                                    .commit();
                                                                            if (popupWindowResult.isShowing()) popupWindowResult.dismiss();
                                                                        });
                                                                        if (snapshot.getValue() != null){
                                                                            long arrTotal = snapshot.getChildrenCount();
                                                                            absRef.child(tgl).child(String.valueOf(arrTotal)).setValue(abs);
                                                                        } else {
                                                                            absRef.child(tgl).child(String.valueOf(0)).setValue(abs);
                                                                        }
                                                                    }

                                                                    @Override
                                                                    public void onCancelled(@NonNull DatabaseError error) {
                                                                    }
                                                                });
                                                            } else {
                                                                Toast.makeText(requireContext(), "Siswa '"
                                                                        + nfcCardName
                                                                        + "' sudah absen hari ini!", Toast.LENGTH_LONG).show();
                                                                if (popupWindowResult.isShowing()) popupWindowResult.dismiss();
                                                            }
                                                        }

                                                        @Override
                                                        public void onCancelled(@NonNull DatabaseError error) {

                                                        }
                                                    });
                                                }

                                                @Override
                                                public void onError(Exception ex) {

                                                }
                                            });
                                        }
                                    }
                                } else {
                                    //Log.i("NCFR-DATA", "No data for " + namaKelas);
                                    //pb_ll_absensi.setVisibility(View.GONE);
                                }
                            }

                            @Override
                            public void onCancelled(@NonNull DatabaseError error) {

                            }
                        });
                    }
                } else {
                    //Log.i("RNFC", "hexr: " + hexr);
                }

                byte[] payload = dumpTagData(tag).getBytes();
                NdefRecord record = new NdefRecord(NdefRecord.TNF_UNKNOWN, empty, id, payload);
                NdefMessage msg = new NdefMessage(new NdefRecord[]{record});
                msgs = new NdefMessage[] {msg};
            }

            //displayNfcMsgs(msgs);
        }
    }

    private void displayNfcMsgs(NdefMessage[] msgs) {
        if (msgs == null || msgs.length == 0)
            return;

        StringBuilder builder = new StringBuilder();
        List<ParsedNdefRecord> records = NdefMessageParser.parse(msgs[0]);
        final int size = records.size();

        for (int i = 0; i < size; i++) {
            ParsedNdefRecord record = records.get(i);
            String str = record.str();
            builder.append(str).append("\n");
        }

        if(tv_nfc_read_result != null) {
            tv_nfc_read_result.setText(builder.toString());
            popupWindowToScan.dismiss();
            viewToScan.setVisibility(View.GONE);
            viewResult.setVisibility(View.VISIBLE);
        } else {
            //Log.i(TAG, "displayNfcMsgs: " + builder.toString());
        }
    }

    private String dumpTagData(Tag tag) {
        StringBuilder sb = new StringBuilder();
        byte[] id = tag.getId();
        /*Log.i("CARD DETECT", "resolveIntent: card detected" +
                ", hex:" + toHex(id).toUpperCase() +
                ", hexr:" + toReversedHex(id).toUpperCase() +
                ", dec:" + toDec(id) +
                ", decr:" + toReversedDec(id));*/
        sb.append("ID (hex): ").append(toHex(id).toUpperCase()).append('\n');
        sb.append("ID (reversed hex): ").append(toReversedHex(id).toUpperCase()).append('\n');
        sb.append("ID (dec): ").append(toDec(id)).append('\n');
        sb.append("ID (reversed dec): ").append(toReversedDec(id)).append('\n');

        String prefix = "android.nfc.tech.";
        sb.append("Technologies: ");
        for (String tech : tag.getTechList()) {
            sb.append(tech.substring(prefix.length()));
            sb.append(", ");
        }

        sb.delete(sb.length() - 2, sb.length());

        for (String tech : tag.getTechList()) {
            if (tech.equals(MifareClassic.class.getName())) {
                sb.append('\n');
                String type = "Unknown";

                try {
                    MifareClassic mifareTag = MifareClassic.get(tag);

                    switch (mifareTag.getType()) {
                        case MifareClassic.TYPE_CLASSIC:
                            type = "Classic";
                            break;
                        case MifareClassic.TYPE_PLUS:
                            type = "Plus";
                            break;
                        case MifareClassic.TYPE_PRO:
                            type = "Pro";
                            break;
                    }
                    sb.append("Mifare Classic type: ");
                    sb.append(type);
                    sb.append('\n');

                    sb.append("Mifare size: ");
                    sb.append(mifareTag.getSize()).append(" bytes");
                    sb.append('\n');

                    sb.append("Mifare sectors: ");
                    sb.append(mifareTag.getSectorCount());
                    sb.append('\n');

                    sb.append("Mifare blocks: ");
                    sb.append(mifareTag.getBlockCount());
                } catch (Exception e) {
                    sb.append("Mifare classic error: ").append(e.getMessage());
                }
            }

            if (tech.equals(MifareUltralight.class.getName())) {
                sb.append('\n');
                MifareUltralight mifareUlTag = MifareUltralight.get(tag);
                String type = "Unknown";
                switch (mifareUlTag.getType()) {
                    case MifareUltralight.TYPE_ULTRALIGHT:
                        type = "Ultralight";
                        break;
                    case MifareUltralight.TYPE_ULTRALIGHT_C:
                        type = "Ultralight C";
                        break;
                }
                sb.append("Mifare Ultralight type: ");
                sb.append(type);
            }
        }

        return sb.toString();
    }
}