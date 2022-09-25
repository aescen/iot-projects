package id.ycmlg.absensisiswa.main.guru.history;

import androidx.lifecycle.LiveData;
import androidx.lifecycle.MutableLiveData;
import androidx.lifecycle.ViewModel;

public class HistoryGuruViewModel extends ViewModel {

    private MutableLiveData<String> mText;

    public HistoryGuruViewModel() {
        mText = new MutableLiveData<>();
        mText.setValue("This is history fragment");
    }

    public LiveData<String> getText() {
        return mText;
    }
}