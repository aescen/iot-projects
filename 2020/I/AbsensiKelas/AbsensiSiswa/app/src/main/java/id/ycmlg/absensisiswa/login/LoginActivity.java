package id.ycmlg.absensisiswa.login;

import android.Manifest;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;

import androidx.appcompat.app.AppCompatActivity;
import androidx.constraintlayout.widget.ConstraintLayout;
import androidx.fragment.app.Fragment;
import androidx.fragment.app.FragmentContainerView;

import com.google.android.material.snackbar.Snackbar;
import com.karumi.dexter.Dexter;
import com.karumi.dexter.listener.multi.CompositeMultiplePermissionsListener;
import com.karumi.dexter.listener.multi.DialogOnAnyDeniedMultiplePermissionsListener;
import com.karumi.dexter.listener.multi.MultiplePermissionsListener;
import com.karumi.dexter.listener.multi.SnackbarOnAnyDeniedMultiplePermissionsListener;

import id.ycmlg.absensisiswa.R;
import id.ycmlg.absensisiswa.data.LocalUserService;

public class LoginActivity extends AppCompatActivity {
    private Button bt_guru = null;
    private Button bt_ortu = null;
    private Fragment fragment = null;
    private FragmentContainerView fcv = null;
    private ConstraintLayout cl = null;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        setTheme(R.style.AppTheme_NoActionBar);
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_login);
        View parentLayout = findViewById(android.R.id.content);

        MultiplePermissionsListener dialogMultiplePermissionsListener =
                DialogOnAnyDeniedMultiplePermissionsListener.Builder
                        .withContext(this)
                        .withTitle("Storage permission")
                        .withMessage("Storage permission are needed to continue")
                        .withButtonText(android.R.string.ok)
                        .withIcon(R.mipmap.ic_launcher_foreground)
                        .build();

        MultiplePermissionsListener snackbarMultiplePermissionsListener =
                SnackbarOnAnyDeniedMultiplePermissionsListener.Builder
                        .with(parentLayout, "Storage permission are needed to continue")
                        .withOpenSettingsButton("Settings")
                        .withCallback(new Snackbar.Callback() {
                            @Override
                            public void onShown(Snackbar snackbar) {
                                // Event handler for when the given Snackbar is visible
                            }
                            @Override
                            public void onDismissed(Snackbar snackbar, int event) {
                                // Event handler for when the given Snackbar has been dismissed
                            }
                        })
                        .build();

        MultiplePermissionsListener compositePermissionsListener = new CompositeMultiplePermissionsListener(snackbarMultiplePermissionsListener, dialogMultiplePermissionsListener);

        Dexter.withContext(this)
                .withPermissions(
                        Manifest.permission.NFC,
                        Manifest.permission.INTERNET,
                        Manifest.permission.ACCESS_WIFI_STATE,
                        Manifest.permission.WRITE_EXTERNAL_STORAGE,
                        Manifest.permission.READ_EXTERNAL_STORAGE
                ).withListener(compositePermissionsListener).onSameThread().check();

        //FirebaseDatabase.getInstance().setPersistenceEnabled(true);

        bt_guru = findViewById(R.id.bt_guru);
        bt_ortu = findViewById(R.id.bt_orang_tua);

        bt_guru.setClickable(true);
        bt_guru.setLongClickable(false);
        bt_ortu.setClickable(true);
        bt_ortu.setLongClickable(false);
        fcv = findViewById(R.id.fragment_container_login);
        cl = findViewById(R.id.cl_login_select);
        bt_guru.setOnClickListener(view -> {
            fragment = new LoginGuruFragment();
            getSupportFragmentManager()
                    .beginTransaction()
                    .replace(R.id.fragment_container_login, fragment)
                    .commit();

            cl.setVisibility(View.GONE);
            fcv.setVisibility(View.VISIBLE);
        });

        bt_ortu.setOnClickListener(view -> {
            fragment = new LoginOrtuFragment();
            getSupportFragmentManager()
                    .beginTransaction()
                    .replace(R.id.fragment_container_login, fragment)
                    .commit();
            cl.setVisibility(View.GONE);
            fcv.setVisibility(View.VISIBLE);
        });

    }

    @Override
    public void onBackPressed() {
        if (fragment != null) {
            cl.setVisibility(View.VISIBLE);
            fcv.setVisibility(View.GONE);
            fragment = null;
        } else {
            super.onBackPressed();
        }
    }

    @Override
    protected void onResume() {
        super.onResume();
        LocalUserService.appResumed();
    }

    @Override
    protected void onPause() {
        super.onPause();
        LocalUserService.appPaused();
    }
}