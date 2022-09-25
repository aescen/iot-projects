package id.ycmlg.absensisiswa.data;

public class PdfLoader {
    public PdfLoader() {}

    public interface Listener {
        void onPdfLoaded(byte[] inputBytes);
        void onError(Exception ex);
    }

    // callback listener
    public Listener listener;

    /**
     * @param listener callback listener after time received.
     */
    public PdfLoader(Listener listener) {
        this.listener = listener;
    }

    public void setPdfFile(byte[] pdfBytes) { LoadedPdfBytes = pdfBytes; }

    public void setEx(Exception e) {
        ex = e;
    }

    public static byte[] LoadedPdfBytes = null;
    public static Exception ex = null;
    public static void getPdf(Listener _listener){
        new Thread(() -> {
            while (true) {
                PdfLoader pdfLoader = new PdfLoader(_listener);
                if (LoadedPdfBytes != null) {
                    pdfLoader.listener.onPdfLoaded(LoadedPdfBytes);
                    break;
                } else if (ex != null) {
                    pdfLoader.listener.onError(ex);
                    break;
                }
            }
        }).start();
    }
}
