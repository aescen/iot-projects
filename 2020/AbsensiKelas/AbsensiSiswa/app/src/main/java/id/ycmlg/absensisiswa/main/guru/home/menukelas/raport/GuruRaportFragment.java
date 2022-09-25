package id.ycmlg.absensisiswa.main.guru.home.menukelas.raport;

import android.app.Activity;
import android.app.ProgressDialog;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.text.Editable;
import android.text.TextUtils;
import android.text.TextWatcher;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.EditText;
import android.widget.ImageButton;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.fragment.app.Fragment;

import com.github.barteksc.pdfviewer.PDFView;
import com.google.firebase.database.DataSnapshot;
import com.google.firebase.database.DatabaseError;
import com.google.firebase.database.DatabaseReference;
import com.google.firebase.database.FirebaseDatabase;
import com.google.firebase.database.ValueEventListener;
import com.google.firebase.storage.FirebaseStorage;
import com.google.firebase.storage.StorageMetadata;
import com.google.firebase.storage.StorageReference;

import java.io.BufferedReader;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.util.Calendar;

import id.ycmlg.absensisiswa.R;
import id.ycmlg.absensisiswa.data.PdfLoader;
import id.ycmlg.absensisiswa.data.Raport;
import id.ycmlg.absensisiswa.data.SNTPClient;
import id.ycmlg.absensisiswa.databinding.FragmentRaportGuruBinding;

/**
 * A simple {@link Fragment} subclass.
 * Use the {@link GuruRaportFragment#newInstance} factory method to
 * create an instance of this fragment.
 */
public class GuruRaportFragment extends Fragment {

    // TODO: Rename parameter arguments, choose names that match
    // the fragment initialization parameters, e.g. ARG_ITEM_NUMBER
    private static final String ARG_PARAM1 = "namaKelas";
    private static final String ARG_PARAM2 = "param2";

    // TODO: Rename and change types of parameters
    private static final int OPEN_REQUEST_CODE = 4041;
    private static final String TYPE_PDF = "application/pdf";
    private String namaKelas;
    private String mParam2;
    private String nis;
    private String namaLengkap;

    public GuruRaportFragment() {
        // Required empty public constructor
    }

    /**
     * Use this factory method to create a new instance of
     * this fragment using the provided parameters.
     *
     * @param namaKelas Parameter 1.
     * @param param2 Parameter 2.
     * @return A new instance of fragment RaportFragment.
     */
    // TODO: Rename and change types and number of parameters
    public static GuruRaportFragment newInstance(String namaKelas, String param2) {
        GuruRaportFragment fragment = new GuruRaportFragment();
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
            dsRef = database.getReference("ds").child(namaKelas.toLowerCase().replaceAll("\\s+",""));
            lapRaportRef = database.getReference("laporanrapor").child(namaKelas.toLowerCase().replaceAll("\\s+",""));
            storage = FirebaseStorage.getInstance();
            raportStorRef = storage.getReference().child("rapor").child(namaKelas.toLowerCase().replaceAll("\\s+",""));
        }
    }

    private View root;
    private FragmentRaportGuruBinding guruRaportBinding;
    private FirebaseDatabase database = null;
    private DatabaseReference dsRef = null;
    private DatabaseReference lapRaportRef = null;
    private FirebaseStorage storage;
    private StorageReference raportStorRef;
    private EditText ed_no_induk_raport_guru;
    private TextView tv_nama_lengkap_raport_guru;
    private ImageButton ib_add_raport_guru;
    private ImageButton ib_send_raport_guru;
    private EditText ed_upload_file_raport_guru;
    private PDFView pdfview_raport_guru = null;
    private static PdfLoader pdfLoader = new PdfLoader();
    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        // Inflate the layout for this fragment
        root = inflater.inflate(R.layout.fragment_raport_guru, container, false);
        guruRaportBinding = FragmentRaportGuruBinding.inflate(inflater, container, false);
        root = guruRaportBinding.getRoot();
        ed_no_induk_raport_guru = guruRaportBinding.edNoIndukRaportGuru;
        tv_nama_lengkap_raport_guru = guruRaportBinding.tvNamaLengkapRaportGuru;
        ed_upload_file_raport_guru = guruRaportBinding.edUploadFileRaportGuru;
        ib_add_raport_guru = guruRaportBinding.ibAddRaportGuru;
        ib_send_raport_guru =  guruRaportBinding.ibSendRaportGuru;
        pdfview_raport_guru = (PDFView) guruRaportBinding.pdfviewRaportGuru;

        ib_send_raport_guru.setOnClickListener(view -> {
            if(ed_no_induk_raport_guru.getText().toString().trim().length() == 0) ed_no_induk_raport_guru.setError("NIS kosong!");
            if(pdfview_raport_guru == null) ed_upload_file_raport_guru.setError("File kosong!");
        });

        ed_no_induk_raport_guru.addTextChangedListener(new TextWatcher() {
            @Override public void beforeTextChanged(CharSequence charSequence, int i, int i1, int i2) {}
            @Override public void onTextChanged(CharSequence charSequence, int i, int i1, int i2) {}
            @Override
            public void afterTextChanged(Editable editable) {
                nis = ed_no_induk_raport_guru.getText().toString().trim();
                if(nis.length() > 3 && TextUtils.isDigitsOnly(nis)){
                    SNTPClient sntpClient = null;
                    SNTPClient.getDate(Calendar.getInstance().getTimeZone(), new SNTPClient.Listener() {
                        @Override
                        public void onTimeReceived(String rawDate) {
                            final String tgl = rawDate.substring(0, rawDate.indexOf("T"));
                            final String wkt = rawDate.substring(rawDate.indexOf("T") + 1, rawDate.indexOf("+"));
                            dsRef.addListenerForSingleValueEvent(new ValueEventListener() {
                                @Override
                                public void onDataChange(@NonNull DataSnapshot snapshot) {
                                    boolean userFound = false;
                                    for (DataSnapshot userChild: snapshot.getChildren()) {
                                        if(nis.contentEquals(userChild.getKey())){
                                            namaLengkap = userChild.child("nama").getValue().toString();
                                            userFound = true;
                                            break;
                                        }
                                    }
                                    if(userFound){
                                        //final LinearLayout pb_ll_raport_guru = root.findViewById(R.id.pb_ll_raport_guru);
                                        tv_nama_lengkap_raport_guru.setText(namaLengkap);

                                        View.OnClickListener addPdfListener = view -> {
                                            ib_add_raport_guru.setVisibility(View.GONE);
                                            //pb_ll_raport_guru.setVisibility(View.VISIBLE);
                                            openFile(TYPE_PDF);
                                            ib_add_raport_guru.setOnClickListener(null);
                                            PdfLoader.getPdf(new PdfLoader.Listener() {
                                                @Override
                                                public void onPdfLoaded(byte[] inputBytes) {
                                                    requireActivity().runOnUiThread(() -> {
                                                        //pb_ll_raport_guru.setVisibility(View.GONE);
                                                        //pdfview_raport_guru.setBackground(null);
                                                        pdfview_raport_guru.fromBytes(inputBytes).defaultPage(0)
                                                                .pages(0)
                                                                .enableSwipe(false)
                                                                .onTap(e -> true)
                                                                .enableDoubletap(false).load();
                                                        ib_send_raport_guru.setVisibility(View.VISIBLE);
                                                        pdfview_raport_guru.setVisibility(View.VISIBLE);
                                                        ed_upload_file_raport_guru.setVisibility(View.GONE);
                                                        //pb_ll_raport_guru.setVisibility(View.GONE);
                                                        ib_send_raport_guru.setOnClickListener(null);
                                                        ib_send_raport_guru.setOnClickListener(view1 -> {
                                                            //pb_ll_raport_guru.setVisibility(View.VISIBLE);
                                                            StorageMetadata meta = new StorageMetadata.Builder().setContentType(TYPE_PDF).build();
                                                            final String nf = nis + "_" + tgl + "_" + wkt.replace(":", "-") + ".pdf";
                                                            final ProgressDialog progressDialog = new ProgressDialog(requireContext());
                                                            progressDialog.setTitle("Uploading");
                                                            progressDialog.show();
                                                            raportStorRef.child(nf).putBytes(inputBytes, meta)
                                                                    .addOnSuccessListener(taskSnapshot -> {
                                                                        Raport newRaport = new Raport();
                                                                        newRaport.ket = "Valid";
                                                                        newRaport.nf = nf;
                                                                        newRaport.nis = nis;
                                                                        newRaport.nm = namaLengkap;
                                                                        newRaport.tgl = tgl;
                                                                        newRaport.wkt = wkt;
                                                                        lapRaportRef.addListenerForSingleValueEvent(new ValueEventListener() {
                                                                            @Override
                                                                            public void onDataChange(@NonNull DataSnapshot snapshot) {
                                                                                if (snapshot.getValue() != null) {
                                                                                    long arrTotal = snapshot.getChildrenCount();
                                                                                    lapRaportRef.child(String.valueOf(arrTotal)).setValue(newRaport);
                                                                                } else {
                                                                                    lapRaportRef.child(String.valueOf(0)).setValue(newRaport);
                                                                                }
                                                                                ed_no_induk_raport_guru.setText("");
                                                                                pdfview_raport_guru.setVisibility(View.GONE);
                                                                                ed_upload_file_raport_guru.setVisibility(View.VISIBLE);
                                                                                Toast.makeText(requireContext(),
                                                                                        "File tersimpan.",
                                                                                        Toast.LENGTH_LONG).show();
                                                                                //pb_ll_raport_guru.setVisibility(View.GONE);
                                                                                Fragment fragment = GuruRaportFragment.newInstance(namaKelas, null);
                                                                                fragment.setRetainInstance(true);
                                                                                requireActivity().getSupportFragmentManager()
                                                                                        .beginTransaction()
                                                                                        .replace(R.id.nav_kelas_host_fragment, fragment)
                                                                                        .commit();
                                                                                ((AppCompatActivity)requireActivity()).getSupportActionBar().setTitle("Raport");
                                                                            }

                                                                            @Override public void onCancelled(@NonNull DatabaseError error) {}
                                                                        });
                                                                    }).addOnFailureListener(fail -> { 
                                                                        pdfview_raport_guru.setVisibility(View.GONE);
                                                                        ed_upload_file_raport_guru.setVisibility(View.VISIBLE);
                                                                        Toast.makeText(requireContext(), 
                                                                                "File gagal disimpan!", 
                                                                                Toast.LENGTH_LONG).show();
                                                                        //pb_ll_raport_guru.setVisibility(View.GONE); 
                                                                    }).addOnProgressListener(snapshot1 -> {
                                                                        double progress = (100.0 * snapshot1.getBytesTransferred()) / snapshot1.getTotalByteCount();
                                                                        progressDialog.setMessage("Uploaded " + ((int) progress) + "%...");
                                                                    });
                                                        });
                                                    });

                                                }

                                                @Override
                                                public void onError(Exception ex) {
                                                    pdfview_raport_guru.setVisibility(View.GONE);
                                                    ed_upload_file_raport_guru.setVisibility(View.VISIBLE);
                                                    Toast.makeText(requireContext(), "File gagal dimuat!", Toast.LENGTH_LONG).show();
                                                    //pb_ll_raport_guru.setVisibility(View.GONE);
                                                }
                                            });
                                        };

                                        ib_add_raport_guru.setOnClickListener(addPdfListener);
                                        ed_upload_file_raport_guru.setOnClickListener(addPdfListener);
                                    } else {
                                        ed_no_induk_raport_guru.setError("NIS tidak ada!");
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
                } else if(nis.trim().length() > 0 && nis.trim().length() <= 3){
                    ed_no_induk_raport_guru.setError("NIS tidak ada!");
                }
            }
        });
        return root;
    }

    public void openFile(final String intentType) {
        Intent intent = new Intent(Intent.ACTION_OPEN_DOCUMENT);
        intent.addCategory(Intent.CATEGORY_OPENABLE);
        intent.setType(intentType);
        startActivityForResult(intent, OPEN_REQUEST_CODE);
    }

    @Override
    public void onActivityResult(int requestCode, int resultCode, Intent resultData) {
        Uri currentUri = null;
        if (resultCode == Activity.RESULT_OK) {
            if (requestCode == OPEN_REQUEST_CODE) {
                if (resultData != null) {
                    currentUri = resultData.getData();
                    try {
                        if (currentUri != null) {
                            pdfLoader.setPdfFile(getBytes(requireActivity().getContentResolver().openInputStream(currentUri)));
                            //final String content = readFileContent(currentUri);
                            //textView.setText(content);
                        } else {
                            pdfLoader.setEx(new NullPointerException());
                        }
                    } catch (IOException e) {
                        // Handle error here
                    }
                }
            }
        }
    }

    private String readFileContent(Uri uri) throws IOException {
        InputStream inputStream = requireActivity().getContentResolver().openInputStream(uri);
        BufferedReader reader = new BufferedReader(new InputStreamReader(inputStream));
        StringBuilder stringBuilder = new StringBuilder();
        String currentline;
        while ((currentline = reader.readLine()) != null) {
            stringBuilder.append(currentline + "\n");
        }
        inputStream.close();
        return stringBuilder.toString();
    }

    public byte[] getBytes(InputStream inputStream) throws IOException {
        ByteArrayOutputStream byteBuffer = new ByteArrayOutputStream();
        int bufferSize = 1024;
        byte[] buffer = new byte[bufferSize];
        int len = 0;
        while ((len = inputStream.read(buffer)) != -1) {
            byteBuffer.write(buffer, 0, len);
        }
        return byteBuffer.toByteArray();
    }
}

