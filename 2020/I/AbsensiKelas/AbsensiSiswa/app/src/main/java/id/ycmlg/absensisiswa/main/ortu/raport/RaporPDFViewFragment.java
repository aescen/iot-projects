package id.ycmlg.absensisiswa.main.ortu.raport;

import android.app.ProgressDialog;
import android.content.ContentResolver;
import android.content.ContentValues;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.provider.MediaStore;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Toast;

import androidx.fragment.app.Fragment;

import com.github.barteksc.pdfviewer.PDFView;
import com.google.firebase.storage.FirebaseStorage;
import com.google.firebase.storage.StorageReference;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.util.Objects;

import id.ycmlg.absensisiswa.R;

/**
 * A simple {@link Fragment} subclass.
 * Use the {@link RaporPDFViewFragment#newInstance} factory method to
 * create an instance of this fragment.
 */
public class RaporPDFViewFragment extends Fragment {

    // TODO: Rename parameter arguments, choose names that match
    // the fragment initialization parameters, e.g. ARG_ITEM_NUMBER
    private static final String ARG_PARAM1 = "namaKelas";
    private static final String ARG_PARAM2 = "namaFile";

    // TODO: Rename and change types of parameters
    private String namaKelas;
    private String namaFile;

    public RaporPDFViewFragment() {
        // Required empty public constructor
    }

    /**
     * Use this factory method to create a new instance of
     * this fragment using the provided parameters.
     *
     * @param namaKelas Parameter 1.
     * @param namaFile Parameter 2.
     * @return A new instance of fragment RaporPDFViewFragment.
     */
    // TODO: Rename and change types and number of parameters
    public static RaporPDFViewFragment newInstance(String namaKelas, String namaFile) {
        RaporPDFViewFragment fragment = new RaporPDFViewFragment();
        Bundle args = new Bundle();
        args.putString(ARG_PARAM1, namaKelas);
        args.putString(ARG_PARAM2, namaFile);
        fragment.setArguments(args);
        return fragment;
    }

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        if (getArguments() != null) {
            namaKelas = getArguments().getString(ARG_PARAM1);
            namaFile = getArguments().getString(ARG_PARAM2);
            storage = FirebaseStorage.getInstance();
            storageRef = storage.getReference();
            raporRef = storageRef.child("rapor");
            fileRef = raporRef.child(namaKelas.toLowerCase().replaceAll("\\s+",""));
        }
    }

    private FirebaseStorage storage;
    private StorageReference storageRef;
    private StorageReference raporRef;
    private StorageReference fileRef;
    private View root;
    private PDFView pdfView;
    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        // Inflate the layout for this fragment
        root = inflater.inflate(R.layout.fragment_rapor_pdf_view, container, false);
        pdfView = (PDFView) root.findViewById(R.id.pdfViewContainer);
        final ProgressDialog progressDialog = new ProgressDialog(requireContext());
        progressDialog.setTitle("Loading");
        progressDialog.show();


        if (namaKelas != null) {
            OutputStream fos = null;
            File localFile = null;
            try {
                localFile = File.createTempFile(namaFile, "pdf");
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                    ContentResolver resolver = requireActivity().getContentResolver();
                    ContentValues contentValues = new ContentValues();
                    contentValues.put(MediaStore.MediaColumns.DISPLAY_NAME, namaFile);
                    contentValues.put(MediaStore.MediaColumns.MIME_TYPE, "application/pdf");
                    contentValues.put(MediaStore.MediaColumns.RELATIVE_PATH, Environment.DIRECTORY_DOWNLOADS);
                    Uri pdfUri = resolver.insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, contentValues);
                    fos = resolver.openOutputStream(Objects.requireNonNull(pdfUri));
                } else {
                    localFile = new File(Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS), namaFile);
                    fos = new FileOutputStream(localFile);
                }
            } catch (Exception e) {
                e.printStackTrace();
                Toast.makeText(requireContext(), namaFile + ": failed to create local file!", Toast.LENGTH_LONG).show();
                requireActivity().onBackPressed();
            }

            //Toast.makeText(requireContext(), fileRef.child(namaFile).getPath(), Toast.LENGTH_LONG).show();
            File finalLocalFile = localFile;
            OutputStream finalFos = fos;
            fileRef.child(namaFile).getFile(localFile).addOnSuccessListener(taskSnapshot -> {
                pdfView.fromFile(finalLocalFile)
                        .onRender( (nbPages, pageWidth, pageHeight)
                                -> progressDialog.dismiss() )
                        .load();
                try {
                    InputStream targetStream = new FileInputStream(finalLocalFile);
                    new Thread(() -> {
                        try {
                            byte[] buf = new byte[1024];
                            int l;
                            while((l=targetStream.read(buf))>0){
                                finalFos.write(buf,0, l);
                            }
                            finalFos.close();
                            targetStream.close();
                        } catch (IOException e) {
                            Toast.makeText(requireContext(), namaFile + ": failed to save!", Toast.LENGTH_LONG).show();
                            //Log.e("PDF", "file: ", e);
                            progressDialog.dismiss();
                            requireActivity().onBackPressed();
                        }
                    }).start();
                } catch (FileNotFoundException e) {
                    e.printStackTrace();
                }
            }).addOnFailureListener(exception -> {
                // Handle any errors
                Toast.makeText(requireContext(), namaFile + ": failed to load!", Toast.LENGTH_LONG).show();
                //Log.e("PDF", "file: ", exception);
                progressDialog.dismiss();
                requireActivity().onBackPressed();
            }).addOnProgressListener(snapshot -> {
                double progress = (100.0 * snapshot.getBytesTransferred()) / snapshot.getTotalByteCount();
                progressDialog.setMessage(((int) progress) + " %");
            });

        }
        return root;
    }
}