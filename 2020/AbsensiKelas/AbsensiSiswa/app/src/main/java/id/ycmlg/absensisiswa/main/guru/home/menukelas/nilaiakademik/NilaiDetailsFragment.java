package id.ycmlg.absensisiswa.main.guru.home.menukelas.nilaiakademik;

import android.content.Context;
import android.graphics.Color;
import android.os.Bundle;
import android.view.Gravity;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageButton;
import android.widget.LinearLayout;
import android.widget.TableLayout;
import android.widget.TableRow;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.fragment.app.Fragment;

import com.google.firebase.database.DataSnapshot;
import com.google.firebase.database.DatabaseError;
import com.google.firebase.database.DatabaseReference;
import com.google.firebase.database.FirebaseDatabase;
import com.google.firebase.database.ValueEventListener;

import java.util.ArrayList;
import java.util.List;

import id.ycmlg.absensisiswa.R;
import id.ycmlg.absensisiswa.data.DaftarSiswaNilaiEditData;

/**
 * A simple {@link Fragment} subclass.
 * Use the {@link NilaiDetailsFragment#newInstance} factory method to
 * create an instance of this fragment.
 */
public class NilaiDetailsFragment extends Fragment {

    // TODO: Rename parameter arguments, choose names that match
    // the fragment initialization parameters, e.g. ARG_ITEM_NUMBER
    private static final String ARG_PARAM1 = "subjectPath";
    private static final String ARG_PARAM2 = "mapel";
    private static final String ARG_PARAM3 = "mapelPath";
    private static final String ARG_PARAM4 = "namaKelas";

    // TODO: Rename and change types of parameters
    private String subject;
    private String mapel;
    private String mapelPath;
    private String namaKelas;
    private String nSubjectPath;

    public NilaiDetailsFragment() {
        // Required empty public constructor
    }

    /**
     * Use this factory method to create a new instance of
     * this fragment using the provided parameters.
     *
     * @param subjectPath Parameter 1.
     * @param mapel Parameter 2.
     * @param mapelPath Parameter 3.
     * @param namaKelas Parameter 4.
     * @return A new instance of fragment NilaiDetailsFragment.
     */
    // TODO: Rename and change types and number of parameters
    public static NilaiDetailsFragment newInstance(String subjectPath, String mapel, String mapelPath, String namaKelas) {
        NilaiDetailsFragment fragment = new NilaiDetailsFragment();
        Bundle args = new Bundle();
        args.putString(ARG_PARAM1, subjectPath);
        args.putString(ARG_PARAM2, mapel);
        args.putString(ARG_PARAM3, mapelPath);
        args.putString(ARG_PARAM4, namaKelas);
        fragment.setArguments(args);
        return fragment;
    }

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        if (getArguments() != null) {
            nSubjectPath = getArguments().getString(ARG_PARAM1, null);
            mapel = getArguments().getString(ARG_PARAM2, null);
            mapelPath = getArguments().getString(ARG_PARAM3, null);
            namaKelas = getArguments().getString(ARG_PARAM4, null);
            subjectPath = nSubjectPath.substring(0, nSubjectPath.indexOf("&"));
            subject = nSubjectPath.substring(nSubjectPath.indexOf("&") + 1);
            //Log.i("NE-ARG", subjectPath + ":" + mapel + ":" + mapelPath + ":" + subject);
            subject = subject.substring(subject.indexOf("_") + 1);
            //Log.i("NE-ARG2", subjectPath + ":" + mapel + ":" + mapelPath + ":" + subject);
            database = FirebaseDatabase.getInstance();
            subjectRef = database.getReference("nilaiakademik").child(mapelPath)
                    .child(namaKelas.replaceAll("\\s+","")
                            .trim()
                            .toLowerCase())
                    .child(subjectPath);
        }
    }

    private View root;
    private TextView tv_title_mata_pelajaran_edit;
    private String subjectPath;
    private FirebaseDatabase database;
    private DatabaseReference subjectRef;
    private List<DaftarSiswaNilaiEditData> daftarSiswaNilaiEditData;
    private LinearLayout pb_ll_nilai_edit;
    private TableLayout tl_daftar_siswa_nilai_edit;
    private TextView tv_subjek_nilai_edit;
    private ImageButton iv_bt_edit_mata_pelajaran_edit;
    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        // Inflate the layout for this fragment
        root = inflater.inflate(R.layout.fragment_nilai_details, container, false);
        tv_title_mata_pelajaran_edit = root.findViewById(R.id.tv_title_mata_pelajaran_edit);
        tv_subjek_nilai_edit = root.findViewById(R.id.tv_subjek_nilai_edit);
        iv_bt_edit_mata_pelajaran_edit = root.findViewById(R.id.iv_bt_edit_mata_pelajaran_edit);
        pb_ll_nilai_edit = root.findViewById(R.id.pb_ll_nilai_edit);
        tl_daftar_siswa_nilai_edit = root.findViewById(R.id.tl_daftar_siswa_nilai_edit);
        if(mapel != null) tv_title_mata_pelajaran_edit.setText(mapel);
        tv_subjek_nilai_edit.setText((subject != null) ? subject : "");
        AppCompatActivity activity = (AppCompatActivity) requireActivity();
        activity.getSupportActionBar().setDisplayHomeAsUpEnabled(true);
        activity.getSupportActionBar().setDisplayShowHomeEnabled(true);


        if (getArguments() != null) {
            if(subjectRef != null) {
                subjectRef.addListenerForSingleValueEvent(new ValueEventListener() {
                    @Override
                    public void onDataChange(@NonNull DataSnapshot snapshot) {
                        daftarSiswaNilaiEditData = new ArrayList<>();
                        int i = 0;
                        for (DataSnapshot childArr : snapshot.getChildren()) {
                            DaftarSiswaNilaiEditData row = new DaftarSiswaNilaiEditData();
                            row.no = (i + 1);
                            row.created = childArr.child("created").getValue().toString();
                            row.mapel = childArr.child("mapel").getValue().toString();
                            row.jn = childArr.child("jn").getValue().toString();
                            row.klssmt = childArr.child("klssmt").getValue().toString();
                            row.n = childArr.child("n").getValue().toString();
                            row.nis = childArr.child("nis").getValue().toString();//
                            row.nm = childArr.child("nm").getValue().toString();
                            row.pmb = childArr.child("pmb").getValue().toString();
                            row.st = childArr.child("st").getValue().toString();
                            row.sub = childArr.child("sub").getValue().toString();
                            row.t = childArr.child("t").getValue().toString();
                            row.ta = childArr.child("ta").getValue().toString();
                            daftarSiswaNilaiEditData.add(row);
                            i++;
                        }
                        loadTableData();
                        pb_ll_nilai_edit.setVisibility(View.GONE);
                    }


                    @Override
                    public void onCancelled(@NonNull DatabaseError error) {
                        pb_ll_nilai_edit.setVisibility(View.GONE);
                    }
                });
            }
        } else {
        }

        iv_bt_edit_mata_pelajaran_edit.setOnClickListener(view -> {
            Fragment fragment = AddNilaiAkademikFragment.newInstance(namaKelas, mapel, mapelPath, nSubjectPath);
            requireActivity().getSupportFragmentManager().
                    beginTransaction()
                    .replace(R.id.nav_kelas_host_fragment, fragment)
                    .addToBackStack(null)
                    .commit();
        });
        
        return root;
    }

    private void loadTableData(){
        Context context = requireContext();
        int rows = daftarSiswaNilaiEditData.size();
        if (daftarSiswaNilaiEditData != null && daftarSiswaNilaiEditData.size() > 0){
            DaftarSiswaNilaiEditData row;
            final int COLUMN_COUNT = 12;
            for (int i=0;i<rows;i++){
                String textColor = "#f8f8f8";
                if(i % 2 == 0){
                    textColor = "#ffffff";
                } else {
                    textColor = "#f8f8f8";
                }
                row = daftarSiswaNilaiEditData.get(i);
                final TextView tvNo = new TextView(context);
                tvNo.setLayoutParams(new TableRow.LayoutParams(TableRow
                        .LayoutParams.WRAP_CONTENT, TableRow
                        .LayoutParams.WRAP_CONTENT));
                tvNo.setBackgroundColor(Color.parseColor(textColor));
                tvNo.setGravity(Gravity.CENTER);
                tvNo.setPadding(5, 15, 0, 15);
                tvNo.setText(String.valueOf(row.no));

                final TextView tvTgl = new TextView(context);
                tvTgl.setLayoutParams(new TableRow.LayoutParams(TableRow
                        .LayoutParams.WRAP_CONTENT, TableRow
                        .LayoutParams.MATCH_PARENT));
                tvTgl.setGravity(Gravity.CENTER);
                tvTgl.setPadding(5, 15, 0, 15);
                tvTgl.setBackgroundColor(Color.parseColor(textColor));
                tvTgl.setText(row.created);

                final TextView tvMapel = new TextView(context);
                tvMapel.setLayoutParams(new TableRow.LayoutParams(TableRow
                        .LayoutParams.WRAP_CONTENT, TableRow
                        .LayoutParams.MATCH_PARENT));
                tvMapel.setGravity(Gravity.CENTER);
                tvMapel.setPadding(5, 15, 0, 15);
                tvMapel.setBackgroundColor(Color.parseColor(textColor));
                tvMapel.setText(row.mapel);

                final TextView tvNis = new TextView(context);
                tvNis.setLayoutParams(new TableRow.LayoutParams(TableRow
                        .LayoutParams.WRAP_CONTENT, TableRow
                        .LayoutParams.MATCH_PARENT));
                tvNis.setGravity(Gravity.CENTER);
                tvNis.setPadding(5, 15, 0, 15);
                tvNis.setBackgroundColor(Color.parseColor(textColor));
                tvNis.setText(row.nis);

                final TextView tvNama = new TextView(context);
                tvNama.setLayoutParams(new TableRow.LayoutParams(TableRow
                        .LayoutParams.WRAP_CONTENT, TableRow
                        .LayoutParams.WRAP_CONTENT));
                tvNama.setGravity(Gravity.CENTER);
                tvNama.setBackgroundColor(Color.parseColor(textColor));
                tvNama.setPadding(5, 15, 0, 15);
                tvNama.setText(row.nm);

                final TextView tvTa = new TextView(context);
                tvTa.setLayoutParams(new TableRow.LayoutParams(TableRow
                        .LayoutParams.WRAP_CONTENT, TableRow
                        .LayoutParams.MATCH_PARENT));
                tvTa.setGravity(Gravity.CENTER);
                tvTa.setPadding(5, 15, 0, 15);
                tvTa.setBackgroundColor(Color.parseColor(textColor));
                tvTa.setText(row.ta);

                final TextView tvKs = new TextView(context);
                tvKs.setLayoutParams(new TableRow.LayoutParams(TableRow
                        .LayoutParams.WRAP_CONTENT, TableRow
                        .LayoutParams.WRAP_CONTENT));
                tvKs.setGravity(Gravity.CENTER);
                tvKs.setBackgroundColor(Color.parseColor(textColor));
                tvKs.setPadding(5, 15, 0, 15);
                tvKs.setText(row.klssmt);

                final TextView tvTm = new TextView(context);
                tvTm.setLayoutParams(new TableRow.LayoutParams(TableRow
                        .LayoutParams.WRAP_CONTENT, TableRow
                        .LayoutParams.MATCH_PARENT));
                tvTm.setGravity(Gravity.CENTER);
                tvTm.setPadding(5, 15, 0, 15);
                tvTm.setBackgroundColor(Color.parseColor(textColor));
                tvTm.setText(row.t);

                final TextView tvSt = new TextView(context);
                tvSt.setLayoutParams(new TableRow.LayoutParams(TableRow
                        .LayoutParams.WRAP_CONTENT, TableRow
                        .LayoutParams.WRAP_CONTENT));
                tvSt.setGravity(Gravity.CENTER);
                tvSt.setBackgroundColor(Color.parseColor(textColor));
                tvSt.setPadding(5, 15, 0, 15);
                tvSt.setText(row.st);

                final TextView tvPmb = new TextView(context);
                tvPmb.setLayoutParams(new TableRow.LayoutParams(TableRow
                        .LayoutParams.WRAP_CONTENT, TableRow
                        .LayoutParams.MATCH_PARENT));
                tvPmb.setGravity(Gravity.CENTER);
                tvPmb.setPadding(5, 15, 0, 15);
                tvPmb.setBackgroundColor(Color.parseColor(textColor));
                tvPmb.setText(row.pmb);

                final TextView tvJn = new TextView(context);
                tvJn.setLayoutParams(new TableRow.LayoutParams(TableRow
                        .LayoutParams.WRAP_CONTENT, TableRow
                        .LayoutParams.WRAP_CONTENT));
                tvJn.setGravity(Gravity.CENTER);
                tvJn.setBackgroundColor(Color.parseColor(textColor));
                tvJn.setPadding(5, 15, 0, 15);
                tvJn.setText(row.jn);

                final TextView tvNl = new TextView(context);
                tvNl.setLayoutParams(new TableRow.LayoutParams(TableRow
                        .LayoutParams.WRAP_CONTENT, TableRow
                        .LayoutParams.MATCH_PARENT));
                tvNl.setGravity(Gravity.CENTER);
                tvNl.setPadding(5, 15, 0, 15);
                tvNl.setBackgroundColor(Color.parseColor(textColor));
                tvNl.setText(row.n);

                final TableRow trNilaiEdit = new TableRow(context);
                trNilaiEdit.setId(i + 1);
                TableLayout.LayoutParams trParams = new TableLayout.LayoutParams(TableLayout
                        .LayoutParams.MATCH_PARENT, TableLayout
                        .LayoutParams.WRAP_CONTENT);
                trParams.setMargins(0, 0, 0, 0);
                trNilaiEdit.setPadding(0,0,0,0);
                trNilaiEdit.setLayoutParams(trParams);
                trNilaiEdit.addView(tvNo);
                trNilaiEdit.addView(tvTgl);
                trNilaiEdit.addView(tvMapel);
                trNilaiEdit.addView(tvNis);
                trNilaiEdit.addView(tvNama);
                trNilaiEdit.addView(tvTa);
                trNilaiEdit.addView(tvKs);
                trNilaiEdit.addView(tvTm);
                trNilaiEdit.addView(tvSt);
                trNilaiEdit.addView(tvPmb);
                trNilaiEdit.addView(tvJn);
                trNilaiEdit.addView(tvNl);

                tl_daftar_siswa_nilai_edit.addView(trNilaiEdit, trParams);
                final TableRow trSep = new TableRow(context);
                TableLayout.LayoutParams trParamsSep = new TableLayout.LayoutParams(TableLayout
                        .LayoutParams.MATCH_PARENT, TableLayout
                        .LayoutParams.WRAP_CONTENT);
                trParamsSep.setMargins(0, 0, 0, 0);
                trSep.setLayoutParams(trParamsSep);
                TextView tvSep = new TextView(requireContext());
                TableRow.LayoutParams tvSepLay = new TableRow.LayoutParams(TableRow
                        .LayoutParams.MATCH_PARENT, TableRow
                        .LayoutParams.WRAP_CONTENT);
                tvSepLay.span = COLUMN_COUNT;
                tvSep.setLayoutParams(tvSepLay);
                tvSep.setBackgroundColor(Color.parseColor("#d9d9d9"));
                tvSep.setHeight(1);
                trSep.addView(tvSep);
                tl_daftar_siswa_nilai_edit.addView(trSep, trParamsSep);
            }
            tl_daftar_siswa_nilai_edit.setVisibility(View.VISIBLE);
        } else {
            //Log.i("ABS-table", "No data");
        }
    }
}