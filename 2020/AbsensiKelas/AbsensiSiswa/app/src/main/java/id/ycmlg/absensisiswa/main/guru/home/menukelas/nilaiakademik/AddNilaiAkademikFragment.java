package id.ycmlg.absensisiswa.main.guru.home.menukelas.nilaiakademik;

import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.LinearLayout;

import androidx.annotation.NonNull;
import androidx.fragment.app.Fragment;

import com.google.firebase.database.DataSnapshot;
import com.google.firebase.database.DatabaseError;
import com.google.firebase.database.DatabaseReference;
import com.google.firebase.database.FirebaseDatabase;
import com.google.firebase.database.ValueEventListener;

import java.util.Calendar;

import id.ycmlg.absensisiswa.R;
import id.ycmlg.absensisiswa.data.DaftarSiswaNilaiEditData;
import id.ycmlg.absensisiswa.data.SNTPClient;
import id.ycmlg.absensisiswa.databinding.FragmentAddNilaiAkademikBinding;

/**
 * A simple {@link Fragment} subclass.
 * Use the {@link AddNilaiAkademikFragment#newInstance} factory method to
 * create an instance of this fragment.
 */
public class AddNilaiAkademikFragment extends Fragment {

    // TODO: Rename parameter arguments, choose names that match
    // the fragment initialization parameters, e.g. ARG_ITEM_NUMBER
    private static final String ARG_PARAM1 = "namaKelas";
    private static final String ARG_PARAM2 = "mapel";
    private static final String ARG_PARAM3 = "mapelPath";
    private static final String ARG_PARAM4 = "subjectPath";

    // TODO: Rename and change types of parameters
    private String namaKelas;
    private String mapel;
    private String mapelPath;
    private String subject;
    private String year;
    private String nSubjectPath;

    public AddNilaiAkademikFragment() {
        // Required empty public constructor
    }

    /**
     * Use this factory method to create a new instance of
     * this fragment using the provided parameters.
     *
     * @param namaKelas Parameter 1.
     * @param mapel Parameter 2.
     * @param mapelPath Parameter 3.
     * @param subjectPath Parameter 4.
     * @return A new instance of fragment AddNilaiAkademikFragment.
     */
    // TODO: Rename and change types and number of parameters
    public static AddNilaiAkademikFragment newInstance(String namaKelas, String mapel, String mapelPath, String subjectPath) {
        AddNilaiAkademikFragment fragment = new AddNilaiAkademikFragment();
        Bundle args = new Bundle();
        args.putString(ARG_PARAM1, namaKelas);
        args.putString(ARG_PARAM2, mapel);
        args.putString(ARG_PARAM3, mapelPath);
        args.putString(ARG_PARAM4, subjectPath);
        fragment.setArguments(args);
        return fragment;
    }

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        database = FirebaseDatabase.getInstance();

        if (getArguments() != null) {
            namaKelas = getArguments().getString(ARG_PARAM1);
            mapel = getArguments().getString(ARG_PARAM2);
            mapelPath = getArguments().getString(ARG_PARAM3);
            if(getArguments().getString(ARG_PARAM4, null) != null){
                nSubjectPath = getArguments().getString(ARG_PARAM4, null);
                subjectPath = nSubjectPath.substring(0, nSubjectPath.indexOf("&"));
                subject = nSubjectPath.substring(nSubjectPath.indexOf("&") + 1, nSubjectPath.length());
                year = subject.substring(0, subject.indexOf("_"));
                subject = subject.substring(subject.indexOf("_") + 1, subject.length());
                subjectRef = database.getReference("nilaiakademik").child(mapelPath)
                        .child(namaKelas.replaceAll("\\s+","")
                                .trim()
                                .toLowerCase())
                        .child(subjectPath);
            } else{ subjectRef = null; }

        }
    }

    private String subjectPath;
    private FirebaseDatabase database;
    private static DatabaseReference subjectRef;
    private FragmentAddNilaiAkademikBinding addNilaiAkademikBinding;
    private View root;
    private String nis;
    private String namaLengkap;
    private String tahunAjaran;
    private String kelasSemester;
    private String tema;
    private String subTema;
    private String pembelajaran;
    private String jenisNilai;
    private String nilai;
    private String nomorNilaiAkademik;//subject
    private LinearLayout pb_ll_add_nilai_akad;
    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        // Inflate the layout for this fragment
        addNilaiAkademikBinding = FragmentAddNilaiAkademikBinding.inflate(inflater, container, false);
        root = addNilaiAkademikBinding.getRoot();
        pb_ll_add_nilai_akad = root.findViewById(R.id.pb_ll_add_nilai_akad);

        
        if(subjectPath != null){
            addNilaiAkademikBinding.nomorAddNilaiAkad.setVisibility(View.GONE);
            addNilaiAkademikBinding.titleNomorAddNilaiAkad.setVisibility(View.GONE);
        }
        
        addNilaiAkademikBinding.btSaveAddNilaiAkad.setOnClickListener(view -> {
            pb_ll_add_nilai_akad.setVisibility(View.VISIBLE);
            nis = addNilaiAkademikBinding.noIndukAddNilaiAkad.getText().toString();
            namaLengkap = addNilaiAkademikBinding.namaSiswaAddNilaiAkad.getText().toString();
            tahunAjaran = addNilaiAkademikBinding.tahunAjaranAddNilaiAkad.getText().toString();
            kelasSemester = addNilaiAkademikBinding.kelasSemesterAddNilaiAkad.getText().toString();
            tema = addNilaiAkademikBinding.temaAddNilaiAkad.getText().toString();
            subTema = addNilaiAkademikBinding.subTemaAddNilaiAkad.getText().toString();
            pembelajaran = addNilaiAkademikBinding.pembelajaranAddNilaiAkad.getText().toString();
            jenisNilai = addNilaiAkademikBinding.jenisNilaiAddNilaiAkad.getText().toString();
            nilai = addNilaiAkademikBinding.nilaiAddNilaiAkad.getText().toString();
            nomorNilaiAkademik = addNilaiAkademikBinding.nomorAddNilaiAkad.getText().toString();
            
            boolean formOK = false;
            
            if(nis != null && namaLengkap != null && tahunAjaran != null &&
                    kelasSemester != null && tema != null && subTema != null &&
                    pembelajaran != null && jenisNilai != null && nilai != null){
                formOK = nis.trim().length() > 0 && namaLengkap.length() > 0 && tahunAjaran.length() > 0 &&
                        kelasSemester.length() > 0 && tema.length() > 0 && subTema.length() > 0 &&
                        pembelajaran.length() > 0 && jenisNilai.length() > 0 && nilai.length() > 0;
            }
            
            if(formOK){
                if(subjectRef != null){
                    addNewNilai(true);
                } else if(subjectPath == null && nomorNilaiAkademik != null){
                    if(nomorNilaiAkademik.trim().length() > 0){
                        addNewNilai(false);
                    } else addNilaiAkademikBinding.nomorAddNilaiAkad.setError("Kosong!");
                    
                } else if(subjectPath == null && nomorNilaiAkademik == null) {
                    addNilaiAkademikBinding.nomorAddNilaiAkad.setError("Kosong!");
                }
            } else {
                if(nis == null) addNilaiAkademikBinding.noIndukAddNilaiAkad.setError("Kosong!");
                if(namaLengkap == null) addNilaiAkademikBinding.namaSiswaAddNilaiAkad.setError("Kosong!");
                if(tahunAjaran == null) addNilaiAkademikBinding.tahunAjaranAddNilaiAkad.setError("Kosong!");
                if(kelasSemester == null) addNilaiAkademikBinding.kelasSemesterAddNilaiAkad.setError("Kosong!");
                if(tema == null) addNilaiAkademikBinding.temaAddNilaiAkad.setError("Kosong!");
                if(subTema == null) addNilaiAkademikBinding.subTemaAddNilaiAkad.setError("Kosong!");
                if(pembelajaran == null) addNilaiAkademikBinding.pembelajaranAddNilaiAkad.setError("Kosong!");
                if(jenisNilai == null) addNilaiAkademikBinding.jenisNilaiAddNilaiAkad.setError("Kosong!");
                if(nilai == null) addNilaiAkademikBinding.nilaiAddNilaiAkad.setError("Kosong!");
                if(subjectPath == null) {
                    if (nomorNilaiAkademik == null) addNilaiAkademikBinding.nomorAddNilaiAkad.setError("Kosong!");
                }
            }
        });
        

        return root;
    }
    
    private void addNewNilai(boolean isSubjectPath){
        SNTPClient sntpClient = null;
        sntpClient.getDate(Calendar.getInstance().getTimeZone(), new SNTPClient.Listener() {
            @Override
            public void onTimeReceived(String rawDate) {
                final String tgl = rawDate.substring(0, rawDate.indexOf("T"));
                //final String wkt = rawDate.substring(rawDate.indexOf("T") + 1, rawDate.indexOf("+"));
                DaftarSiswaNilaiEditData newNilai = new DaftarSiswaNilaiEditData();
                newNilai.no = null;
                newNilai.created = tgl; //-
                newNilai.mapel = mapel; //-
                newNilai.jn = jenisNilai;
                newNilai.klssmt = kelasSemester;
                newNilai.n = nilai;
                newNilai.nis = nis;//
                newNilai.nm = namaLengkap;
                newNilai.pmb = pembelajaran;
                newNilai.st = subTema;
                if (isSubjectPath){
                    newNilai.created = year; //-
                    newNilai.sub = subject; //-
                } else {
                    newNilai.sub = nomorNilaiAkademik; //-
                    String nStr = nomorNilaiAkademik.replaceAll("/", "ss");
                    subjectPath = tgl + "_" + nStr.replaceAll("\\.", "t");
                    subjectRef = database.getReference("nilaiakademik").child(mapelPath)
                            .child(namaKelas.replaceAll("\\s+","")
                                    .trim()
                                    .toLowerCase())
                            .child(subjectPath);
                }
                newNilai.t = tema;
                newNilai.ta = tahunAjaran;

                /*Log.i("ADDNILAI", "nSubjectPath:" + nSubjectPath);
                Log.i("ADDNILAI", "subjectPath:" + subjectPath);
                Log.i("ADDNILAI", "subject:" + subject);
                Log.i("ADDNILAI", "subjectRef:" + subjectRef.getKey());*/

                subjectRef.addListenerForSingleValueEvent(new ValueEventListener() {
                    @Override
                    public void onDataChange(@NonNull DataSnapshot snapshot) {
                        if (snapshot.getValue() != null){
                            long arrTotal = snapshot.getChildrenCount();
                            subjectRef.child(String.valueOf(arrTotal)).setValue(newNilai);
                        } else {
                            subjectRef.child(String.valueOf(0)).setValue(newNilai);
                        }

                        addNilaiAkademikBinding.noIndukAddNilaiAkad.setText("");
                        addNilaiAkademikBinding.namaSiswaAddNilaiAkad.setText("");
                        addNilaiAkademikBinding.tahunAjaranAddNilaiAkad.setText("");
                        addNilaiAkademikBinding.kelasSemesterAddNilaiAkad.setText("");
                        addNilaiAkademikBinding.temaAddNilaiAkad.setText("");
                        addNilaiAkademikBinding.subTemaAddNilaiAkad.setText("");
                        addNilaiAkademikBinding.pembelajaranAddNilaiAkad.setText("");
                        addNilaiAkademikBinding.jenisNilaiAddNilaiAkad.setText("");
                        addNilaiAkademikBinding.nilaiAddNilaiAkad.setText("");
                        addNilaiAkademikBinding.nomorAddNilaiAkad.setText("");

                        pb_ll_add_nilai_akad.setVisibility(View.GONE);
                        requireActivity().onBackPressed();
                    }
                    @Override public void onCancelled(@NonNull DatabaseError error) {}
                });
            }

            @Override public void onError(Exception ex) {}
        });
    }
}