package id.ycmlg.absensisiswa.main.guru.history;

import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;

import androidx.annotation.NonNull;
import androidx.fragment.app.Fragment;
import androidx.viewpager2.widget.ViewPager2;

import com.google.android.material.tabs.TabLayout;
import com.google.android.material.tabs.TabLayoutMediator;

import id.ycmlg.absensisiswa.R;

public class HistoryGuruFragment extends Fragment {
    private static ViewPager2 view_pager_history_guru;
    private TabLayout tab_layout_history_guru;
    private View root;
    public final static int PENDING_POSITION = 0;
    public final static int TERKIRIM_POSITION = 1;

    public View onCreateView(@NonNull LayoutInflater inflater,
                             ViewGroup container, Bundle savedInstanceState) {
        root = inflater.inflate(R.layout.fragment_history_guru, container, false);
        tab_layout_history_guru = root.findViewById(R.id.tab_layout_history_guru);
        view_pager_history_guru = root.findViewById(R.id.view_pager_history_guru);

        view_pager_history_guru.setAdapter(new HistoryGuruViewPagerAdapter(requireActivity()));
        TabLayoutMediator tabLayoutMediator = new TabLayoutMediator(tab_layout_history_guru, view_pager_history_guru, (tab, position) -> {
            if (position == 0) {
                tab.setText("Pending");
            } else {
                tab.setText("Terkirim");
            }
        });
        tabLayoutMediator.attach();
        return root;
    }

    public static void setTabPosition(int position){
        view_pager_history_guru.setCurrentItem(position, true);
    }
}